from henpy.searchers import searchers
from henpy.utilities.tagtools import TagManager


# tm = TagManager.from_file("data/tagdata.tsv")
tm = TagManager()
s = searchers.JavlibrarySearcher(tm)

a = s.search("LOVE-049", return_multi=True)
print(a[0].tags)
print(a)
for i in a:
    print(i)

a = s.search("LOVE-001", return_multi=True)
for i in a:
    print(i)