"""
General use models for data acquisition
"""

from datetime import datetime

class QuerySet:
    """
    Data object representing a query of a given video database with a code
    Iterating over iterates over the metadata
    @args
        metadata (iterable of VideoMetadata): Metadata objects for each code provided
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
                 image_path):
        """
        """
        self.code = code
        self.release_date = release_date
        self.tags = tags
        self.image_path = image_path
        self.director = director
        self.maker = maker
        self.lable = label
        # Only the titles change language
        self.titles = {}

    def __repr__(self):
        f"<VideoMetadata:code={self.code}|tags={self.tags}>"

# Tag related data
class Tag:
    """Tag object
    @args
        id
        base_lang (str): Base language to store tag data in. Default English ("en").
                         Japanese ("jp") available
    """

    def __init__(self, id, base_lang="en"):
        self.id = id
        self.data = {}
        self.base_lang = base_lang

    def __repr__(self):
        return f"<Tag: id={self.id}, data={self.data[self.base_lang ]}>"


class TagData:
    def __init__(self, tag_type, name, lang, display_name=None):
        """
        @args:
            tag_type (str): Type of tag star, act, play, etc
            name (str): Unique name of the tag
            lang
            display_name
        """
        self.type = tag_type
        self.name = name
        self.lang = lang
        self.display_name = display_name
        if display_name is None:
            self.display_name = name

    def __repr__(self):
        return f"<TagData:{self.type}-{self.name}>"
