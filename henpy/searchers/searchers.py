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
        # Captures the following groups: link appending for the entry and the entry-code
        self.multi_results_re = re.compile(r"""f="\.(.*)" title*.*<div class="id">([\w-]*)<""")

        # image_path regex
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

    def _search_code(self, code, lang):
        """Performs a search of the code against the selected web database with specified language
        @args:
            code: string. Code to search
        @returns
            request object if successful, raises if status
        """
        site = self.search_path.format(lang=lang, code=code)
        req = self.s.get(site)
        req.raise_for_status()
        return req

    def _normalize_search(self, code, req, lang):
        """Handles the raw search result. Correcting for missing / duplicate entries
        @args
            req: request object to process for information
        @returns
            Single request object containing the database page for the code OR
            the selected page in the case of multiple entries
            raises if not found
        """
        req.raise_for_status()
        if req.url.startswith(self.fail_path.format(lang)):
            # multi re returns a list of (path, code) tuples
            multi = self.multi_results_re.findall(req.text)
            # Check if the database contains multiple results
            if multi:
                # Try to guess which one is the code we want (exact match)
                # try an exact match
                # logging.debug("Performing Multiple search for ")
                options = [suffix for suffix, icode in multi if icode == code]
                # In the case of an exact match, return the match
                if len(options) == 1:
                    req = self.s.get(self.access_path.format(lang=lang,
                                                             suffix=options[0]))
                # Else return all the matches (currently raises error)
                else:
                    raise errors.SearchMultipleResults
        return req

    def _extract_metadata(self, req, lang):
        """Extracts the relevant metadata from a given request
        @args
        @returns
            dictionary containing the raw metadata in the following structure
        """
        text = req.text

        title = self._unpack_search(self.title_re.search(text))
        star = self.star_re.findall(text)
        genre = self.genre_re.findall(text)
        maker = self._unpack_search(self.maker_re.search(text))
        label = self._unpack_search(self.label_re.search(text))
        director = self._unpack_search(self.director_re.search(text))
        release_date = self._unpack_search(self.release_date_re.search(text))
        code = self._unpack_search(self.code_re.search(text))
        image_path = self._unpack_search(self.image_re.search(text))

        # Create the tags from the genre and star fields
        tags = [TagData("star", star_name, lang) for star_name in star] + [TagData("genre", genre_name, lang) for genre_name in genre]
        return {"title": title,
                "code": code,
                "tags": tags,
                "maker": maker,
                "label": label,
                "director": director,
                "release_date": release_date,
                "image_path": image_path}

    def search(self, code, topn=10):
        for num, lang in enumerate(self.langs):
            req = self._search_code(code, lang)
            req = self._normalize_search(code, req, lang)
            metadata = self._extract_metadata(req, lang)
            if num == 0:
                res = VideoMetadata(metadata["code"], metadata["release_date"], metadata["tags"],
                                    metadata["directpr"], metadata["maker"], metadata["label"],
                                    metadata["image_path"])
            res.title[lang] = metadata["title"]
        return res