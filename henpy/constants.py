"""Constants and configuration
"""

import os

tag_data_path = os.path.split(__file__)[0]
tag_data_path = os.path.normpath(os.path.join(tag_data_path, "data/tagdata.tsv"))