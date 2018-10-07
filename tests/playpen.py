from henpy.searchers import searchers

s = searchers.JavlibrarySearcher()

a = s.search("LOVE-049")
for i in a:
    print(i)

a = s.search("LOVE-001")
for i in a:
    print(i)