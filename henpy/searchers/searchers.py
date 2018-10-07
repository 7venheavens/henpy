import re
import requests
import cfscrape
from abc import ABC, abstractmethod
from henpy.models import Tag, TagData, VideoMetadata


class SiteSearcher(ABC):
    """Dummpy prototype for generic API for data retrieval from a specific site
    """

    def __init__(self, tag_manager):
        """General init method
        """
        self.tm = tag_manager

    @abstractmethod
    def search(self, code, topn=10):
        """Queries the remote site with a given code and acquires the metadata for the query.

        @args
            code (str): Unicode encoded string containing video code to quey with
            topn (int): Number of entries to return given a multiple-match scenario
        @returns
            Iterable QuerySet object containing multiple VideoMetadata objects
        """
        pass


class JavlibrarySearcher(SiteSearcher):
    def __init__(self, tag_manager):
        super().__init__(tag_manager)
        self.search_path = "http://www.javlibrary.com/{lang}/vl_searchbyid.php?keyword={code}"
        # Where it ends up if it fails (0 or >1 entries)
        self.fail_path = "http://www.javlibrary.com/{0}/vl_search"
        # Path template to do a direct access to a specifc entry
        self.access_path = "http://www.javlibrary.com/{lang}{suffix}"
        self.langs = ["en", "ja"]

        # Regexes for the acquisiton of metadata
        self.star_re = re.compile(r'vl\_star\.php\?s\=[a-z0-9]{1,10}" rel="tag">(.{1,20})</a>')
        self.genre_re = re.compile(r'vl\_genre\.php\?g=[a-z0-9]+" rel="category tag">(.{1,20})</a>')
        self.director_re = re.compile(r'vl\_director\.php\?d=[a-z0-9]+" rel="tag">(.{1,20})</a>')
        self.maker_re = re.compile(r'vl\_maker\.php\?m=[a-z0-9]+"\srel="tag">(.{1,20})</a>')
        self.label_re = re.compile(r'vl\_label\.php\?l=[a-z0-9]+"\srel="tag">(.{1,20})</a>')
        self.title_re = re.compile(r'<meta property="og:title" content=".*? (.*) - JAVLibrary" \/>')
        self.release_date_re = re.compile(r'video_date.*\n.*\n.*\n.*\n.*"text">(.*)<\/td>', re.MULTILINE)
        self.image_re = re.compile(r'video_jacket_img" src="(.*\.jpg)" ')
        self.code_re = re.compile(r'ID:<\/td>\s+<td class="text">([\w-]+)<\/td>', re.MULTILINE)
        # regex for capturing multiple search entries
        # Captures the following groups: link appending for the entry (suffix), entry-code and image_url.
        # Suffix contains the preceeding forward slash
        self.multi_results_re = re.compile(r"""f="\.(.*)" title*.*<div class="id">([\w-]*)<\/div><img src="(\/\/[\w+\.\/]+)""")

        # image_url regex
        self.image_re = re.compile(r'video_jacket_img" src="(\/\/[\w+\.\/]+)"')

        # Session initialization
        session = requests.Session()
        self.s = cfscrape.create_scraper(sess=session)

    def _unpack_search(self, obj):
        """Unpacks a re.search object, return "" if obj is none
        """
        if not obj:
            return ""
        return obj.group(1)

    def _search_code(self, code, lang=None):
        """Performs a search of the code against the selected web database with specified language
        @args:
            code: string. Code to search
            lang (): Default None -> first language in self.langs
        @returns
            request object if successful, raises if status
        """
        if lang is None:
            lang = self.langs[0]
        site = self.search_path.format(lang=lang, code=code)
        req = self.s.get(site)
        req.raise_for_status()
        return req

    def _normalize_search(self, code, req):
        """Handles the raw search result. Correcting for missing / duplicate entries
        @args
            req: request object to process for information
        @returns
            response containing the single page if only one entry is present,
            or an iterable of all page_paths if multiple matching detected
        """
        req.raise_for_status()
        lang = self.langs[0]
        if req.url.startswith(self.fail_path.format(lang)):
            # multi re returns a list of (path, code) tuples
            multi = self.multi_results_re.findall(req.text)
            # Check if the database contains multiple results
            if multi:
                if len(multi) == 0:
                    return
                # Try to guess which one is the code we want (exact match)
                options = [suffix for suffix, icode, image_url in multi if icode == code]
                # In the case of an exact match, return the match
                if len(options) == 1:
                    req = self.s.get(self.access_path.format(lang=lang,
                                                             suffix=options[0]))
                else:
                    return [(self.access_path.format(lang="{lang}",
                                                     suffix=suffix),
                             icode,
                             image_url) for suffix, icode, image_url in multi]

        return req

    def _extract_metadata(self, resp):
        """Extracts the relevant metadata from a given request
        @args
        @returns
            dictionary containing the raw metadata in the following structure
        """
        text = resp.text

        title = self._unpack_search(self.title_re.search(text))
        star = self.star_re.findall(text)
        genre = self.genre_re.findall(text)
        maker = self._unpack_search(self.maker_re.search(text))
        label = self._unpack_search(self.label_re.search(text))
        director = self._unpack_search(self.director_re.search(text))
        release_date = self._unpack_search(self.release_date_re.search(text))
        code = self._unpack_search(self.code_re.search(text))
        image_url = self._unpack_search(self.image_re.search(text))

        # Create the tags from the genre and star fields
        tags = [genre_name for genre_name in genre]
        stars = [star_name for star_name in star]
        return {"title": title,
                "code": code,
                "tags": tags,
                "stars": stars,
                "maker": maker,
                "label": label,
                "director": director,
                "release_date": release_date,
                "image_url": image_url}

    def _process_page(self, search_data):
        """Handles the processing of a single page from normalize_search. Maybe raise and catch if multiple
        @args
            search data (response or list): . If list, hands over to process_pages
        """
        if isinstance(search_data, list):
            raise TypeError("Iterable input when singular expected")
        # If it's gotten this far, we know the search_data is a http response
        resp = search_data
        for num, lang in enumerate(self.langs):
            metadata = self._extract_metadata(resp)
            # Initialize the result object using the first language
            if num == 0:
                # Create the taglist for the video
                tags = [self.tm[tag] for tag in metadata["tags"]]
                stars = [self.tm.get_or_create(star, "star") for star in metadata["stars"]]
                tags += stars
                res = VideoMetadata(metadata["code"], metadata["release_date"], tags,
                                    metadata["director"], metadata["maker"], metadata["label"],
                                    metadata["image_url"])

            # If we're looking at not the first language, we'll need to pull the data.
            # We do it here to requnce query count, since this bit is slow
            if num != 0:
                resp = self.s.get(resp.url.replace(".com/en/", f".com/{lang}/"))
                metadata = self._extract_metadata(resp)

            res.title[lang] = metadata["title"]
        return res

    def process_pages(self, search_data, topn=10):
        targets = None

    def search(self, code, topn=5, return_multi=False):
        """Flow is as follows: Seach using english -> Identify pages/candidate pages
        -> For top N pages, extract information for each language (Currently implement using multiple queries)
        @ args
            code
            topn
            return_multi
        @ returns
            FIGURE THIS ONE OUT
        """
        resp = self._search_code(code)
        search_data = self._normalize_search(code, resp)
        try:
            res = self._process_page(search_data)
        except TypeError:
            if return_multi:
                res = self._process_pages(search_data, topn)
            else:
                res = None
        return res
