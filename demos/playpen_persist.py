"""Little playpen demoing the Initialization and persistence of a tag database in the henpy library
What will be shown here is the creation
"""
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from henpy.persist.tables import Base
from henpy.persist import tables

from henpy.utilities.tagtools import TagManager

# Database initialization
# Create the engine in memory
# engine = create_engine("sqlite:///:memory:")
# on on a file to disk
engine = create_engine("sqlite:///test.db")

Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

# Initialize the tag manager from 
tm = TagManager.from_file("data/tagdata.tsv")
for tag in tm.tags:
    tag_name = tag.data[tag.base_lang].name
    db_tag = tables.Tag(name=tag_name)
    db_tag.data = [tables.TagData(language=tag_datum.lang,
                                  name=tag_datum.name,
                                  display_name=tag_datum.display_name)for lang, tag_datum in tag.data.items()]
    session.add(db_tag)
session.commit()