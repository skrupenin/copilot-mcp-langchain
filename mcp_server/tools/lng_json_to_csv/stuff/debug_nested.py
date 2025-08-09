"""
Debug nested object processing
"""
import sys
import os

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

from simple_test import json_to_csv, json_to_markdown

# Test nested object from Java test
input_json = """[
    {
        "zField": "value3",
        "aField": "value1",
        "objectField": {
            "name": "banana",
            "color": "yellow"
        },
        "numberArray": [3, 1, 2]
    },
    {
        "zField": "test",
        "name": "example",
        "numberArray": [10, 2, 30]
    }
]"""

print("Input JSON:", input_json)

csv_result = json_to_csv(input_json)
print("CSV result:")
print(csv_result)
print("CSV repr:", repr(csv_result))

print("\nExpected from Java:")
expected = """zField,aField,objectField,,numberArray,name
,,name,color,,
value3,value1,banana,yellow,3,
,,,,1,
,,,,2,
test,,,,10,example
,,,,2,
,,,,30,
"""
print(expected)
print("Expected repr:", repr(expected))