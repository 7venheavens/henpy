"""Misc functions and variables to make 
"""
import os


test_dir = os.path.join(os.path.dirname(__file__), "data/test")
test_dir = os.path.normpath(test_dir)

cached_pages_dir = os.path.join(test_dir, "cached_pages")

if __name__ == "__main__":
    print(test_dir)
