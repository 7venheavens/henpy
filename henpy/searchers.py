import re
import requests
import cfscrape
import logging
import os

from abc import ABC, abstractmethod
from functools import lru_cache

from henpy.models import Tag, TagData, VideoMetadata
from henpy.dummy import DummySession


logger = logging.getLogger(__name__)


class SiteSearcher(ABC):
    """Dummy prototype for generic API for data retrieval from a specific site
    """

    def __init__(self):
        """General init method
        @args
        """
        pass

    @abstractmethod
    def search(self, code, topn=10):
        """Queries the remote site with a given code and acquires the metadata for the query.

        @args
            code (str): Unicode encoded string containing video code to query with
            topn (int): Number of entries to return given a multiple-match scenario
        @returns
            Iterable QuerySet object containing multiple VideoMetadata objects
        """
        pass


class JavlibrarySearcher(SiteSearcher):
    def __init__(self, normalizer=None, debug=False):
        """
        @args
            normalizer (Normalizer file to use, if any, to normalize tag names)
            debug (bool / string): if None or False, run as per normal. Expects a path to a folder
                                   containing html files keyed by id containing dumps. This is to improve
                                   testing and debugging
        """
        super().__init__()
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

        # Debug enablers
        self.debug = debug
        if self.debug:
            assert(os.path.exists(debug))
            self.s = DummySession(debug)
        else:
            # Session initialization
            session = requests.Session()
            logging.info("Creating Cloudflare scraper")
            self.s = cfscrape.create_scraper(sess=session)
            logging.info("Finished creating Cloudflare scraper")

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
        resp = self.s.get(site)
        resp.raise_for_status()
        return resp

    def _normalize_search(self, code, resp, guess_with_code=True):
        """Handles the raw search result. Correcting for missing / duplicate entries
        @args
            code (str): Code of the video
            resp: response object to process for information
            guess_with_code (bool): If True, uses exact matches to the code to filter out
                                    the targets.
        @returns
            response object or list of (url, code, image_url) tuples
            if only one entry is present, response is provided
            if no results found (empty seach), empty list provided
            if multimatch (url, code, image_url provided)
        """
        resp.raise_for_status()
        lang = self.langs[0]
        if resp.url.startswith(self.fail_path.format(lang)):
            logger.debug(f"Multiple hit found for code={code}. path={resp.url}")
            # multi re returns a list of (suffix, code, image_url) tuples
            multi = self.multi_results_re.findall(resp.text)
            logging.debug(f"Multi_results: {multi}")
            # Check if the database contains multiple results
            if multi:
                # if no entires found on page, return empty list
                if len(multi) == 0:
                    return []
                # Try to guess which one is the code we want (exact match)
                if guess_with_code:
                    options = [suffix for suffix, icode, image_url in multi if icode == code]
                else:
                    options = [suffix for suffix, icode, image_url in multi]
                # In the case of an exact match, return the match
                if len(options) == 1:
                    resp = self.s.get(self.access_path.format(lang=lang,
                                                              suffix=options[0]))
                else:
                    return [(self.access_path.format(lang="{lang}",
                                                     suffix=suffix),
                             icode,
                             image_url) for suffix, icode, image_url in multi]

        return resp

    def _extract_metadata(self, text):
        """Extracts the relevant metadata from a given request
        @args
            text (str): Raw html for a given
        @returns
            dictionary containing the raw metadata in the following structure
        """
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
        # We'll figure out how to handle the multimatches later
        if isinstance(search_data, list):
            logging.debug(search_data)
            raise NotImplementedError("Multiple match input not yet handled")
        # If it's gotten this far, we know the search_data is a http response
        resp = search_data
        for num, lang in enumerate(self.langs):
            metadata = self._extract_metadata(resp.text)
            # Initialize the result object using the first language
            if num == 0:
                # Create the taglist for the video
                tags = [tag for tag in metadata["tags"]]
                stars = [star for star in metadata["stars"]]
                res = VideoMetadata(metadata["code"], metadata["release_date"], tags,
                                    metadata["director"], metadata["maker"], metadata["label"],
                                    metadata["image_url"], stars)

            # If we're looking at not the first language, we'll need to pull the data.
            # We do it here to reduce query count, since this bit is slow
            if num != 0:
                resp = self.s.get(resp.url.replace(".com/en/", f".com/{lang}/"))
                metadata = self._extract_metadata(resp.text)

            res.title[lang] = metadata["title"]
        return res

    def process_pages(self, search_data, topn=10):
        """
        @args
            search_data (tuple (url, code, image_url))
        @returns

        """
        search_data = search_data[:topn]
        res = []
        lang = self.langs[0]
        for url, code, image_url in search_data:
            logger.debug(f"Processing url={url} with code={code}")
            resp = self.s.get(url.format(lang=lang))
            video = self._process_page(resp)
            logger.debug(f"video={video}")
            res.append(video)

        return res

    @lru_cache(maxsize=128)
    def search(self, code, topn=5, return_multi=False, **kwargs):
        """Flow is as follows: Seach using english -> Identify pages/candidate pages
        -> For top N pages, extract information for each language (Currently implement using multiple queries)
        @ args
            code (string):
            topn (int): Top n results to use to query if any
            return_multi (bool): Should search return multiple entries. If true, returns all entries
                                 as a list regardless of the length
        @ returns
            FIGURE THIS ONE OUT
        """
        resp = self._search_code(code)
        search_data = self._normalize_search(code, resp, **kwargs)
        logging.debug(f"search_data: {search_data}")
        if not isinstance(search_data, list):
            res = self._process_page(search_data)
            logging.debug(f"Search result: {res}")
        else:
            logging.debug("Multiple search targets found: {search_data}")
            if return_multi:
                res = self.process_pages(search_data, topn=topn)
            else:
                logging.info(f"Multiple matches found for code={code}")
                res = None
        # Quick hack to return a list if necessary
        if return_multi and not isinstance(res, list):
            return [res]
        return res
