from henpy.models import QuerySet
from henpy.persist import tables as T

import logging
# import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound


class SQLTagManager:
    """Basic class handling Tag creation and video tagging
    """

    def __init__(self, db_path):
        self.engine = create_engine(db_path)
        # Create the tables if they don't exist
        T.Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def get_tag(self, tag_name):
        """Gets a tag with name == tag_name
        @args
            tag_name
        @returns
            Tag object or None
        """
        logging.info(f"Querying database for tag with tag_name={tag_name}")
        try:
            # This bit will probably have to be modified for multiple languages.
            # Also, what happens if identical tag_names exist?
            return self.session.query(T.Tag).filter(T.Tag.name == tag_name).one()
        except NoResultFound:
            logging.info(f"Unable to find tag with name '{tag_name}'")
            return None
        # Check for multiple match
        except MultipleResultsFound:
            logging.info(self.session.query(T.Tag).filter(T.Tag.name == tag_name).all())
            raise

    def _create_tag(self, tag_name, tag_data):
        """Creates a tag without committing
        @args:
            tag_name(string): base name of the tag
            tag_data (iterable): Iterables of form (language, tag_type, name, display_name) used to initialize the tag
        """
        tag = T.Tag(name=tag_name)
        data = [T.TagData(language=language,
                          type=tag_type,
                          name=name,
                          display_name=display_name) for language, tag_type, name, display_name in tag_data]
        tag.data = data
        self.session.add(tag)
        return tag

    def create_tag(self, tag_name, tag_data):
        # Maybe put a warning for duplicate tags
        logging.debug(f"Creating tag with tag_name={tag_name}, tag_data={tag_data}")
        tag = self._create_tag(tag_name, tag_data)
        # self.session.add(tag)
        self.session.commit()

    def get_or_create_tag(self, tag_name, tag_type=None, language="en", tag_data=None):
        """Quick and dirty tag creation from just a name and type
        """
        tag = self.get_tag(tag_name)
        if tag:
            return tag
        return self.create_tag(tag_name, tag_data)

    @classmethod
    def from_file(cls, db_path, tag_tsv):
        tm = cls(db_path)
        with open(tag_tsv, encoding="utf-8") as f:
            for line in f:
                # strip out comments
                line = line.split("#")[0].strip()
                if not line:
                    continue
                logging.debug(f"processing line: {line}")
                # Force lowercase for standardization
                line = line.lower()
                e_type, j_type, e_name, j_name = line.split("\t")
                tm._create_tag(e_name, [("en", e_type, e_name, e_name),
                                        ("jp", j_type, j_name, j_name)])
                # # Should we batch commits instead in some create_tags with batchsize = N
                tm.session.commit()
        return tm






# class TagManager:
#     """"Tag manager to handle raw data input from a given source."
#     """

#     def __init__(self, tags=None):
#         # Mapping from string to known tag
#         self.tags = tags
#         if tags is None:
#             self.tags = []
#         # self.next_id = max(tag.id for tag in self.tags) + 1
#         # Create a mapping for tag names of different langues to Tag object
#         self.mapping = {}
#         # for tag in tags:
#         #     for lang, tag_data in tag.data.items():
#         #         self.mapping[tag_data.name.lower()] = tag

#     def __getitem__(self, tag_name):
#         """Get tag from TagManager using the tag name
#         @args
#             tag_name
#         @returns
#             Tag object if exists else None
#         """
#         try:
#             return self.mapping[tag_name.lower()]
#         except KeyError:
#             return None

#     def get_or_create(self, tag_name, tag_type=None, lang="en"):
#         """Gets a tag if it exists in the database otherwise creates it.
#         @args
#             tag_name (string)
#             tag_type (string or None): Tag type to give a tag if it needs to be created
#             lang: Language to creat the tag under
#         @returns
#             Tag object corresponding to the tag_name
#         """
#         res = self[tag_name]
#         if res:
#             return (res, 0)
#         elif tag_type:
#             tag = Tag()
#             tag_data = TagData(tag_type, tag_name, lang)
#             tag.data[lang] = tag_data
#             # self.next_id += 1
#             return tag
#         else:
#             raise Exception("Provide tag_type to enable tag creation")

#     @classmethod
#     def from_file(cls, tag_data):
#         """Performs preliminary loading of all tag information from a given file,
#         @args
#             tagdata (str): Filepath to tsv containing tag information
#         """
#         # initialize tags from file
#         tags = []
#         with open(tag_data, encoding="utf-8") as f:
#             f.readline()
#             for tag_id, line in enumerate(f):
#                 e_type, j_type, e_tag, j_tag = line.strip().split("\t")
#                 e_tag = TagData(e_type, e_tag, "en")
#                 j_tag = TagData(j_type, j_tag, "en")
#                 tag = Tag()
#                 tag.data["en"] = e_tag
#                 tag.data["jp"] = j_tag
#                 tags.append(tag)
#                 # Keep track of the maximum id for incrementing
#         return cls(tags)

#     @classmethod
#     def from_connection(cls, connection):
#         pass



if __name__ == "__main__":
    tm = TagManager.from_file("../data/tagdata.tsv")
    t = tm["couple"]
    print(t.data["en"])
