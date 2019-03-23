class dotdict(dict):
    """dot.notation access to dictionary attributes"""
    __getattr__ = dict.get
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


if __name__ == "__main__":
    idx = dotdict(**{"code": 0,
                     "stars": 1,
                     "tags": 2,
                     "maker": 3,
                     "publisher": 4,
                     "path": 5})

    assert(idx.code == 0)


def title_case(word):
    return word[0].upper() + word[1:].lower()
