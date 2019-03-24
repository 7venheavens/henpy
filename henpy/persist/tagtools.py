from henpy.models import QuerySet
from henpy.persist import tables as T

import logging
# import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.exc import ArgumentError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.exc import NoResultFound, MultipleResultsFound
from functools import lru_cache


logger = logging.getLogger(__name__)


class SQLTagManager:
    """Overall handler of tag creation / video tagging using a SQL backend
    """

    def __init__(self, db_path):
        try:
            self.engine = create_engine(db_path)
        except ArgumentError:
            # if it fails here like this, it's probably due to the lack of a sqlite:// prefix
            self.engine = create_engine("sqlite:///" + db_path)

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
        logger.info(f"Querying database for tag with tag_name={tag_name}")
        try:
            # This bit will probably have to be modified for multiple languages.
            # Also, what happens if identical tag_names exist?
            return self.session.query(T.Tag).filter(T.Tag.name == tag_name).one()
        except NoResultFound:
            logger.info(f"Unable to find tag with name '{tag_name}'")
            return None
        # Check for multiple match
        except MultipleResultsFound:
            logger.info(self.session.query(T.Tag).filter(T.Tag.name == tag_name).all())
            raise

    def _create_tag(self, tag_name, tag_data):
        """Creates a tag without committing
        @args:
            tag_name(string): base name of the tag
            tag_data (iter dict): Iterables containing tag data necessary to creat the tag data instances
        """
        tag = T.Tag(name=tag_name)
        data = [T.TagData(**tag_datum) for tag_datum in tag_data]
        tag.data = data
        self.session.add(tag)
        return tag

    def create_tag(self, tag_name, tag_data):
        # Maybe put a warning for duplicate tags
        logger.debug(f"Creating tag with tag_name={tag_name}, tag_data={tag_data}")
        tag = self._create_tag(tag_name, tag_data)
        self.save()
        return tag

    def get_or_create_tag(self, tag_name, tag_type=None, language="en", tag_data=None):
        """Quick and dirty tag creation from just a name and type
        """
        tag = self.get_tag(tag_name)
        if tag:
            return tag
        return self.create_tag(tag_name, tag_data)

    @lru_cache(maxsize=None)
    def get_tag_from_data(self, query, col="name", return_first=False):
        """Queries a tag using a given field's data

        Args:
            query (TYPE): Description
            col (str, optional): Description
            return_first (bool, optional): If True, on a multiple match, returns the first entry.
                                           This seems like a trap, but is best used on cases where it doesn't matter
                                           For instance, when getting tag_data by source_id. Due to multiple languages
                                           the same id might exist multiple times. Use it then.

        Returns:
            Tag: Description
        """
        logger.info(f"Querying database for tag with col:{col} == {query}")
        try:
            # This bit will probably have to be modified for multiple languages.
            if return_first:
                logger.debug("return_first: 0")
                return self.session.query(T.Tag).filter(T.Tag.data.any(getattr(T.TagData, col) == query)).first()
            logger.info(f"Found a singular entry")
            return self.session.query(T.Tag).filter(T.Tag.data.any(getattr(T.TagData, col) == query)).one()
        except NoResultFound:
            logger.info(f"Unable to find tag with col:{col} == {query}")
            return None
        # Check for multiple match
        except MultipleResultsFound:
            logger.error(f"Expected one result. Found "
                         f"{self.session.query(T.Tag).filter(T.Tag.data.any(getattr(T.TagData, col) == query)).all()}")

    def add_video(self, video_data, create_tag_if_missing=False, create_star_if_missing=True):
        """Adds a video to the database

        Args:
            video_data (henpy.models.VideoMetadata): VideoMetadata object containing video data
            create_tag_if_missing (bool, optional): If true, automatically creates a tag if it is missing
        """
        # Get the tags first
        tags = []
        for source_id, tag_name in video_data.tags:
            # Get the tag using the source_id
            # RETURN FIRST IS NECESSARY HERE DUE TO THE MULTIMAPPING
            tag = self.get_tag_from_data(source_id, col="source_id", return_first=True)
            logging.debug(f"Query for source_id={source_id} found tag={tag}")
            if tag is None:
                # Currently unhandled
                if create_tag_if_missing:
                    pass
                continue
            tags.append(tag)
        # Then the stars
        stars = []
        for source_id, tag_name in video_data.stars:
            star = self.get_tag_from_data(source_id, col="source_id", return_first=True)
            logging.debug(f"Unable to find star={tag_name} with id={source_id}")
            if star is None:
                # Create and save the tag if necessary
                if create_star_if_missing:
                    logging.debug(f"Unable to find star={tag_name} with id={source_id}")
                    tag = self.create_tag(tag_name, [{"category": "star",
                                                      "language": "en",
                                                      "name": tag_name,
                                                      "display_name": tag_name,
                                                      "source_id": source_id}])
                else:
                    continue
            stars.append(tag)

        # Then the supplementary information
        maker = video_data.maker[0]
        label = video_data.label[0]
        director = video_data.director[0]
        print(stars, tags)
        video = T.Video(code=video_data.code,
                        release_date=video_data.release_date,
                        image_path=video_data.image_path,
                        director=director,
                        maker=maker,
                        label=label,
                        tags=tags + stars)
        self.session.add(video)

    def save(self):
        """Persists any changes. This is just to allow for other backends
        """
        self.session.commit()

    # This is outdated and needs to be redone
    # @classmethod
    # def from_file(cls, db_path, tag_tsv):
    #     tm = cls(db_path)
    #     with open(tag_tsv, encoding="utf-8") as f:
    #         for line in f:
    #             # strip out comments
    #             line = line.split("#")[0].strip()
    #             if not line:
    #                 continue
    #             logger.debug(f"processing line: {line}")
    #             # Force lowercase for standardization
    #             line = line.lower()
    #             e_type, j_type, e_name, j_name = line.split("\t")
    #             tm._create_tag(e_name, [("en", e_type, e_name, e_name),
    #                                     ("jp", j_type, j_name, j_name)])
    #             # # Should we batch commits instead in some create_tags with batchsize = N
    #             tm.session.commit()
    #     return tm


if __name__ == "__main__":
    from henpy.misc import data_dir, playpen_dir, logging_config_path
    from henpy.persist.init import initalize_javlib
    import os
    import logging.config
    logging.config.fileConfig(logging_config_path, disable_existing_loggers=False)
    logging.getLogger().setLevel(logging.DEBUG)

    en_path = os.path.join(data_dir, "javlib_tagdata_en.tsv")
    jp_path = os.path.join(data_dir, "javlib_tagdata_jp.tsv")
    tag_dict = {"en": en_path, "jp": jp_path}
    playpen_data_path = os.path.join(playpen_dir, "db.sqlite3")
    # Remove the instance first
    os.remove(playpen_data_path)
    tag_manager = SQLTagManager(playpen_data_path)
    initalize_javlib(tag_dict, tag_manager)
    tag = tag_manager.get_tag_from_data("javlib_a46q", col="source_id", return_first=True)
    print(tag)
    print(tag.data)
    # assert(tag == )

    # tag_manager.get_tag_from_data_
