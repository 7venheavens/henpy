"""Misc functions and variables to make
"""
import os


data_dir = os.path.join(os.path.dirname(__file__), "data")
playpen_dir = os.path.join(data_dir, "playpen")

# Config dirs/paths
config_dir = os.path.join(data_dir, "config")
config_default_path = os.path.join(config_dir, "default.yaml")
logging_config_path = os.path.join(config_dir, "logger.conf")

test_dir = os.path.join(data_dir, "test")
test_dir = os.path.normpath(test_dir)

# Test directory containing various sync tests
test_sync_dir = os.path.join(test_dir, "sync")

# Directory to the cached page data for tests
cached_pages_dir = os.path.join(test_dir, "cached_pages")


if __name__ == "__main__":
    print(test_dir)
