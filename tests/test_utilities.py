import pytest
import requests
import os

from henpy import misc
from henpy.utilities import extract_categories as ec



@pytest.fixture
def cached_pages():
    with open(os.path.join(misc.cached_pages_dir, "javlibrary_category_jp.html")) as f:
        jcat_html = f.read()
    jcat_resp = requests.Response()
    jcat_resp._content = str.encode(jact_html, encoding="utf-8")
    jcat_resp.url = "http://www.javlibrary.com/ja/genres.php"
    jcat_resp.status_code = 200
    return (jcat_resp, )


def test_extract_categories(cached_pages):
    jp_cats = utilities.get_categories(cached_pages[0])


