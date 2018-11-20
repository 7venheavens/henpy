from sqlalchemy import Column, ForeignKey, Integer, String, Date, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine


Base = declarative_base()


# Association table for many2many video tag relatiojn
video_tag = Table("video_tag", Base.metadata,
                  Column("video_id", Integer, ForeignKey("video.id")),
                  Column("tag_id", Integer, ForeignKey("tag.id")),)


class Tag(Base):
    """
    @attrs
        id
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


class TagData(Base):
    """Language specific tag data
    @attrs
        id
        tag
        language
        name
        display_name
    """
    __tablename__ = "tag_data"
    id = Column(Integer, primary_key=True)
    tag_id = Column(Integer, ForeignKey("tag.id"))
    type = Column(String(255))
    language = Column(String(20), nullable=False)
    name = Column(String(255), nullable=False, index=True)
    display_name = Column(String(255), nullable=False)


class Video(Base):
    __tablename__ = "video"

    id = Column(Integer, primary_key=True)
    code = Column(String(50), nullable=False, index=True)
    release_date = Column(Date, index=True)
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
