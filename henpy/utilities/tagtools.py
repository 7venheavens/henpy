from henpy.models import Tag, TagData


class TagManager:
    """"Tag manager to handle raw data input from a given source."
    """

    def __init__(self, tags=None):
        # Mapping from string to known tag
        self.tags = tags
        if tags is None:
            self.tags = []
        # self.next_id = max(tag.id for tag in self.tags) + 1
        # Create a mapping for tag names of different langues to Tag object
        self.mapping = {}
        # for tag in tags:
        #     for lang, tag_data in tag.data.items():
        #         self.mapping[tag_data.name.lower()] = tag

    def __getitem__(self, tag_name):
        """Get tag from TagManager using the tag name
        @args
            tag_name
        @returns
            Tag object if exists else None
        """
        try:
            return self.mapping[tag_name.lower()]
        except KeyError:
            return None

    def get_or_create(self, tag_name, tag_type=None, lang="en"):
        """Gets a tag if it exists in the database otherwise creates it.
        @args
            tag_name (string)
            tag_type (string or None): Tag type to give a tag if it needs to be created
            lang: Language to creat the tag under
        @returns
            Tag object corresponding to the tag_name
        """
        res = self[tag_name]
        if res:
            return (res, 0)
        elif tag_type:
            tag = Tag()
            tag_data = TagData(tag_type, tag_name, lang)
            tag.data[lang] = tag_data
            # self.next_id += 1
            return tag
        else:
            raise Exception("Provide tag_type to enable tag creation")

    @classmethod
    def from_file(cls, tag_data):
        """
        @args
            tagdata (str): Filepath to tsv containing tag information
        """
        # initialize tags from file
        tags = []
        with open(tag_data, encoding="utf-8") as f:
            f.readline()
            for tag_id, line in enumerate(f):
                e_type, j_type, e_tag, j_tag = line.strip().split("\t")
                e_tag = TagData(e_type, e_tag, "en")
                j_tag = TagData(j_type, j_tag, "en")
                tag = Tag()
                tag.data["en"] = e_tag
                tag.data["jp"] = j_tag
                tags.append(tag)
                # Keep track of the maximum id for incrementing
        return cls(tags)



if __name__ == "__main__":
    tm = TagManager.from_file("../data/tagdata.tsv")
    t = tm["couple"]
    print(t.data["en"])