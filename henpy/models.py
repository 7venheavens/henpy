"""
General use models for data acquisition.

Note: these are not database models. These are simply to hold the raw tag information
      extracted from the database of choice
"""

from datetime import datetime


class QuerySet:
    """
    Data object representing a query of a given video database with a code
    Iterating over iterates over the metadata
    @args
         (iterable of VideoMetadata): Metadata objects for each code provided
    @returns
    """

    def __init__(self, metadata):
        self.metadata = metadata

    def __iter__(self):
        return iter(self.metadata)


class VideoMetadata:
    """Data object collecting metadata for a video across multiple languages
    """

    def __init__(self, code, release_date, tags,
                 director, maker, label,
                 image_path, stars):
        """Initiation assumnes that the tags are all using english language database
        (Or whatever the default is)
        Args:
            code (str): Description
            release_date (str): Description
            tags (list=> tuple(str, str)): Description
            director (tuple(str, str)): Description
            maker (tuple(str, str)): Description
            label (tuple(str, str)): Description
            image_path (tuple(str, str)): source_tag_id, tag_name
            stars (list=> tuple(str, str)): Description
        """
        self.code = code
        self.release_date = release_date
        self.tags = tags
        self.image_path = image_path
        self.director = director
        self.maker = maker
        self.label = label
        self.stars = stars
        # Only the titles change language
        self.title = {}

    def __repr__(self):
        return f"<VideoMetadata:code={self.code}|tags={self.tags}|stars={self.stars}>"


# Tag related data
class Tag:
    """Tag object
    @attrs
        id (int):
        self.data (dict): Contains TagData objects keyed by language
    """

    def __init__(self, base_lang="en"):
        """
        @args
        # id (int): Unique key to identify a tag
        base_lang (str): Base language to store tag data in. Default English ("en").
                         Japanese ("jp") available
        """
        # self.id = id
        self.data = {}
        self.base_lang = base_lang

    def __repr__(self):
        return f"<Tag:data={self.data[self.base_lang]}>"


class TagData:
    def __init__(self, tag_type, name, lang, display_name=None, committed=True):
        """Information for a specific tag object
        @args:
            tag_type (str): Type of tag star, act, play, etc
            name (str): Unique name of the tag
            lang
            display_name
            comitted (): Has the tag been persisted?
        """
        self.type = tag_type
        self.name = name
        self.lang = lang
        self.display_name = display_name
        if display_name is None:
            self.display_name = name
        self.committed = committed

    def __repr__(self):
        return f"<TagData:{self.type}-{self.name}>"
