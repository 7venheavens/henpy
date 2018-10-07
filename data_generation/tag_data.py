import yaml
from henpy import models

with open("../supplementary/tags_en.yaml", encoding="utf-8") as f:
    en = yaml.load(f)
with open("../supplementary/tags_jp.yaml", encoding="utf-8") as f:
    jp = yaml.load(f)

with open("../supplementary/tagdata.tsv", "w", encoding="utf-8") as f:
    count = 0
    f.write("e_type\tj_type\te_tag\tj_tag\n")
    for (e_type, e_tags), (j_type, j_tags) in zip(en.items(), jp.items()):
        for e_tag, j_tag in zip(e_tags, j_tags):
            # f.write(f"{e_type.lower()}\t{j_type.lower()}\t{e_tag.lower()}\t{j_tag.lower()}\n")
            f.write(f"{e_type}\t{j_type}\t{e_tag}\t{j_tag}\n")
