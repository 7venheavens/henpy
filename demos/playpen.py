from henpy import searchers
from henpy.utilities.tagtools import SQLTagManager
from henpy.misc import cached_pages_dir
import logging

logging.getLogger().setLevel(logging.DEBUG)
logging.getLogger("chardet.charsetprober").setLevel(logging.INFO)

# tm = TagManager.from_file("data/tagdata.tsv")
tm = SQLTagManager("sqlite://")
s = searchers.JavlibrarySearcher(debug=cached_pages_dir)

a = s.search("LOVE-049", return_multi=True)
print(a[0].tags)
print(a)
for i in a:
    print(i, i.tags)

a = s.search("LOVE-001", return_multi=True, topn=4, guess_with_code=False)
print(a)
for i in a:
    print(i)