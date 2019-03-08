import requests
import os
import yaml
import re
import logging


logger = logging.getLogger(__name__)


class DummySession:
    def __init__(self, cached_pages_dir):
        self.cache_dir = cached_pages_dir
        self.path_regex = r"""http://www.javlibrary.com/(ja|en)(/)"""
        self.url_map = self._build_url_map(self.cache_dir)

    def _clean_metadata(self, md):
        md["url"] = md["url"].lower()
        return

    def _build_url_map(self, cache_dir):
        metadata = [i for i in os.listdir(cache_dir) if i.endswith('.yaml')]
        metadata_paths = [os.path.join(cache_dir, i) for i in metadata]
        res = {}
        for metadatum_path in metadata_paths:
            with open(metadatum_path,
                      encoding="utf-8") as f:
                metadata = yaml.load(f)
            if "html_suffix" in metadata:
                html_path = os.path.join(self.cache_dir, metadata["html_suffix"])
            else:
                html_path = os.path.splitext(metadatum_path)[0] + ".html"
            metadata["html"] = html_path
            try:
                assert(os.path.exists(html_path))
            except AssertionError:
                logging.error(f"Path: {html_path} does not exist")
            self._clean_metadata(metadata)
            res[metadata["url"]] = metadata
        return res

    def get(self, url):
        resp = requests.Response()
        url = url.lower()
        metadata = self.url_map[url]
        with open(metadata["html"],
                  encoding="utf-8") as f:
            html_text = f.read()
        resp._content = str.encode(html_text, encoding="utf-8")
        resp.url = metadata["url"]
        resp.status_code = 200
        return resp


    def _get_cached_search(self, code, lang):
        """Creates a response object instead of querying data from the site (speed up tests)
        @args
            code (str): to search for
        @returns
            response object
        """
        resp = requests.Response()
        with open(os.path.join(self.cache_dir, f"javlibrary_{code}_{lang}.html"),
                  encoding="utf-8") as f:
            text = f.read()

        with open(os.path.join(self.cache_dir, f"javlibrary_{code}_{lang}.yaml"),
                  encoding="utf-8") as f:
            metadata = yaml.load(f)
        resp._content = str.encode(text, encoding="utf-8")
        resp.url = metadata["url"]
        resp.status_code = 200
        return resp
