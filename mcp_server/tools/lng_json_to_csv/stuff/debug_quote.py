"""
Debug quote escaping issue
"""
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from simple_test import json_to_csv, json_to_markdown

# Test quote escaping
input_json = """[
    {
        "field": "val\\"ue1"
    }
]"""

print("Input JSON:", repr(input_json))
print("Parsed JSON value:", repr("val\"ue1"))  # This is what JSON parsing should give us

csv_result = json_to_csv(input_json)
print("CSV result:", repr(csv_result))

md_result = json_to_markdown(input_json)
print("Markdown result:", repr(md_result))

print("\nExpected CSV:")
print(repr('field\n"val""ue1"\n'))

print("\nExpected Markdown:")
print(repr('field  \n-------\nval"ue1\n'))