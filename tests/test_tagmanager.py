import pytest
import os
import logging

from henpy.persist import tagtools as tt
from henpy.persist.tables import Tag

TEST_DIR = os.path.split(__file__)[0]

@pytest.fixture(scope="function")
def empty_db():
    return "sqlite://"


def test_basic_tag_creation(empty_db):
    tm = tt.SQLTagManager(empty_db)
    # Simple single language tag
    tm.create_tag("tag1", [("en", "tagtype1", "tag1", "tag1")])
    tag1 = tm.get_tag("tag1")
    assert(tag1.data[0].language == "en")
    # Multiple language tag
    tm.create_tag("tag2", [("en", "tagtype1", "tag2", "tag2"),
                           ("jp", "taggutypu1", "taggu2", "taggu2")])
    tag2 = tm.get_tag("tag2")
    jp_data = [i for i in tag2.data if i.language == "jp"]
    assert(len(jp_data) == 1)
    assert(jp_data[0].type == "taggutypu1")


def test_tag_initialization_from_file(empty_db):
    tm = tt.SQLTagManager.from_file(empty_db, os.path.join(TEST_DIR, "data/test_tags_1.tsv"))
    tag = tm.get_tag("affair")
    logging.info([i.name for i in tm.session.query(Tag).all()])
    assert(tag.name == "affair")
    assert(len(tag.data) == 2)
    # Check if the data is loaded properly under the hood
    tags = tm.session.query(Tag).filter(Tag.data.any(type="theme")).all()
    assert(len(tags) == 4)
