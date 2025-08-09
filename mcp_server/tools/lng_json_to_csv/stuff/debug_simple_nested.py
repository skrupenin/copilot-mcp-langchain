"""
Debug simple nested object
"""
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from simple_test import json_to_csv, json_to_markdown

# Test simple nested object
input_json = """[
    {
        "user": {
            "name": "John",
            "age": 30
        },
        "settings": {
            "theme": "dark",
            "lang": "en"
        }
    }
]"""

print("Input JSON:", input_json)

csv_result = json_to_csv(input_json)
print("CSV result:")
print(csv_result)
print("CSV repr:", repr(csv_result))

md_result = json_to_markdown(input_json)
print("Markdown result:")
print(md_result)
print("Markdown repr:", repr(md_result))

# Also test simpler case
simple_json = """[
    {
        "objectField": {
            "name": "banana",
            "color": "yellow"
        }
    }
]"""

print("\n\nSimple nested object:")
simple_result = json_to_csv(simple_json)
print("CSV result:")
print(simple_result)
print("CSV repr:", repr(simple_result))