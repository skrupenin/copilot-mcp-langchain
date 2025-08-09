"""
Debug array of objects markdown
"""
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from simple_test import json_to_csv, json_to_markdown

# Test array of objects
input_json = """[
    {
        "name": "test1",
        "items": [
            {"id": 1, "value": "a"},
            {"id": 2, "value": "b"}
        ]
    },
    {
        "name": "test2", 
        "items": [
            {"id": 3, "value": "c"},
            {"id": 4, "value": "d"}
        ]
    }
]"""

md_result = json_to_markdown(input_json)
print("Markdown result:")
print(md_result)
print("Markdown repr:", repr(md_result))