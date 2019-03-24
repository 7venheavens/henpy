from sqlalchemy import Column, ForeignKey, Integer, String, Date, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.schema import UniqueConstraint

Base = declarative_base()


# Association table for many2many video tag relatiojn
video_tag = Table("video_tag", Base.metadata,
                  Column("video_id", Integer, ForeignKey("video.id"), index=True),
                  Column("tag_id", Integer, ForeignKey("tag.id"), index=True))


class Tag(Base):
    """
    @attrs
        id (integer): unique ID for a tag
        name
        data
    """
    __tablename__ = "tag"
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    data = relationship("TagData")

    videos = relationship(
        "Video",
        secondary=video_tag,
        back_populates="tags")

    def __str__(self):
        return f"<Tag: name={self.name}>"

    def __repr__(self):
        return self.__str__()


class TagData(Base):
    """Language specific tag data

    Attributes:
        display_name (TYPE): Name to be displayed
        id (TYPE): Description
        language (TYPE): Description
        name (TYPE): Core unified name
        tag_id (TYPE): ID of the tag
        type (TYPE): Description
        source_id (string): Id of the tag from the source
    """
    __tablename__ = "tag_data"
    id = Column(Integer, primary_key=True)
    tag_id = Column(Integer, ForeignKey("tag.id"))
    category = Column(String(255), nullable=True)
    language = Column(String(20), nullable=False)
    name = Column(String(255), nullable=False, index=True)
    display_name = Column(String(255), nullable=False)
    source_id = Column(String(255), nullable=True, index=True)

    __table_args__ = (UniqueConstraint("source_id", "language", name="_source_id_language"),
                      )

    tag = relationship("Tag")

    def __repr__(self):
        return f"<TagData: name={self.name}, tag={self.tag}, source_id={self.source_id}>"


class Video(Base):
    """Core video data containing all data of interest
    """
    __tablename__ = "video"

    id = Column(Integer, primary_key=True)
    code = Column(String(50), nullable=False, index=True)
    release_date = Column(Date, index=True, nullable=True)
    image_path = Column(String(255), nullable=True)  # Images are optional
    director = Column(String(100), nullable=False)
    maker = Column(String(100), nullable=False)
    label = Column(String(100), nullable=False)

    tags = relationship(
        "Tag",
        secondary=video_tag,
        back_populates="videos")

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"<VideoMetadata:code={self.code}>"


class VideoData(Base):
    """Video data containing language requirements
    """
    __tablename__ = "video_data"
    id = Column(Integer, primary_key=True)
    title = Column(String(100), nullable=False)
    language = Column(String(20), nullable=False)
