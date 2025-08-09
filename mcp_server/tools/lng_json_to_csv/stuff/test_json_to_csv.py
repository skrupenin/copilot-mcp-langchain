import unittest
import sys
import os
import json

# Add the parent directory to the path to import the tool
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from tool import json_to_csv, json_to_markdown

class JsonToCsvTest(unittest.TestCase):
    """Test cases exactly matching the Java JsonToCsvTest.java implementation."""
    
    def assert_r(self, expected: str):
        """Helper method to assert conversion like Java assertR method."""
        input_json = expected.split("\n\n")[0]
        actual_csv = json_to_csv(input_json)
        actual_markdown = json_to_markdown(input_json)
        actual = input_json + "\n\n\n" + actual_csv + "\n\n" + actual_markdown
        
        self.assertEqual(expected, actual, 
                        f"Conversion failed.\nExpected:\n{repr(expected)}\nActual:\n{repr(actual)}")
    
    def test_json_to_csv_simple_one_object_one_field(self):
        """Test conversion of simple JSON object with one field."""
        self.assert_r("""[
    {
        "field": "value1"
    }
]


field
value1


field 
------
value1
""")
    
    def test_json_to_csv_simple_one_object_one_field_case_escape_case_comma(self):
        """Test conversion with comma escaping."""
        self.assert_r("""[
    {
        "field": "val,ue1"
    }
]


field
"val,ue1"


field  
-------
val,ue1
""")
    
    def test_json_to_csv_simple_one_object_one_field_case_escape_case_quote(self):
        """Test conversion with quote escaping."""
        self.assert_r("""[
    {
        "field": "val\\"ue1"
    }
]


field
"val""ue1"


field  
-------
val"ue1
""")
    
    def test_json_to_csv_simple_one_object_one_field_case_escape_case_new_line(self):
        """Test conversion with newline escaping."""
        self.assert_r("""[
    {
        "field": "val\\nue1"
    }
]


field
"val
ue1"


field  
-------
val
ue1
""")
    
    def test_json_to_csv_simple_two_objects_one_field(self):
        """Test conversion of two objects with one field."""
        self.assert_r("""[
    {
        "field": "value1"
    },
    {
        "field": "value2"
    }
]


field
value1
value2


field 
------
value1
value2
""")
        
    def test_json_to_csv_simple_one_object_two_fields(self):
        """Test conversion of one object with two fields."""
        self.assert_r("""[
    {
        "field1": "value1",
        "field2": "value2"
    }
]


field1,field2
value1,value2


field1|field2
-------------
value1|value2
""")
        
    def test_json_to_csv_simple_two_objects_two_fields(self):
        """Test conversion of two objects with two fields."""
        self.assert_r("""[
    {
        "field1": "value1",
        "field2": "value2"
    },
    {
        "field1": "value3",
        "field2": "value4"
    }
]


field1,field2
value1,value2
value3,value4


field1|field2
-------------
value1|value2
value3|value4
""")
        
    def test_json_to_csv_simple(self):
        """Test conversion with different fields per object."""
        self.assert_r("""[
    {
        "zField": "value3",
        "aField": "value1"
    },
    {
        "zField": "test",
        "name": "example"
    }
]


zField,aField,name
value3,value1,
test,,example


zField|aField|name   
---------------------
value3|value1|       
test  |      |example
""")
        
    def test_json_to_csv_sub_array_case_simple(self):
        """Test conversion with simple sub-arrays."""
        self.assert_r("""[
    {
        "field": "value1",
        "array": ["value2", "value3"]
    },
    {
        "field": "value4",
        "array": ["value5", "value6"]
    }
]


field,array
value1,value2
,value3
value4,value5
,value6


field |array 
-------------
value1|value2
      |value3
value4|value5
      |value6
""")
        
    def test_json_to_csv_sub_array(self):
        """Test conversion with number arrays."""
        self.assert_r("""[
    {
        "zField": "value3",
        "aField": "value1",
        "numberArray": [3, 1, 2]
    },
    {
        "zField": "test",
        "name": "example",
        "numberArray": [10, 2, 30]
    }
]


zField,aField,numberArray,name
value3,value1,3,
,,1,
,,2,
test,,10,example
,,2,
,,30,


zField|aField|numberArray|name   
---------------------------------
value3|value1|3          |       
      |      |1          |       
      |      |2          |       
test  |      |10         |example
      |      |2          |       
      |      |30         |       
""")
        
    def test_json_to_csv_sub_array_not_same_length(self):
        """Test conversion with arrays of different lengths."""
        self.assert_r("""[
    {
        "zField": "value3",
        "aField": "value1",
        "numberArray": [3, 1, 2]
    },
    {
        "zField": "test",
        "name": "example",
        "numberArray": [10, 2, 30]
    },
    {
        "id": "12345",
        "aField": "value6",
        "numberArray": [1, 10, 100, 1000]
    }
]


zField,aField,numberArray,name,id
value3,value1,3,,
,,1,,
,,2,,
test,,10,example,
,,2,,
,,30,,
,value6,1,,12345
,,10,,
,,100,,
,,1000,,


zField|aField|numberArray|name   |id   
---------------------------------------
value3|value1|3          |       |     
      |      |1          |       |     
      |      |2          |       |     
test  |      |10         |example|     
      |      |2          |       |     
      |      |30         |       |     
      |value6|1          |       |12345
      |      |10         |       |     
      |      |100        |       |     
      |      |1000       |       |     
""")
        
    def test_json_to_csv_two_different_arrays(self):
        """Test conversion with two different arrays."""
        self.assert_r("""[
    {
        "filed": "name",
        "array1": [1, 2, 3],
        "array2": [4, 5, 6]
    }
]


filed,array1,array2
name,1,4
,2,5
,3,6


filed|array1|array2
-------------------
name |1     |4     
     |2     |5     
     |3     |6     
""")

    def test_json_to_csv_sub_array_of_objects_case_same_arrays_length(self):
        """Test conversion with arrays of objects with same lengths."""
        self.assert_r("""[
    {
        "zField": "value3",
        "aField": "value1",
        "arrayField": [
            {"name": "banana", "color": "yellow"},
            {"name": "apple", "color": "red"},
            {"name": "cherry", "color": "red"}
        ],
        "numberArray": [3, 1, 2]
    },
    {
        "zField": "test",
        "name": "example",
        "numberArray": [10, 2, 30]
    }
]


zField,aField,arrayField,,numberArray,name
,,name,color,,
value3,value1,banana,yellow,3,
,,apple,red,1,
,,cherry,red,2,
test,,,,10,example
,,,,2,
,,,,30,


zField|aField|arrayField|      |numberArray|name   
      |      |name      |color |           |       
---------------------------------------------------
value3|value1|banana    |yellow|3          |       
      |      |apple     |red   |1          |       
      |      |cherry    |red   |2          |       
test  |      |          |      |10         |example
      |      |          |      |2          |       
      |      |          |      |30         |       
""")

    def test_json_to_csv_sub_array_of_objects_case_one_is_less(self):
        """Test conversion with arrays of objects where one is shorter."""
        self.assert_r("""[
    {
        "zField": "value3",
        "aField": "value1",
        "arrayField": [
            {"name": "banana", "color": "yellow"},
            {"name": "apple", "color": "red"}
        ],
        "numberArray": [3, 1, 2]
    },
    {
        "zField": "test",
        "name": "example",
        "numberArray": [10, 2, 30]
    }
]


zField,aField,arrayField,,numberArray,name
,,name,color,,
value3,value1,banana,yellow,3,
,,apple,red,1,
,,,,2,
test,,,,10,example
,,,,2,
,,,,30,


zField|aField|arrayField|      |numberArray|name   
      |      |name      |color |           |       
---------------------------------------------------
value3|value1|banana    |yellow|3          |       
      |      |apple     |red   |1          |       
      |      |          |      |2          |       
test  |      |          |      |10         |example
      |      |          |      |2          |       
      |      |          |      |30         |       
""")

    def test_json_to_csv_sub_array_of_objects_case_another_is_less(self):
        """Test conversion with arrays where another one is shorter."""
        self.assert_r("""[
    {
        "zField": "value3",
        "aField": "value1",
        "arrayField": [
            {"name": "banana", "color": "yellow"},
            {"name": "apple", "color": "red"},
            {"name": "cherry", "color": "red"}
        ],
        "numberArray": [3, 1]
    },
    {
        "zField": "test",
        "name": "example",
        "numberArray": [10, 2, 30]
    }
]


zField,aField,arrayField,,numberArray,name
,,name,color,,
value3,value1,banana,yellow,3,
,,apple,red,1,
,,cherry,red,,
test,,,,10,example
,,,,2,
,,,,30,


zField|aField|arrayField|      |numberArray|name   
      |      |name      |color |           |       
---------------------------------------------------
value3|value1|banana    |yellow|3          |       
      |      |apple     |red   |1          |       
      |      |cherry    |red   |           |       
test  |      |          |      |10         |example
      |      |          |      |2          |       
      |      |          |      |30         |       
""")

    def test_json_to_csv_sub_array_of_objects_that_contains_of_objects(self):
        """Test conversion with nested objects within array objects."""
        self.assert_r("""[
    {
        "zField": "value3",
        "aField": "value1",
        "arrayField": [
            {"name": "banana", "color":
                {"id": "y", "value": "yellow"}
            },
            {"name": "apple", "color":
                {"id": "r", "value": "red"}
            },
            {"name": "cherry", "color":
                {"id": "r", "value": "red"}
            }
        ],
        "numberArray": [3, 1, 2]
    },
    {
        "zField": "test",
        "name": "example",
        "numberArray": [10, 2, 30]
    }
]


zField,aField,arrayField,,,numberArray,name
,,name,color,,,
,,,id,value,,
value3,value1,banana,y,yellow,3,
,,apple,r,red,1,
,,cherry,r,red,2,
test,,,,,10,example
,,,,,2,
,,,,,30,


zField|aField|arrayField|     |      |numberArray|name   
      |      |name      |color|      |           |       
      |      |          |id   |value |           |       
---------------------------------------------------------
value3|value1|banana    |y    |yellow|3          |       
      |      |apple     |r    |red   |1          |       
      |      |cherry    |r    |red   |2          |       
test  |      |          |     |      |10         |example
      |      |          |     |      |2          |       
      |      |          |     |      |30         |       
""")

    def test_json_to_csv_sub_array_of_objects_that_contains_of_array_of_objects(self):
        """Test conversion with arrays of objects containing arrays of objects."""
        self.assert_r("""[
    {
        "zField": "value3",
        "aField": "value1",
        "arrayField": [
            {"name": "banana", "colors": [
                {"id": "y", "value": "yellow"},
                {"id": "g", "value": "green"}
            ]},
            {"name": "apple", "colors": [
                {"id": "m", "value": "magenta"}
            ]},
            {"name": "cherry", "colors": [
                {"id": "bl", "value": "black"},
                {"id": "w", "value": "white"},
                {"id": "br", "value": "brown"}
            ]}
        ],
        "numberArray": [3, 1, 2]
    },
    {
        "zField": "test",
        "name": "example",
        "numberArray": [10, 2, 30]
    }
]


zField,aField,arrayField,,,numberArray,name
,,name,colors,,,
,,,id,value,,
value3,value1,banana,y,yellow,3,
,,,g,green,1,
,,apple,m,magenta,2,
,,cherry,bl,black,,
,,,w,white,,
,,,br,brown,,
test,,,,,10,example
,,,,,2,
,,,,,30,


zField|aField|arrayField|      |       |numberArray|name   
      |      |name      |colors|       |           |       
      |      |          |id    |value  |           |       
-----------------------------------------------------------
value3|value1|banana    |y     |yellow |3          |       
      |      |          |g     |green  |1          |       
      |      |apple     |m     |magenta|2          |       
      |      |cherry    |bl    |black  |           |       
      |      |          |w     |white  |           |       
      |      |          |br    |brown  |           |       
test  |      |          |      |       |10         |example
      |      |          |      |       |2          |       
      |      |          |      |       |30         |       
""")

    def test_json_to_csv_object_with_object(self):
        """Test conversion with nested objects (not arrays)."""
        self.assert_r("""[
    {
        "zField": "value3",
        "aField": "value1",
        "objectField": {
            "name": "banana",             "color": "yellow"
        },
        "numberArray": [3, 1, 2]
    },
    {
        "zField": "test",
        "name": "example",
        "numberArray": [10, 2, 30]
    }
]


zField,aField,objectField,,numberArray,name
,,name,color,,
value3,value1,banana,yellow,3,
,,,,1,
,,,,2,
test,,,,10,example
,,,,2,
,,,,30,


zField|aField|objectField|      |numberArray|name   
      |      |name       |color |           |       
----------------------------------------------------
value3|value1|banana     |yellow|3          |       
      |      |           |      |1          |       
      |      |           |      |2          |       
test  |      |           |      |10         |example
      |      |           |      |2          |       
      |      |           |      |30         |       
""")

    def test_json_to_csv_partially_from_different_lines(self):
        """Test complex partially mixed structure."""
        self.assert_r("""[
  {
    "date": "2025-03-17",
    "one": {
      "data1": 0
    },
    "data2": 1,
    "two": {
      "data3": 0
    },
    "data4": 1,
    "three": {
      "data5": 0
    }
  },
  {
    "date": "2025-03-18",
    "one": {
      "data6": [
        {
          "name": "JetBrains"
        },
        {
          "name": "vscode"
        }
      ]
    },
    "data2": 5,
    "two": {
      "data3": 0
    },
    "data4": 3,
    "three": {
      "data5": 0
    }
  }
]


date,one,,data2,two,data4,three
,data1,data6,,data3,,data5
,,name,,,,
2025-03-17,0,,1,0,1,0
2025-03-18,,JetBrains,5,0,3,0
,,vscode,,,,


date      |one  |         |data2|two  |data4|three
          |data1|data6    |     |data3|     |data5
          |     |name     |     |     |     |     
--------------------------------------------------
2025-03-17|0    |         |1    |0    |1    |0    
2025-03-18|     |JetBrains|5    |0    |3    |0    
          |     |vscode   |     |     |     |     
""")

    def test_json_to_csv_complex(self):
        """Test conversion with complex nested structure."""
        self.assert_r("""[
  {
    "date": "2025-03-17",
    "copilot_ide_chat": {
      "total_engaged_users": 0
    },
    "total_active_users": 1,
    "copilot_dotcom_chat": {
      "total_engaged_users": 0
    },
    "total_engaged_users": 1,
    "copilot_dotcom_pull_requests": {
      "total_engaged_users": 0
    },
    "copilot_ide_code_completions": {
      "editors": [
        {
          "name": "JetBrains",
          "models": [
            {
              "name": "default",
              "languages": [
                {
                  "name": "json",
                  "total_engaged_users": 1,
                  "total_code_acceptances": 1,
                  "total_code_suggestions": 1,
                  "total_code_lines_accepted": 1,
                  "total_code_lines_suggested": 1
                }
              ],
              "is_custom_model": false,
              "total_engaged_users": 1
            }
          ],
          "total_engaged_users": 1
        }
      ],
      "languages": [
        {
          "name": "json",
          "total_engaged_users": 1
        }
      ],
      "total_engaged_users": 1
    }
  },
  {
    "date": "2025-03-18",
    "copilot_ide_chat": {
      "editors": [
        {
          "name": "JetBrains",
          "models": [
            {
              "name": "default",
              "total_chats": 4,
              "is_custom_model": false,
              "total_engaged_users": 1,
              "total_chat_copy_events": 1,
              "total_chat_insertion_events": 0
            }
          ],
          "total_engaged_users": 1
        },
        {
          "name": "vscode",
          "models": [
            {
              "name": "default",
              "total_chats": 4,
              "is_custom_model": false,
              "total_engaged_users": 1,
              "total_chat_copy_events": 0,
              "total_chat_insertion_events": 0
            }
          ],
          "total_engaged_users": 1
        }
      ],
      "total_engaged_users": 2
    },
    "total_active_users": 5,
    "copilot_dotcom_chat": {
      "total_engaged_users": 0
    },
    "total_engaged_users": 3,
    "copilot_dotcom_pull_requests": {
      "total_engaged_users": 0
    },
    "copilot_ide_code_completions": {
      "editors": [
        {
          "name": "JetBrains",
          "models": [
            {
              "name": "default",
              "languages": [
                {
                  "name": "java",
                  "total_engaged_users": 2,
                  "total_code_acceptances": 12,
                  "total_code_suggestions": 67,
                  "total_code_lines_accepted": 18,
                  "total_code_lines_suggested": 214
                },
                {
                  "name": "unknown",
                  "total_engaged_users": 0,
                  "total_code_acceptances": 0,
                  "total_code_suggestions": 11,
                  "total_code_lines_accepted": 0,
                  "total_code_lines_suggested": 21
                },
                {
                  "name": "json",
                  "total_engaged_users": 0,
                  "total_code_acceptances": 0,
                  "total_code_suggestions": 1,
                  "total_code_lines_accepted": 0,
                  "total_code_lines_suggested": 13
                }
              ],
              "is_custom_model": false,
              "total_engaged_users": 2
            }
          ],
          "total_engaged_users": 2
        }
      ],
      "languages": [
        {
          "name": "java",
          "total_engaged_users": 2
        },
        {
          "name": "unknown",
          "total_engaged_users": 0
        },
        {
          "name": "json",
          "total_engaged_users": 0
        }
      ],
      "total_engaged_users": 2
    }
  }
]


date,copilot_ide_chat,,,,,,,,,total_active_users,copilot_dotcom_chat,total_engaged_users,copilot_dotcom_pull_requests,copilot_ide_code_completions,,,,,,,,,,,,,
,total_engaged_users,editors,,,,,,,,,total_engaged_users,,total_engaged_users,editors,,,,,,,,,,,languages,,total_engaged_users
,,name,models,,,,,,total_engaged_users,,,,,name,models,,,,,,,,,total_engaged_users,name,total_engaged_users,
,,,name,total_chats,is_custom_model,total_engaged_users,total_chat_copy_events,total_chat_insertion_events,,,,,,,name,languages,,,,,,is_custom_model,total_engaged_users,,,,
,,,,,,,,,,,,,,,,name,total_engaged_users,total_code_acceptances,total_code_suggestions,total_code_lines_accepted,total_code_lines_suggested,,,,,,
2025-03-17,0,,,,,,,,,1,0,1,0,JetBrains,default,json,1,1,1,1,1,false,1,1,json,1,1
2025-03-18,2,JetBrains,default,4,false,1,1,0,1,5,0,3,0,JetBrains,default,java,2,12,67,18,214,false,2,2,java,2,2
,,vscode,default,4,false,1,0,0,1,,,,,,,unknown,0,0,11,0,21,,,,unknown,0,
,,,,,,,,,,,,,,,,json,0,0,1,0,13,,,,json,0,


date      |copilot_ide_chat   |         |       |           |               |                   |                      |                           |                   |total_active_users|copilot_dotcom_chat|total_engaged_users|copilot_dotcom_pull_requests|copilot_ide_code_completions|       |         |                   |                      |                      |                         |                          |               |                   |                   |         |                   |                   
          |total_engaged_users|editors  |       |           |               |                   |                      |                           |                   |                  |total_engaged_users|                   |total_engaged_users         |editors                     |       |         |                   |                      |                      |                         |                          |               |                   |                   |languages|                   |total_engaged_users
          |                   |name     |models |           |               |                   |                      |                           |total_engaged_users|                  |                   |                   |                            |name                        |models |         |                   |                      |                      |                         |                          |               |                   |total_engaged_users|name     |total_engaged_users|                   
          |                   |         |name   |total_chats|is_custom_model|total_engaged_users|total_chat_copy_events|total_chat_insertion_events|                   |                  |                   |                   |                            |                            |name   |languages|                   |                      |                      |                         |                          |is_custom_model|total_engaged_users|                   |         |                   |                   
          |                   |         |       |           |               |                   |                      |                           |                   |                  |                   |                   |                            |                            |       |name     |total_engaged_users|total_code_acceptances|total_code_suggestions|total_code_lines_accepted|total_code_lines_suggested|               |                   |                   |         |                   |                   
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
2025-03-17|0                  |         |       |           |               |                   |                      |                           |                   |1                 |0                  |1                  |0                           |JetBrains                   |default|json     |1                  |1                     |1                     |1                        |1                         |false          |1                  |1                  |json     |1                  |1                  
2025-03-18|2                  |JetBrains|default|4          |false          |1                  |1                     |0                          |1                  |5                 |0                  |3                  |0                           |JetBrains                   |default|java     |2                  |12                    |67                    |18                       |214                       |false          |2                  |2                  |java     |2                  |2                  
          |                   |vscode   |default|4          |false          |1                  |0                     |0                          |1                  |                  |                   |                   |                            |                            |       |unknown  |0                  |0                     |11                    |0                        |21                        |               |                   |                   |unknown  |0                  |                   
          |                   |         |       |           |               |                   |                      |                           |                   |                  |                   |                   |                            |                            |       |json     |0                  |0                     |1                     |0                        |13                        |               |                   |                   |json     |0                  |                   
""")

    def test_json_to_csv_corner_case(self):
        """Test complex nested corner case."""
        self.assert_r("""[
  {
    "date": "2025-03-17",
    "object": {
      "field1": [
        {
          "name": "field1_name",
          "array1": [
            {
              "name": "array1_name",
              "array2": [
                {
                  "name": "array2_name",
                  "data3": 3
                }
              ],
              "data4": 4
            }
          ],
          "data5": 5
        }
      ],
      "field2": [
        {
          "name": "field2_name",
          "data6": 6
        }
      ],
      "data7": 7
    }
  }
]


date,object,,,,,,,,
,field1,,,,,,field2,,data7
,name,array1,,,,data5,name,data6,
,,name,array2,,data4,,,,
,,,name,data3,,,,,
2025-03-17,field1_name,array1_name,array2_name,3,4,5,field2_name,6,7


date      |object     |           |           |     |     |     |           |     |     
          |field1     |           |           |     |     |     |field2     |     |data7
          |name       |array1     |           |     |     |data5|name       |data6|     
          |           |name       |array2     |     |data4|     |           |     |     
          |           |           |name       |data3|     |     |           |     |     
----------------------------------------------------------------------------------------
2025-03-17|field1_name|array1_name|array2_name|3    |4    |5    |field2_name|6    |7    
""")

    def test_json_to_csv_super_complex(self):
        """Test super complex conversion with large dataset (minified JSON)."""
        json_data = '[{"date":"2025-03-17","copilot_ide_chat":{"total_engaged_users":0},"total_active_users":1,"copilot_dotcom_chat":{"total_engaged_users":0},"total_engaged_users":1,"copilot_dotcom_pull_requests":{"total_engaged_users":0},"copilot_ide_code_completions":{"editors":[{"name":"JetBrains","models":[{"name":"default","languages":[{"name":"json","total_engaged_users":1,"total_code_acceptances":1,"total_code_suggestions":1,"total_code_lines_accepted":1,"total_code_lines_suggested":1}],"is_custom_model":false,"total_engaged_users":1}],"total_engaged_users":1}],"languages":[{"name":"json","total_engaged_users":1}],"total_engaged_users":1}},{"date":"2025-03-18","copilot_ide_chat":{"editors":[{"name":"JetBrains","models":[{"name":"default","total_chats":4,"is_custom_model":false,"total_engaged_users":1,"total_chat_copy_events":1,"total_chat_insertion_events":0}],"total_engaged_users":1},{"name":"vscode","models":[{"name":"default","total_chats":4,"is_custom_model":false,"total_engaged_users":1,"total_chat_copy_events":0,"total_chat_insertion_events":0}],"total_engaged_users":1}],"total_engaged_users":2},"total_active_users":5,"copilot_dotcom_chat":{"total_engaged_users":0},"total_engaged_users":3,"copilot_dotcom_pull_requests":{"total_engaged_users":0},"copilot_ide_code_completions":{"editors":[{"name":"JetBrains","models":[{"name":"default","languages":[{"name":"java","total_engaged_users":2,"total_code_acceptances":12,"total_code_suggestions":67,"total_code_lines_accepted":18,"total_code_lines_suggested":214},{"name":"unknown","total_engaged_users":0,"total_code_acceptances":0,"total_code_suggestions":11,"total_code_lines_accepted":0,"total_code_lines_suggested":21},{"name":"json","total_engaged_users":0,"total_code_acceptances":0,"total_code_suggestions":1,"total_code_lines_accepted":0,"total_code_lines_suggested":13}],"is_custom_model":false,"total_engaged_users":2}],"total_engaged_users":2}],"languages":[{"name":"java","total_engaged_users":2},{"name":"unknown","total_engaged_users":0},{"name":"json","total_engaged_users":0}],"total_engaged_users":2}}]'
        expected_csv = "date,copilot_ide_chat,,,,,,,,,total_active_users,copilot_dotcom_chat,total_engaged_users,copilot_dotcom_pull_requests,copilot_ide_code_completions,,,,,,,,,,,,,\n,total_engaged_users,editors,,,,,,,,,total_engaged_users,,total_engaged_users,editors,,,,,,,,,,,languages,,total_engaged_users\n,,name,models,,,,,,total_engaged_users,,,,,name,models,,,,,,,,,total_engaged_users,name,total_engaged_users,\n,,,name,total_chats,is_custom_model,total_engaged_users,total_chat_copy_events,total_chat_insertion_events,,,,,,,name,languages,,,,,,is_custom_model,total_engaged_users,,,,\n,,,,,,,,,,,,,,,,name,total_engaged_users,total_code_acceptances,total_code_suggestions,total_code_lines_accepted,total_code_lines_suggested,,,,,,\n2025-03-17,0,,,,,,,,,1,0,1,0,JetBrains,default,json,1,1,1,1,1,false,1,1,json,1,1\n2025-03-18,2,JetBrains,default,4,false,1,1,0,1,5,0,3,0,JetBrains,default,java,2,12,67,18,214,false,2,2,java,2,2\n,,vscode,default,4,false,1,0,0,1,,,,,,,unknown,0,0,11,0,21,,,,unknown,0,\n,,,,,,,,,,,,,,,,json,0,0,1,0,13,,,,json,0,"
        expected_markdown = "date      |copilot_ide_chat   |         |       |           |               |                   |                      |                           |                   |total_active_users|copilot_dotcom_chat|total_engaged_users|copilot_dotcom_pull_requests|copilot_ide_code_completions|       |               |                   |                      |                      |                         |                          |               |                   |                   |               |                   |                   \n          |total_engaged_users|editors  |       |           |               |                   |                      |                           |                   |                  |total_engaged_users|                   |total_engaged_users         |editors                     |       |               |                   |                      |                      |                         |                          |               |                   |                   |languages      |                   |total_engaged_users\n          |                   |name     |models |           |               |                   |                      |                           |total_engaged_users|                  |                   |                   |                            |name                        |models |               |                   |                      |                      |                         |                          |               |                   |total_engaged_users|name           |total_engaged_users|                   \n          |                   |         |name   |total_chats|is_custom_model|total_engaged_users|total_chat_copy_events|total_chat_insertion_events|                   |                  |                   |                   |                            |                            |name   |languages      |                   |                      |                      |                         |                          |is_custom_model|total_engaged_users|                   |               |                   |                   \n          |                   |         |       |           |               |                   |                      |                           |                   |                  |                   |                   |                            |                            |       |name           |total_engaged_users|total_code_acceptances|total_code_suggestions|total_code_lines_accepted|total_code_lines_suggested|               |                   |                   |               |                   |                   \n-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------\n2025-03-17|0                  |         |       |           |               |                   |                      |                           |                   |1                 |0                  |1                  |0                           |JetBrains                   |default|json           |1                  |1                     |1                     |1                        |1                         |false          |1                  |1                  |json           |1                  |1                  \n2025-03-18|2                  |JetBrains|default|4          |false          |1                  |1                     |0                          |1                  |5                 |0                  |3                  |0                           |JetBrains                   |default|java           |2                  |12                    |67                    |18                       |214                       |false          |2                  |2                  |java           |2                  |2                  \n          |                   |vscode   |default|4          |false          |1                  |0                     |0                          |1                  |                  |                   |                   |                            |                            |       |unknown        |0                  |0                     |11                    |0                        |21                        |               |                   |                   |unknown        |0                  |                   \n          |                   |         |       |           |               |                   |                      |                           |                   |                  |                   |                   |                            |                            |       |json           |0                  |0                     |1                     |0                        |13                        |               |                   |                   |json           |0                  |                   "
        expected = json_data + "\n\n\n" + expected_csv + "\n\n" + expected_markdown
        self.assert_r("""
[{"date":"2025-03-17","copilot_ide_chat":{"total_engaged_users":0},"total_active_users":1,"copilot_dotcom_chat":{"total_engaged_users":0},"total_engaged_users":1,"copilot_dotcom_pull_requests":{"total_engaged_users":0},"copilot_ide_code_completions":{"editors":[{"name":"JetBrains","models":[{"name":"default","languages":[{"name":"json","total_engaged_users":1,"total_code_acceptances":1,"total_code_suggestions":1,"total_code_lines_accepted":1,"total_code_lines_suggested":1}],"is_custom_model":false,"total_engaged_users":1}],"total_engaged_users":1}],"languages":[{"name":"json","total_engaged_users":1}],"total_engaged_users":1}},{"date":"2025-03-18","copilot_ide_chat":{"editors":[{"name":"JetBrains","models":[{"name":"default","total_chats":4,"is_custom_model":false,"total_engaged_users":1,"total_chat_copy_events":1,"total_chat_insertion_events":0}],"total_engaged_users":1},{"name":"vscode","models":[{"name":"default","total_chats":4,"is_custom_model":false,"total_engaged_users":1,"total_chat_copy_events":0,"total_chat_insertion_events":0}],"total_engaged_users":1}],"total_engaged_users":2},"total_active_users":5,"copilot_dotcom_chat":{"total_engaged_users":0},"total_engaged_users":3,"copilot_dotcom_pull_requests":{"total_engaged_users":0},"copilot_ide_code_completions":{"editors":[{"name":"JetBrains","models":[{"name":"default","languages":[{"name":"java","total_engaged_users":2,"total_code_acceptances":12,"total_code_suggestions":67,"total_code_lines_accepted":18,"total_code_lines_suggested":214},{"name":"unknown","total_engaged_users":0,"total_code_acceptances":0,"total_code_suggestions":11,"total_code_lines_accepted":0,"total_code_lines_suggested":21},{"name":"json","total_engaged_users":0,"total_code_acceptances":0,"total_code_suggestions":1,"total_code_lines_accepted":0,"total_code_lines_suggested":13}],"is_custom_model":false,"total_engaged_users":2}],"total_engaged_users":2}],"languages":[{"name":"java","total_engaged_users":2},{"name":"unknown","total_engaged_users":0},{"name":"json","total_engaged_users":0}],"total_engaged_users":2}},{"date":"2025-03-19","copilot_ide_chat":{"editors":[{"name":"JetBrains","models":[{"name":"default","total_chats":20,"is_custom_model":false,"total_engaged_users":3,"total_chat_copy_events":2,"total_chat_insertion_events":3}],"total_engaged_users":3},{"name":"vscode","models":[{"name":"default","total_chats":14,"is_custom_model":false,"total_engaged_users":1,"total_chat_copy_events":0,"total_chat_insertion_events":0}],"total_engaged_users":1}],"total_engaged_users":4},"total_active_users":5,"copilot_dotcom_chat":{"total_engaged_users":0},"total_engaged_users":5,"copilot_dotcom_pull_requests":{"total_engaged_users":0},"copilot_ide_code_completions":{"editors":[{"name":"JetBrains","models":[{"name":"default","languages":[{"name":"java","total_engaged_users":2,"total_code_acceptances":39,"total_code_suggestions":103,"total_code_lines_accepted":75,"total_code_lines_suggested":185},{"name":"unknown","total_engaged_users":1,"total_code_acceptances":15,"total_code_suggestions":24,"total_code_lines_accepted":17,"total_code_lines_suggested":41},{"name":"json","total_engaged_users":1,"total_code_acceptances":10,"total_code_suggestions":13,"total_code_lines_accepted":11,"total_code_lines_suggested":26},{"name":"yaml","total_engaged_users":1,"total_code_acceptances":3,"total_code_suggestions":4,"total_code_lines_accepted":6,"total_code_lines_suggested":10}],"is_custom_model":false,"total_engaged_users":3}],"total_engaged_users":3},{"name":"vscode","models":[{"name":"default","languages":[{"name":"typescriptreact","total_engaged_users":1,"total_code_acceptances":5,"total_code_suggestions":25,"total_code_lines_accepted":1,"total_code_lines_suggested":31},{"name":"typescript","total_engaged_users":1,"total_code_acceptances":12,"total_code_suggestions":58,"total_code_lines_accepted":9,"total_code_lines_suggested":81}],"is_custom_model":false,"total_engaged_users":1}],"total_engaged_users":1}],"languages":[{"name":"java","total_engaged_users":2},{"name":"typescriptreact","total_engaged_users":1},{"name":"unknown","total_engaged_users":1},{"name":"typescript","total_engaged_users":1},{"name":"json","total_engaged_users":1},{"name":"yaml","total_engaged_users":1}],"total_engaged_users":4}},{"date":"2025-03-20","copilot_ide_chat":{"editors":[{"name":"vscode","models":[{"name":"default","total_chats":4,"is_custom_model":false,"total_engaged_users":1,"total_chat_copy_events":0,"total_chat_insertion_events":0}],"total_engaged_users":1},{"name":"JetBrains","models":[{"name":"default","total_chats":30,"is_custom_model":false,"total_engaged_users":3,"total_chat_copy_events":5,"total_chat_insertion_events":21}],"total_engaged_users":3}],"total_engaged_users":4},"total_active_users":5,"copilot_dotcom_chat":{"total_engaged_users":0},"total_engaged_users":5,"copilot_dotcom_pull_requests":{"total_engaged_users":0},"copilot_ide_code_completions":{"editors":[{"name":"vscode","models":[{"name":"default","languages":[{"name":"typescript","total_engaged_users":1,"total_code_acceptances":23,"total_code_suggestions":86,"total_code_lines_accepted":13,"total_code_lines_suggested":118},{"name":"typescriptreact","total_engaged_users":1,"total_code_acceptances":59,"total_code_suggestions":136,"total_code_lines_accepted":54,"total_code_lines_suggested":234},{"name":"json","total_engaged_users":1,"total_code_acceptances":3,"total_code_suggestions":12,"total_code_lines_accepted":3,"total_code_lines_suggested":13}],"is_custom_model":false,"total_engaged_users":1}],"total_engaged_users":1},{"name":"JetBrains","models":[{"name":"default","languages":[{"name":"java","total_engaged_users":3,"total_code_acceptances":12,"total_code_suggestions":37,"total_code_lines_accepted":26,"total_code_lines_suggested":88},{"name":"unknown","total_engaged_users":1,"total_code_acceptances":3,"total_code_suggestions":13,"total_code_lines_accepted":4,"total_code_lines_suggested":28}],"is_custom_model":false,"total_engaged_users":3}],"total_engaged_users":3}],"languages":[{"name":"typescript","total_engaged_users":1},{"name":"java","total_engaged_users":3},{"name":"typescriptreact","total_engaged_users":1},{"name":"unknown","total_engaged_users":1},{"name":"json","total_engaged_users":1}],"total_engaged_users":4}},{"date":"2025-03-21","copilot_ide_chat":{"editors":[{"name":"vscode","models":[{"name":"default","total_chats":21,"is_custom_model":false,"total_engaged_users":2,"total_chat_copy_events":12,"total_chat_insertion_events":0}],"total_engaged_users":2},{"name":"JetBrains","models":[{"name":"default","total_chats":12,"is_custom_model":false,"total_engaged_users":3,"total_chat_copy_events":0,"total_chat_insertion_events":13}],"total_engaged_users":3}],"total_engaged_users":5},"total_active_users":6,"copilot_dotcom_chat":{"total_engaged_users":0},"total_engaged_users":6,"copilot_dotcom_pull_requests":{"total_engaged_users":0},"copilot_ide_code_completions":{"editors":[{"name":"vscode","models":[{"name":"default","languages":[{"name":"typescript","total_engaged_users":1,"total_code_acceptances":59,"total_code_suggestions":238,"total_code_lines_accepted":49,"total_code_lines_suggested":385},{"name":"typescriptreact","total_engaged_users":2,"total_code_acceptances":89,"total_code_suggestions":243,"total_code_lines_accepted":108,"total_code_lines_suggested":491},{"name":"json","total_engaged_users":0,"total_code_acceptances":0,"total_code_suggestions":1,"total_code_lines_accepted":0,"total_code_lines_suggested":1}],"is_custom_model":false,"total_engaged_users":2}],"total_engaged_users":2},{"name":"JetBrains","models":[{"name":"default","languages":[{"name":"java","total_engaged_users":2,"total_code_acceptances":10,"total_code_suggestions":39,"total_code_lines_accepted":15,"total_code_lines_suggested":85},{"name":"unknown","total_engaged_users":2,"total_code_acceptances":45,"total_code_suggestions":92,"total_code_lines_accepted":48,"total_code_lines_suggested":129},{"name":"json","total_engaged_users":2,"total_code_acceptances":5,"total_code_suggestions":12,"total_code_lines_accepted":5,"total_code_lines_suggested":26},{"name":"yaml","total_engaged_users":0,"total_code_acceptances":0,"total_code_suggestions":4,"total_code_lines_accepted":0,"total_code_lines_suggested":4}],"is_custom_model":false,"total_engaged_users":4}],"total_engaged_users":4}],"languages":[{"name":"typescript","total_engaged_users":1},{"name":"typescriptreact","total_engaged_users":2},{"name":"java","total_engaged_users":2},{"name":"unknown","total_engaged_users":2},{"name":"json","total_engaged_users":2},{"name":"yaml","total_engaged_users":0}],"total_engaged_users":6}},{"date":"2025-03-23","copilot_ide_chat":{"editors":[{"name":"vscode","models":[{"name":"default","total_chats":13,"is_custom_model":false,"total_engaged_users":1,"total_chat_copy_events":0,"total_chat_insertion_events":0}],"total_engaged_users":1}],"total_engaged_users":1},"total_active_users":1,"copilot_dotcom_chat":{"total_engaged_users":0},"total_engaged_users":1,"copilot_dotcom_pull_requests":{"total_engaged_users":0},"copilot_ide_code_completions":{"editors":[{"name":"vscode","models":[{"name":"default","languages":[{"name":"typescriptreact","total_engaged_users":1,"total_code_acceptances":54,"total_code_suggestions":100,"total_code_lines_accepted":47,"total_code_lines_suggested":192}],"is_custom_model":false,"total_engaged_users":1}],"total_engaged_users":1}],"languages":[{"name":"typescriptreact","total_engaged_users":1}],"total_engaged_users":1}},{"date":"2025-03-24","copilot_ide_chat":{"editors":[{"name":"JetBrains","models":[{"name":"default","total_chats":16,"is_custom_model":false,"total_engaged_users":5,"total_chat_copy_events":15,"total_chat_insertion_events":10}],"total_engaged_users":5},{"name":"vscode","models":[{"name":"default","total_chats":12,"is_custom_model":false,"total_engaged_users":1,"total_chat_copy_events":0,"total_chat_insertion_events":0}],"total_engaged_users":1}],"total_engaged_users":6},"total_active_users":7,"copilot_dotcom_chat":{"total_engaged_users":0},"total_engaged_users":7,"copilot_dotcom_pull_requests":{"total_engaged_users":0},"copilot_ide_code_completions":{"editors":[{"name":"JetBrains","models":[{"name":"default","languages":[{"name":"unknown","total_engaged_users":1,"total_code_acceptances":35,"total_code_suggestions":79,"total_code_lines_accepted":43,"total_code_lines_suggested":144},{"name":"json","total_engaged_users":0,"total_code_acceptances":0,"total_code_suggestions":2,"total_code_lines_accepted":0,"total_code_lines_suggested":4},{"name":"java","total_engaged_users":2,"total_code_acceptances":3,"total_code_suggestions":17,"total_code_lines_accepted":3,"total_code_lines_suggested":24},{"name":"markdown","total_engaged_users":0,"total_code_acceptances":0,"total_code_suggestions":1,"total_code_lines_accepted":0,"total_code_lines_suggested":1},{"name":"xml","total_engaged_users":1,"total_code_acceptances":1,"total_code_suggestions":4,"total_code_lines_accepted":1,"total_code_lines_suggested":5}],"is_custom_model":false,"total_engaged_users":2}],"total_engaged_users":2},{"name":"vscode","models":[{"name":"default","languages":[{"name":"typescript","total_engaged_users":2,"total_code_acceptances":34,"total_code_suggestions":156,"total_code_lines_accepted":12,"total_code_lines_suggested":218},{"name":"typescriptreact","total_engaged_users":2,"total_code_acceptances":61,"total_code_suggestions":205,"total_code_lines_accepted":70,"total_code_lines_suggested":396}],"is_custom_model":false,"total_engaged_users":2}],"total_engaged_users":2}],"languages":[{"name":"unknown","total_engaged_users":1},{"name":"typescript","total_engaged_users":2},{"name":"typescriptreact","total_engaged_users":2},{"name":"json","total_engaged_users":0},{"name":"java","total_engaged_users":2},{"name":"markdown","total_engaged_users":0},{"name":"xml","total_engaged_users":1}],"total_engaged_users":4}},{"date":"2025-03-25","copilot_ide_chat":{"editors":[{"name":"vscode","models":[{"name":"default","total_chats":20,"is_custom_model":false,"total_engaged_users":2,"total_chat_copy_events":2,"total_chat_insertion_events":0}],"total_engaged_users":2},{"name":"JetBrains","models":[{"name":"default","total_chats":27,"is_custom_model":false,"total_engaged_users":4,"total_chat_copy_events":10,"total_chat_insertion_events":10}],"total_engaged_users":4}],"total_engaged_users":6},"total_active_users":7,"copilot_dotcom_chat":{"total_engaged_users":0},"total_engaged_users":7,"copilot_dotcom_pull_requests":{"total_engaged_users":0},"copilot_ide_code_completions":{"editors":[{"name":"JetBrains","models":[{"name":"default","languages":[{"name":"java","total_engaged_users":5,"total_code_acceptances":47,"total_code_suggestions":145,"total_code_lines_accepted":96,"total_code_lines_suggested":363},{"name":"unknown","total_engaged_users":1,"total_code_acceptances":9,"total_code_suggestions":23,"total_code_lines_accepted":9,"total_code_lines_suggested":43},{"name":"json","total_engaged_users":1,"total_code_acceptances":1,"total_code_suggestions":2,"total_code_lines_accepted":1,"total_code_lines_suggested":4}],"is_custom_model":false,"total_engaged_users":5}],"total_engaged_users":5},{"name":"vscode","models":[{"name":"default","languages":[{"name":"typescriptreact","total_engaged_users":2,"total_code_acceptances":78,"total_code_suggestions":225,"total_code_lines_accepted":128,"total_code_lines_suggested":491},{"name":"typescript","total_engaged_users":2,"total_code_acceptances":40,"total_code_suggestions":126,"total_code_lines_accepted":39,"total_code_lines_suggested":154}],"is_custom_model":false,"total_engaged_users":2}],"total_engaged_users":2}],"languages":[{"name":"typescriptreact","total_engaged_users":2},{"name":"java","total_engaged_users":5},{"name":"typescript","total_engaged_users":2},{"name":"unknown","total_engaged_users":1},{"name":"json","total_engaged_users":1}],"total_engaged_users":7}},{"date":"2025-03-26","copilot_ide_chat":{"editors":[{"name":"vscode","models":[{"name":"default","total_chats":14,"is_custom_model":false,"total_engaged_users":2,"total_chat_copy_events":2,"total_chat_insertion_events":0}],"total_engaged_users":2},{"name":"JetBrains","models":[{"name":"default","total_chats":19,"is_custom_model":false,"total_engaged_users":2,"total_chat_copy_events":8,"total_chat_insertion_events":5}],"total_engaged_users":2}],"total_engaged_users":4},"total_active_users":7,"copilot_dotcom_chat":{"total_engaged_users":0},"total_engaged_users":6,"copilot_dotcom_pull_requests":{"total_engaged_users":0},"copilot_ide_code_completions":{"editors":[{"name":"vscode","models":[{"name":"default","languages":[{"name":"typescript","total_engaged_users":3,"total_code_acceptances":220,"total_code_suggestions":421,"total_code_lines_accepted":275,"total_code_lines_suggested":733},{"name":"typescriptreact","total_engaged_users":2,"total_code_acceptances":151,"total_code_suggestions":392,"total_code_lines_accepted":157,"total_code_lines_suggested":582},{"name":"unknown","total_engaged_users":1,"total_code_acceptances":2,"total_code_suggestions":20,"total_code_lines_accepted":14,"total_code_lines_suggested":167}],"is_custom_model":false,"total_engaged_users":3}],"total_engaged_users":3},{"name":"JetBrains","models":[{"name":"default","languages":[{"name":"java","total_engaged_users":1,"total_code_acceptances":11,"total_code_suggestions":39,"total_code_lines_accepted":92,"total_code_lines_suggested":237},{"name":"xml","total_engaged_users":1,"total_code_acceptances":1,"total_code_suggestions":9,"total_code_lines_accepted":1,"total_code_lines_suggested":9},{"name":"json","total_engaged_users":0,"total_code_acceptances":0,"total_code_suggestions":2,"total_code_lines_accepted":0,"total_code_lines_suggested":2}],"is_custom_model":false,"total_engaged_users":2}],"total_engaged_users":2}],"languages":[{"name":"typescript","total_engaged_users":3},{"name":"java","total_engaged_users":1},{"name":"typescriptreact","total_engaged_users":2},{"name":"xml","total_engaged_users":1},{"name":"unknown","total_engaged_users":1},{"name":"json","total_engaged_users":0}],"total_engaged_users":5}},{"date":"2025-03-27","copilot_ide_chat":{"editors":[{"name":"vscode","models":[{"name":"default","total_chats":26,"is_custom_model":false,"total_engaged_users":2,"total_chat_copy_events":0,"total_chat_insertion_events":0}],"total_engaged_users":2},{"name":"JetBrains","models":[{"name":"default","total_chats":25,"is_custom_model":false,"total_engaged_users":3,"total_chat_copy_events":11,"total_chat_insertion_events":9}],"total_engaged_users":3}],"total_engaged_users":5},"total_active_users":7,"copilot_dotcom_chat":{"total_engaged_users":0},"total_engaged_users":7,"copilot_dotcom_pull_requests":{"total_engaged_users":0},"copilot_ide_code_completions":{"editors":[{"name":"JetBrains","models":[{"name":"default","languages":[{"name":"unknown","total_engaged_users":2,"total_code_acceptances":38,"total_code_suggestions":77,"total_code_lines_accepted":50,"total_code_lines_suggested":110},{"name":"java","total_engaged_users":3,"total_code_acceptances":45,"total_code_suggestions":156,"total_code_lines_accepted":123,"total_code_lines_suggested":509}],"is_custom_model":false,"total_engaged_users":4}],"total_engaged_users":4},{"name":"vscode","models":[{"name":"default","languages":[{"name":"typescriptreact","total_engaged_users":2,"total_code_acceptances":26,"total_code_suggestions":87,"total_code_lines_accepted":28,"total_code_lines_suggested":131},{"name":"unknown","total_engaged_users":1,"total_code_acceptances":2,"total_code_suggestions":42,"total_code_lines_accepted":2,"total_code_lines_suggested":99},{"name":"typescript","total_engaged_users":3,"total_code_acceptances":16,"total_code_suggestions":62,"total_code_lines_accepted":12,"total_code_lines_suggested":83}],"is_custom_model":false,"total_engaged_users":3}],"total_engaged_users":3}],"languages":[{"name":"unknown","total_engaged_users":3},{"name":"java","total_engaged_users":3},{"name":"typescriptreact","total_engaged_users":2},{"name":"typescript","total_engaged_users":3}],"total_engaged_users":7}},{"date":"2025-03-28","copilot_ide_chat":{"editors":[{"name":"vscode","models":[{"name":"default","total_chats":7,"is_custom_model":false,"total_engaged_users":2,"total_chat_copy_events":0,"total_chat_insertion_events":0}],"total_engaged_users":2},{"name":"JetBrains","models":[{"name":"default","total_chats":18,"is_custom_model":false,"total_engaged_users":2,"total_chat_copy_events":2,"total_chat_insertion_events":18}],"total_engaged_users":2}],"total_engaged_users":4},"total_active_users":6,"copilot_dotcom_chat":{"total_engaged_users":0},"total_engaged_users":6,"copilot_dotcom_pull_requests":{"total_engaged_users":0},"copilot_ide_code_completions":{"editors":[{"name":"JetBrains","models":[{"name":"default","languages":[{"name":"java","total_engaged_users":2,"total_code_acceptances":35,"total_code_suggestions":132,"total_code_lines_accepted":91,"total_code_lines_suggested":449},{"name":"unknown","total_engaged_users":2,"total_code_acceptances":8,"total_code_suggestions":20,"total_code_lines_accepted":8,"total_code_lines_suggested":22},{"name":"json","total_engaged_users":1,"total_code_acceptances":2,"total_code_suggestions":2,"total_code_lines_accepted":2,"total_code_lines_suggested":2}],"is_custom_model":false,"total_engaged_users":4}],"total_engaged_users":4},{"name":"vscode","models":[{"name":"default","languages":[{"name":"feature","total_engaged_users":1,"total_code_acceptances":2,"total_code_suggestions":14,"total_code_lines_accepted":2,"total_code_lines_suggested":27},{"name":"typescript","total_engaged_users":1,"total_code_acceptances":6,"total_code_suggestions":22,"total_code_lines_accepted":5,"total_code_lines_suggested":30}],"is_custom_model":false,"total_engaged_users":1}],"total_engaged_users":1}],"languages":[{"name":"java","total_engaged_users":2},{"name":"unknown","total_engaged_users":2},{"name":"feature","total_engaged_users":1},{"name":"typescript","total_engaged_users":1},{"name":"json","total_engaged_users":1}],"total_engaged_users":5}},{"date":"2025-03-31","copilot_ide_chat":{"editors":[{"name":"vscode","models":[{"name":"default","total_chats":8,"is_custom_model":false,"total_engaged_users":2,"total_chat_copy_events":0,"total_chat_insertion_events":0}],"total_engaged_users":2},{"name":"JetBrains","models":[{"name":"default","total_chats":16,"is_custom_model":false,"total_engaged_users":4,"total_chat_copy_events":5,"total_chat_insertion_events":13}],"total_engaged_users":4}],"total_engaged_users":6},"total_active_users":7,"copilot_dotcom_chat":{"total_engaged_users":0},"total_engaged_users":7,"copilot_dotcom_pull_requests":{"total_engaged_users":0},"copilot_ide_code_completions":{"editors":[{"name":"vscode","models":[{"name":"default","languages":[{"name":"typescript","total_engaged_users":2,"total_code_acceptances":72,"total_code_suggestions":153,"total_code_lines_accepted":64,"total_code_lines_suggested":185},{"name":"feature","total_engaged_users":0,"total_code_acceptances":0,"total_code_suggestions":10,"total_code_lines_accepted":0,"total_code_lines_suggested":32},{"name":"csv","total_engaged_users":0,"total_code_acceptances":0,"total_code_suggestions":3,"total_code_lines_accepted":0,"total_code_lines_suggested":5},{"name":"json","total_engaged_users":0,"total_code_acceptances":0,"total_code_suggestions":3,"total_code_lines_accepted":0,"total_code_lines_suggested":4}],"is_custom_model":false,"total_engaged_users":2}],"total_engaged_users":2},{"name":"JetBrains","models":[{"name":"default","languages":[{"name":"java","total_engaged_users":4,"total_code_acceptances":41,"total_code_suggestions":168,"total_code_lines_accepted":95,"total_code_lines_suggested":460},{"name":"unknown","total_engaged_users":1,"total_code_acceptances":2,"total_code_suggestions":9,"total_code_lines_accepted":2,"total_code_lines_suggested":10},{"name":"json","total_engaged_users":0,"total_code_acceptances":0,"total_code_suggestions":1,"total_code_lines_accepted":0,"total_code_lines_suggested":1}],"is_custom_model":false,"total_engaged_users":4}],"total_engaged_users":4}],"languages":[{"name":"typescript","total_engaged_users":2},{"name":"java","total_engaged_users":4},{"name":"feature","total_engaged_users":0},{"name":"unknown","total_engaged_users":1},{"name":"csv","total_engaged_users":0},{"name":"json","total_engaged_users":0}],"total_engaged_users":6}},{"date":"2025-04-01","copilot_ide_chat":{"editors":[{"name":"JetBrains","models":[{"name":"default","total_chats":20,"is_custom_model":false,"total_engaged_users":2,"total_chat_copy_events":4,"total_chat_insertion_events":21}],"total_engaged_users":2},{"name":"vscode","models":[{"name":"default","total_chats":10,"is_custom_model":false,"total_engaged_users":1,"total_chat_copy_events":0,"total_chat_insertion_events":0}],"total_engaged_users":1}],"total_engaged_users":3},"total_active_users":6,"copilot_dotcom_chat":{"total_engaged_users":0},"total_engaged_users":6,"copilot_dotcom_pull_requests":{"total_engaged_users":0},"copilot_ide_code_completions":{"editors":[{"name":"vscode","models":[{"name":"default","languages":[{"name":"typescript","total_engaged_users":2,"total_code_acceptances":101,"total_code_suggestions":231,"total_code_lines_accepted":92,"total_code_lines_suggested":313},{"name":"feature","total_engaged_users":1,"total_code_acceptances":2,"total_code_suggestions":21,"total_code_lines_accepted":0,"total_code_lines_suggested":74},{"name":"csv","total_engaged_users":1,"total_code_acceptances":1,"total_code_suggestions":3,"total_code_lines_accepted":1,"total_code_lines_suggested":3}],"is_custom_model":false,"total_engaged_users":2}],"total_engaged_users":2},{"name":"JetBrains","models":[{"name":"default","languages":[{"name":"java","total_engaged_users":3,"total_code_acceptances":53,"total_code_suggestions":273,"total_code_lines_accepted":86,"total_code_lines_suggested":912},{"name":"unknown","total_engaged_users":2,"total_code_acceptances":3,"total_code_suggestions":7,"total_code_lines_accepted":3,"total_code_lines_suggested":11},{"name":"json","total_engaged_users":0,"total_code_acceptances":0,"total_code_suggestions":3,"total_code_lines_accepted":0,"total_code_lines_suggested":4}],"is_custom_model":false,"total_engaged_users":3}],"total_engaged_users":3}],"languages":[{"name":"typescript","total_engaged_users":2},{"name":"java","total_engaged_users":3},{"name":"feature","total_engaged_users":1},{"name":"unknown","total_engaged_users":2},{"name":"json","total_engaged_users":0},{"name":"csv","total_engaged_users":1}],"total_engaged_users":5}},{"date":"2025-04-02","copilot_ide_chat":{"editors":[{"name":"vscode","models":[{"name":"default","total_chats":51,"is_custom_model":false,"total_engaged_users":6,"total_chat_copy_events":12,"total_chat_insertion_events":0}],"total_engaged_users":6},{"name":"JetBrains","models":[{"name":"default","total_chats":11,"is_custom_model":false,"total_engaged_users":3,"total_chat_copy_events":9,"total_chat_insertion_events":1}],"total_engaged_users":3}],"total_engaged_users":9},"total_active_users":9,"copilot_dotcom_chat":{"total_engaged_users":0},"total_engaged_users":9,"copilot_dotcom_pull_requests":{"total_engaged_users":0},"copilot_ide_code_completions":{"editors":[{"name":"vscode","models":[{"name":"default","languages":[{"name":"typescript","total_engaged_users":2,"total_code_acceptances":96,"total_code_suggestions":221,"total_code_lines_accepted":103,"total_code_lines_suggested":332},{"name":"typescriptreact","total_engaged_users":1,"total_code_acceptances":14,"total_code_suggestions":57,"total_code_lines_accepted":16,"total_code_lines_suggested":127},{"name":"feature","total_engaged_users":1,"total_code_acceptances":1,"total_code_suggestions":25,"total_code_lines_accepted":2,"total_code_lines_suggested":70},{"name":"json","total_engaged_users":0,"total_code_acceptances":0,"total_code_suggestions":7,"total_code_lines_accepted":0,"total_code_lines_suggested":9},{"name":"java","total_engaged_users":1,"total_code_acceptances":1,"total_code_suggestions":5,"total_code_lines_accepted":0,"total_code_lines_suggested":7}],"is_custom_model":false,"total_engaged_users":4}],"total_engaged_users":4},{"name":"JetBrains","models":[{"name":"default","languages":[{"name":"java","total_engaged_users":3,"total_code_acceptances":54,"total_code_suggestions":244,"total_code_lines_accepted":89,"total_code_lines_suggested":626},{"name":"yaml","total_engaged_users":1,"total_code_acceptances":5,"total_code_suggestions":6,"total_code_lines_accepted":17,"total_code_lines_suggested":18},{"name":"unknown","total_engaged_users":1,"total_code_acceptances":3,"total_code_suggestions":7,"total_code_lines_accepted":3,"total_code_lines_suggested":7},{"name":"json","total_engaged_users":0,"total_code_acceptances":0,"total_code_suggestions":1,"total_code_lines_accepted":0,"total_code_lines_suggested":2}],"is_custom_model":false,"total_engaged_users":4}],"total_engaged_users":4}],"languages":[{"name":"typescript","total_engaged_users":2},{"name":"java","total_engaged_users":4},{"name":"typescriptreact","total_engaged_users":1},{"name":"feature","total_engaged_users":1},{"name":"yaml","total_engaged_users":1},{"name":"json","total_engaged_users":0},{"name":"unknown","total_engaged_users":1}],"total_engaged_users":7}},{"date":"2025-04-03","copilot_ide_chat":{"editors":[{"name":"JetBrains","models":[{"name":"default","total_chats":18,"is_custom_model":false,"total_engaged_users":4,"total_chat_copy_events":5,"total_chat_insertion_events":6}],"total_engaged_users":4},{"name":"vscode","models":[{"name":"default","total_chats":52,"is_custom_model":false,"total_engaged_users":4,"total_chat_copy_events":6,"total_chat_insertion_events":1}],"total_engaged_users":4}],"total_engaged_users":8},"total_active_users":8,"copilot_dotcom_chat":{"total_engaged_users":0},"total_engaged_users":8,"copilot_dotcom_pull_requests":{"total_engaged_users":0},"copilot_ide_code_completions":{"editors":[{"name":"vscode","models":[{"name":"default","languages":[{"name":"typescript","total_engaged_users":3,"total_code_acceptances":108,"total_code_suggestions":250,"total_code_lines_accepted":170,"total_code_lines_suggested":418},{"name":"typescriptreact","total_engaged_users":2,"total_code_acceptances":37,"total_code_suggestions":165,"total_code_lines_accepted":33,"total_code_lines_suggested":303},{"name":"feature","total_engaged_users":1,"total_code_acceptances":1,"total_code_suggestions":22,"total_code_lines_accepted":1,"total_code_lines_suggested":38},{"name":"dotenv","total_engaged_users":0,"total_code_acceptances":0,"total_code_suggestions":2,"total_code_lines_accepted":0,"total_code_lines_suggested":2}],"is_custom_model":false,"total_engaged_users":3}],"total_engaged_users":3},{"name":"JetBrains","models":[{"name":"default","languages":[{"name":"java","total_engaged_users":3,"total_code_acceptances":26,"total_code_suggestions":111,"total_code_lines_accepted":37,"total_code_lines_suggested":210},{"name":"unknown","total_engaged_users":1,"total_code_acceptances":1,"total_code_suggestions":18,"total_code_lines_accepted":1,"total_code_lines_suggested":58}],"is_custom_model":false,"total_engaged_users":3}],"total_engaged_users":3}],"languages":[{"name":"typescript","total_engaged_users":3},{"name":"java","total_engaged_users":3},{"name":"typescriptreact","total_engaged_users":2},{"name":"feature","total_engaged_users":1},{"name":"unknown","total_engaged_users":1},{"name":"dotenv","total_engaged_users":0}],"total_engaged_users":6}}]


date,copilot_ide_chat,,,,,,,,,total_active_users,copilot_dotcom_chat,total_engaged_users,copilot_dotcom_pull_requests,copilot_ide_code_completions,,,,,,,,,,,,,
,total_engaged_users,editors,,,,,,,,,total_engaged_users,,total_engaged_users,editors,,,,,,,,,,,languages,,total_engaged_users
,,name,models,,,,,,total_engaged_users,,,,,name,models,,,,,,,,,total_engaged_users,name,total_engaged_users,
,,,name,total_chats,is_custom_model,total_engaged_users,total_chat_copy_events,total_chat_insertion_events,,,,,,,name,languages,,,,,,is_custom_model,total_engaged_users,,,,
,,,,,,,,,,,,,,,,name,total_engaged_users,total_code_acceptances,total_code_suggestions,total_code_lines_accepted,total_code_lines_suggested,,,,,,
2025-03-17,0,,,,,,,,,1,0,1,0,JetBrains,default,json,1,1,1,1,1,false,1,1,json,1,1
2025-03-18,2,JetBrains,default,4,false,1,1,0,1,5,0,3,0,JetBrains,default,java,2,12,67,18,214,false,2,2,java,2,2
,,vscode,default,4,false,1,0,0,1,,,,,,,unknown,0,0,11,0,21,,,,unknown,0,
,,,,,,,,,,,,,,,,json,0,0,1,0,13,,,,json,0,
2025-03-19,4,JetBrains,default,20,false,3,2,3,3,5,0,5,0,JetBrains,default,java,2,39,103,75,185,false,3,3,java,2,4
,,vscode,default,14,false,1,0,0,1,,,,,vscode,default,typescriptreact,1,5,25,1,31,,,,typescriptreact,1,
,,,,,,,,,,,,,,,,typescript,1,12,58,9,81,false,1,1,unknown,1,
,,,,,,,,,,,,,,,,yaml,1,3,4,6,10,,,,typescript,1,
,,,,,,,,,,,,,,,,,,,,,,,,,json,1,
,,,,,,,,,,,,,,,,,,,,,,,,,yaml,1,
2025-03-20,4,vscode,default,4,false,1,0,0,1,5,0,5,0,vscode,default,typescript,1,23,86,13,118,false,1,1,typescript,1,4
,,JetBrains,default,30,false,3,5,21,3,,,,,JetBrains,default,java,3,12,37,26,88,,,,java,3,
,,,,,,,,,,,,,,,,unknown,1,3,13,4,28,false,3,3,typescriptreact,1,
,,,,,,,,,,,,,,,,,,,,,,,,,unknown,1,
,,,,,,,,,,,,,,,,,,,,,,,,,json,1,
2025-03-21,5,vscode,default,21,false,2,12,0,2,6,0,6,0,vscode,default,typescript,1,59,238,49,385,false,2,2,typescript,1,6
,,JetBrains,default,12,false,3,0,13,3,,,,,JetBrains,default,java,2,10,39,15,85,,,,typescriptreact,2,
,,,,,,,,,,,,,,,,unknown,2,45,92,48,129,,,,java,2,
,,,,,,,,,,,,,,,,json,2,5,12,5,26,,,,unknown,2,
,,,,,,,,,,,,,,,,yaml,0,0,4,0,4,false,4,4,json,2,
,,,,,,,,,,,,,,,,,,,,,,,,,yaml,0,
2025-03-23,1,vscode,default,13,false,1,0,0,1,1,0,1,0,vscode,default,typescriptreact,1,54,100,47,192,false,1,1,typescriptreact,1,1
2025-03-24,6,JetBrains,default,16,false,5,15,10,5,7,0,7,0,JetBrains,default,unknown,1,35,79,43,144,false,2,2,unknown,1,4
,,vscode,default,12,false,1,0,0,1,,,,,vscode,default,typescript,2,34,156,12,218,,,,typescript,2,
,,,,,,,,,,,,,,,,typescriptreact,2,61,205,70,396,false,2,2,typescriptreact,2,
,,,,,,,,,,,,,,,,markdown,0,0,1,0,1,,,,json,0,
,,,,,,,,,,,,,,,,xml,1,1,4,1,5,,,,java,2,
,,,,,,,,,,,,,,,,,,,,,,,,,markdown,0,
,,,,,,,,,,,,,,,,,,,,,,,,,xml,1,
2025-03-25,6,vscode,default,20,false,2,2,0,2,7,0,7,0,JetBrains,default,java,5,47,145,96,363,false,5,5,typescriptreact,2,7
,,JetBrains,default,27,false,4,10,10,4,,,,,vscode,default,typescriptreact,2,78,225,128,491,,,,java,5,
,,,,,,,,,,,,,,,,typescript,2,40,126,39,154,false,2,2,typescript,2,
,,,,,,,,,,,,,,,,,,,,,,,,,unknown,1,
,,,,,,,,,,,,,,,,,,,,,,,,,json,1,
2025-03-26,4,vscode,default,14,false,2,2,0,2,7,0,6,0,vscode,default,typescript,3,220,421,275,733,false,3,3,typescript,3,5
,,JetBrains,default,19,false,2,8,5,2,,,,,JetBrains,default,java,1,11,39,92,237,,,,java,1,
,,,,,,,,,,,,,,,,xml,1,1,9,1,9,,,,typescriptreact,2,
,,,,,,,,,,,,,,,,json,0,0,2,0,2,false,2,2,xml,1,
,,,,,,,,,,,,,,,,,,,,,,,,,unknown,1,
,,,,,,,,,,,,,,,,,,,,,,,,,json,0,
2025-03-27,5,vscode,default,26,false,2,0,0,2,7,0,7,0,JetBrains,default,unknown,2,38,77,50,110,false,4,4,unknown,3,7
,,JetBrains,default,25,false,3,11,9,3,,,,,vscode,default,typescriptreact,2,26,87,28,131,,,,java,3,
,,,,,,,,,,,,,,,,unknown,1,2,42,2,99,,,,typescriptreact,2,
,,,,,,,,,,,,,,,,typescript,3,16,62,12,83,false,3,3,typescript,3,
2025-03-28,4,vscode,default,7,false,2,0,0,2,6,0,6,0,JetBrains,default,java,2,35,132,91,449,false,4,4,java,2,5
,,JetBrains,default,18,false,2,2,18,2,,,,,vscode,default,feature,1,2,14,2,27,,,,unknown,2,
,,,,,,,,,,,,,,,,typescript,1,6,22,5,30,false,1,1,feature,1,
,,,,,,,,,,,,,,,,,,,,,,,,,typescript,1,
,,,,,,,,,,,,,,,,,,,,,,,,,json,1,
2025-03-31,6,vscode,default,8,false,2,0,0,2,7,0,7,0,vscode,default,typescript,2,72,153,64,185,false,2,2,typescript,2,6
,,JetBrains,default,16,false,4,5,13,4,,,,,JetBrains,default,java,4,41,168,95,460,,,,java,4,
,,,,,,,,,,,,,,,,unknown,1,2,9,2,10,,,,feature,0,
,,,,,,,,,,,,,,,,json,0,0,1,0,1,false,4,4,unknown,1,
,,,,,,,,,,,,,,,,,,,,,,,,,csv,0,
,,,,,,,,,,,,,,,,,,,,,,,,,json,0,
2025-04-01,3,JetBrains,default,20,false,2,4,21,2,6,0,6,0,vscode,default,typescript,2,101,231,92,313,false,2,2,typescript,2,5
,,vscode,default,10,false,1,0,0,1,,,,,JetBrains,default,java,3,53,273,86,912,,,,java,3,
,,,,,,,,,,,,,,,,unknown,2,3,7,3,11,,,,feature,1,
,,,,,,,,,,,,,,,,json,0,0,3,0,4,false,3,3,unknown,2,
,,,,,,,,,,,,,,,,,,,,,,,,,json,0,
,,,,,,,,,,,,,,,,,,,,,,,,,csv,1,
2025-04-02,9,vscode,default,51,false,6,12,0,6,9,0,9,0,vscode,default,typescript,2,96,221,103,332,false,4,4,typescript,2,7
,,JetBrains,default,11,false,3,9,1,3,,,,,JetBrains,default,java,3,54,244,89,626,,,,java,4,
,,,,,,,,,,,,,,,,yaml,1,5,6,17,18,,,,typescriptreact,1,
,,,,,,,,,,,,,,,,unknown,1,3,7,3,7,,,,feature,1,
,,,,,,,,,,,,,,,,json,0,0,1,0,2,false,4,4,yaml,1,
,,,,,,,,,,,,,,,,,,,,,,,,,json,0,
,,,,,,,,,,,,,,,,,,,,,,,,,unknown,1,
2025-04-03,8,JetBrains,default,18,false,4,5,6,4,8,0,8,0,vscode,default,typescript,3,108,250,170,418,false,3,3,typescript,3,6
,,vscode,default,52,false,4,6,1,4,,,,,JetBrains,default,java,3,26,111,37,210,,,,java,3,
,,,,,,,,,,,,,,,,unknown,1,1,18,1,58,false,3,3,typescriptreact,2,
,,,,,,,,,,,,,,,,dotenv,0,0,2,0,2,,,,feature,1,
,,,,,,,,,,,,,,,,,,,,,,,,,unknown,1,
,,,,,,,,,,,,,,,,,,,,,,,,,dotenv,0,


date      |copilot_ide_chat   |         |       |           |               |                   |                      |                           |                   |total_active_users|copilot_dotcom_chat|total_engaged_users|copilot_dotcom_pull_requests|copilot_ide_code_completions|       |               |                   |                      |                      |                         |                          |               |                   |                   |               |                   |                   
          |total_engaged_users|editors  |       |           |               |                   |                      |                           |                   |                  |total_engaged_users|                   |total_engaged_users         |editors                     |       |               |                   |                      |                      |                         |                          |               |                   |                   |languages      |                   |total_engaged_users
          |                   |name     |models |           |               |                   |                      |                           |total_engaged_users|                  |                   |                   |                            |name                        |models |               |                   |                      |                      |                         |                          |               |                   |total_engaged_users|name           |total_engaged_users|                   
          |                   |         |name   |total_chats|is_custom_model|total_engaged_users|total_chat_copy_events|total_chat_insertion_events|                   |                  |                   |                   |                            |                            |name   |languages      |                   |                      |                      |                         |                          |is_custom_model|total_engaged_users|                   |               |                   |                   
          |                   |         |       |           |               |                   |                      |                           |                   |                  |                   |                   |                            |                            |       |name           |total_engaged_users|total_code_acceptances|total_code_suggestions|total_code_lines_accepted|total_code_lines_suggested|               |                   |                   |               |                   |                   
-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
2025-03-17|0                  |         |       |           |               |                   |                      |                           |                   |1                 |0                  |1                  |0                           |JetBrains                   |default|json           |1                  |1                     |1                     |1                        |1                         |false          |1                  |1                  |json           |1                  |1                  
2025-03-18|2                  |JetBrains|default|4          |false          |1                  |1                     |0                          |1                  |5                 |0                  |3                  |0                           |JetBrains                   |default|java           |2                  |12                    |67                    |18                       |214                       |false          |2                  |2                  |java           |2                  |2                  
          |                   |vscode   |default|4          |false          |1                  |0                     |0                          |1                  |                  |                   |                   |                            |                            |       |unknown        |0                  |0                     |11                    |0                        |21                        |               |                   |                   |unknown        |0                  |                   
          |                   |         |       |           |               |                   |                      |                           |                   |                  |                   |                   |                            |                            |       |json           |0                  |0                     |1                     |0                        |13                        |               |                   |                   |json           |0                  |                   
2025-03-19|4                  |JetBrains|default|20         |false          |3                  |2                     |3                          |3                  |5                 |0                  |5                  |0                           |JetBrains                   |default|java           |2                  |39                    |103                   |75                       |185                       |false          |3                  |3                  |java           |2                  |4                  
          |                   |vscode   |default|14         |false          |1                  |0                     |0                          |1                  |                  |                   |                   |                            |vscode                      |default|typescriptreact|1                  |5                     |25                    |1                        |31                        |               |                   |                   |typescriptreact|1                  |                   
          |                   |         |       |           |               |                   |                      |                           |                   |                  |                   |                   |                            |                            |       |typescript     |1                  |12                    |58                    |9                        |81                        |false          |1                  |1                  |unknown        |1                  |                   
          |                   |         |       |           |               |                   |                      |                           |                   |                  |                   |                   |                            |                            |       |yaml           |1                  |3                     |4                     |6                        |10                        |               |                   |                   |typescript     |1                  |                   
          |                   |         |       |           |               |                   |                      |                           |                   |                  |                   |                   |                            |                            |       |               |                   |                      |                      |                         |                          |               |                   |                   |json           |1                  |                   
          |                   |         |       |           |               |                   |                      |                           |                   |                  |                   |                   |                            |                            |       |               |                   |                      |                      |                         |                          |               |                   |                   |yaml           |1                  |                   
2025-03-20|4                  |vscode   |default|4          |false          |1                  |0                     |0                          |1                  |5                 |0                  |5                  |0                           |vscode                      |default|typescript     |1                  |23                    |86                    |13                       |118                       |false          |1                  |1                  |typescript     |1                  |4                  
          |                   |JetBrains|default|30         |false          |3                  |5                     |21                         |3                  |                  |                   |                   |                            |JetBrains                   |default|java           |3                  |12                    |37                    |26                       |88                        |               |                   |                   |java           |3                  |                   
          |                   |         |       |           |               |                   |                      |                           |                   |                  |                   |                   |                            |                            |       |unknown        |1                  |3                     |13                    |4                        |28                        |false          |3                  |3                  |typescriptreact|1                  |                   
          |                   |         |       |           |               |                   |                      |                           |                   |                  |                   |                   |                            |                            |       |               |                   |                      |                      |                         |                          |               |                   |                   |unknown        |1                  |                   
          |                   |         |       |           |               |                   |                      |                           |                   |                  |                   |                   |                            |                            |       |               |                   |                      |                      |                         |                          |               |                   |                   |json           |1                  |                   
2025-03-21|5                  |vscode   |default|21         |false          |2                  |12                    |0                          |2                  |6                 |0                  |6                  |0                           |vscode                      |default|typescript     |1                  |59                    |238                   |49                       |385                       |false          |2                  |2                  |typescript     |1                  |6                  
          |                   |JetBrains|default|12         |false          |3                  |0                     |13                         |3                  |                  |                   |                   |                            |JetBrains                   |default|java           |2                  |10                    |39                    |15                       |85                        |               |                   |                   |typescriptreact|2                  |                   
          |                   |         |       |           |               |                   |                      |                           |                   |                  |                   |                   |                            |                            |       |unknown        |2                  |45                    |92                    |48                       |129                       |               |                   |                   |java           |2                  |                   
          |                   |         |       |           |               |                   |                      |                           |                   |                  |                   |                   |                            |                            |       |json           |2                  |5                     |12                    |5                        |26                        |               |                   |                   |unknown        |2                  |                   
          |                   |         |       |           |               |                   |                      |                           |                   |                  |                   |                   |                            |                            |       |yaml           |0                  |0                     |4                     |0                        |4                         |false          |4                  |4                  |json           |2                  |                   
          |                   |         |       |           |               |                   |                      |                           |                   |                  |                   |                   |                            |                            |       |               |                   |                      |                      |                         |                          |               |                   |                   |yaml           |0                  |                   
2025-03-23|1                  |vscode   |default|13         |false          |1                  |0                     |0                          |1                  |1                 |0                  |1                  |0                           |vscode                      |default|typescriptreact|1                  |54                    |100                   |47                       |192                       |false          |1                  |1                  |typescriptreact|1                  |1                  
2025-03-24|6                  |JetBrains|default|16         |false          |5                  |15                    |10                         |5                  |7                 |0                  |7                  |0                           |JetBrains                   |default|unknown        |1                  |35                    |79                    |43                       |144                       |false          |2                  |2                  |unknown        |1                  |4                  
          |                   |vscode   |default|12         |false          |1                  |0                     |0                          |1                  |                  |                   |                   |                            |vscode                      |default|typescript     |2                  |34                    |156                   |12                       |218                       |               |                   |                   |typescript     |2                  |                   
          |                   |         |       |           |               |                   |                      |                           |                   |                  |                   |                   |                            |                            |       |typescriptreact|2                  |61                    |205                   |70                       |396                       |false          |2                  |2                  |typescriptreact|2                  |                   
          |                   |         |       |           |               |                   |                      |                           |                   |                  |                   |                   |                            |                            |       |markdown       |0                  |0                     |1                     |0                        |1                         |               |                   |                   |json           |0                  |                   
          |                   |         |       |           |               |                   |                      |                           |                   |                  |                   |                   |                            |                            |       |xml            |1                  |1                     |4                     |1                        |5                         |               |                   |                   |java           |2                  |                   
          |                   |         |       |           |               |                   |                      |                           |                   |                  |                   |                   |                            |                            |       |               |                   |                      |                      |                         |                          |               |                   |                   |markdown       |0                  |                   
          |                   |         |       |           |               |                   |                      |                           |                   |                  |                   |                   |                            |                            |       |               |                   |                      |                      |                         |                          |               |                   |                   |xml            |1                  |                   
2025-03-25|6                  |vscode   |default|20         |false          |2                  |2                     |0                          |2                  |7                 |0                  |7                  |0                           |JetBrains                   |default|java           |5                  |47                    |145                   |96                       |363                       |false          |5                  |5                  |typescriptreact|2                  |7                  
          |                   |JetBrains|default|27         |false          |4                  |10                    |10                         |4                  |                  |                   |                   |                            |vscode                      |default|typescriptreact|2                  |78                    |225                   |128                      |491                       |               |                   |                   |java           |5                  |                   
          |                   |         |       |           |               |                   |                      |                           |                   |                  |                   |                   |                            |                            |       |typescript     |2                  |40                    |126                   |39                       |154                       |false          |2                  |2                  |typescript     |2                  |                   
          |                   |         |       |           |               |                   |                      |                           |                   |                  |                   |                   |                            |                            |       |               |                   |                      |                      |                         |                          |               |                   |                   |unknown        |1                  |                   
          |                   |         |       |           |               |                   |                      |                           |                   |                  |                   |                   |                            |                            |       |               |                   |                      |                      |                         |                          |               |                   |                   |json           |1                  |                   
2025-03-26|4                  |vscode   |default|14         |false          |2                  |2                     |0                          |2                  |7                 |0                  |6                  |0                           |vscode                      |default|typescript     |3                  |220                   |421                   |275                      |733                       |false          |3                  |3                  |typescript     |3                  |5                  
          |                   |JetBrains|default|19         |false          |2                  |8                     |5                          |2                  |                  |                   |                   |                            |JetBrains                   |default|java           |1                  |11                    |39                    |92                       |237                       |               |                   |                   |java           |1                  |                   
          |                   |         |       |           |               |                   |                      |                           |                   |                  |                   |                   |                            |                            |       |xml            |1                  |1                     |9                     |1                        |9                         |               |                   |                   |typescriptreact|2                  |                   
          |                   |         |       |           |               |                   |                      |                           |                   |                  |                   |                   |                            |                            |       |json           |0                  |0                     |2                     |0                        |2                         |false          |2                  |2                  |xml            |1                  |                   
          |                   |         |       |           |               |                   |                      |                           |                   |                  |                   |                   |                            |                            |       |               |                   |                      |                      |                         |                          |               |                   |                   |unknown        |1                  |                   
          |                   |         |       |           |               |                   |                      |                           |                   |                  |                   |                   |                            |                            |       |               |                   |                      |                      |                         |                          |               |                   |                   |json           |0                  |                   
2025-03-27|5                  |vscode   |default|26         |false          |2                  |0                     |0                          |2                  |7                 |0                  |7                  |0                           |JetBrains                   |default|unknown        |2                  |38                    |77                    |50                       |110                       |false          |4                  |4                  |unknown        |3                  |7                  
          |                   |JetBrains|default|25         |false          |3                  |11                    |9                          |3                  |                  |                   |                   |                            |vscode                      |default|typescriptreact|2                  |26                    |87                    |28                       |131                       |               |                   |                   |java           |3                  |                   
          |                   |         |       |           |               |                   |                      |                           |                   |                  |                   |                   |                            |                            |       |unknown        |1                  |2                     |42                    |2                        |99                        |               |                   |                   |typescriptreact|2                  |                   
          |                   |         |       |           |               |                   |                      |                           |                   |                  |                   |                   |                            |                            |       |typescript     |3                  |16                    |62                    |12                       |83                        |false          |3                  |3                  |typescript     |3                  |                   
2025-03-28|4                  |vscode   |default|7          |false          |2                  |0                     |0                          |2                  |6                 |0                  |6                  |0                           |JetBrains                   |default|java           |2                  |35                    |132                   |91                       |449                       |false          |4                  |4                  |java           |2                  |5                  
          |                   |JetBrains|default|18         |false          |2                  |2                     |18                         |2                  |                  |                   |                   |                            |vscode                      |default|feature        |1                  |2                     |14                    |2                        |27                        |               |                   |                   |unknown        |2                  |                   
          |                   |         |       |           |               |                   |                      |                           |                   |                  |                   |                   |                            |                            |       |typescript     |1                  |6                     |22                    |5                        |30                        |false          |1                  |1                  |feature        |1                  |                   
          |                   |         |       |           |               |                   |                      |                           |                   |                  |                   |                   |                            |                            |       |               |                   |                      |                      |                         |                          |               |                   |                   |typescript     |1                  |                   
          |                   |         |       |           |               |                   |                      |                           |                   |                  |                   |                   |                            |                            |       |               |                   |                      |                      |                         |                          |               |                   |                   |json           |1                  |                   
2025-03-31|6                  |vscode   |default|8          |false          |2                  |0                     |0                          |2                  |7                 |0                  |7                  |0                           |vscode                      |default|typescript     |2                  |72                    |153                   |64                       |185                       |false          |2                  |2                  |typescript     |2                  |6                  
          |                   |JetBrains|default|16         |false          |4                  |5                     |13                         |4                  |                  |                   |                   |                            |JetBrains                   |default|java           |4                  |41                    |168                   |95                       |460                       |               |                   |                   |java           |4                  |                   
          |                   |         |       |           |               |                   |                      |                           |                   |                  |                   |                   |                            |                            |       |unknown        |1                  |2                     |9                     |2                        |10                        |               |                   |                   |feature        |0                  |                   
          |                   |         |       |           |               |                   |                      |                           |                   |                  |                   |                   |                            |                            |       |json           |0                  |0                     |1                     |0                        |1                         |false          |4                  |4                  |unknown        |1                  |                   
          |                   |         |       |           |               |                   |                      |                           |                   |                  |                   |                   |                            |                            |       |               |                   |                      |                      |                         |                          |               |                   |                   |csv            |0                  |                   
          |                   |         |       |           |               |                   |                      |                           |                   |                  |                   |                   |                            |                            |       |               |                   |                      |                      |                         |                          |               |                   |                   |json           |0                  |                   
2025-04-01|3                  |JetBrains|default|20         |false          |2                  |4                     |21                         |2                  |6                 |0                  |6                  |0                           |vscode                      |default|typescript     |2                  |101                   |231                   |92                       |313                       |false          |2                  |2                  |typescript     |2                  |5                  
          |                   |vscode   |default|10         |false          |1                  |0                     |0                          |1                  |                  |                   |                   |                            |JetBrains                   |default|java           |3                  |53                    |273                   |86                       |912                       |               |                   |                   |java           |3                  |                   
          |                   |         |       |           |               |                   |                      |                           |                   |                  |                   |                   |                            |                            |       |unknown        |2                  |3                     |7                     |3                        |11                        |               |                   |                   |feature        |1                  |                   
          |                   |         |       |           |               |                   |                      |                           |                   |                  |                   |                   |                            |                            |       |json           |0                  |0                     |3                     |0                        |4                         |false          |3                  |3                  |unknown        |2                  |                   
          |                   |         |       |           |               |                   |                      |                           |                   |                  |                   |                   |                            |                            |       |               |                   |                      |                      |                         |                          |               |                   |                   |json           |0                  |                   
          |                   |         |       |           |               |                   |                      |                           |                   |                  |                   |                   |                            |                            |       |               |                   |                      |                      |                         |                          |               |                   |                   |csv            |1                  |                   
2025-04-02|9                  |vscode   |default|51         |false          |6                  |12                    |0                          |6                  |9                 |0                  |9                  |0                           |vscode                      |default|typescript     |2                  |96                    |221                   |103                      |332                       |false          |4                  |4                  |typescript     |2                  |7                  
          |                   |JetBrains|default|11         |false          |3                  |9                     |1                          |3                  |                  |                   |                   |                            |JetBrains                   |default|java           |3                  |54                    |244                   |89                       |626                       |               |                   |                   |java           |4                  |                   
          |                   |         |       |           |               |                   |                      |                           |                   |                  |                   |                   |                            |                            |       |yaml           |1                  |5                     |6                     |17                       |18                        |               |                   |                   |typescriptreact|1                  |                   
          |                   |         |       |           |               |                   |                      |                           |                   |                  |                   |                   |                            |                            |       |unknown        |1                  |3                     |7                     |3                        |7                         |               |                   |                   |feature        |1                  |                   
          |                   |         |       |           |               |                   |                      |                           |                   |                  |                   |                   |                            |                            |       |json           |0                  |0                     |1                     |0                        |2                         |false          |4                  |4                  |yaml           |1                  |                   
          |                   |         |       |           |               |                   |                      |                           |                   |                  |                   |                   |                            |                            |       |               |                   |                      |                      |                         |                          |               |                   |                   |json           |0                  |                   
          |                   |         |       |           |               |                   |                      |                           |                   |                  |                   |                   |                            |                            |       |               |                   |                      |                      |                         |                          |               |                   |                   |unknown        |1                  |                   
2025-04-03|8                  |JetBrains|default|18         |false          |4                  |5                     |6                          |4                  |8                 |0                  |8                  |0                           |vscode                      |default|typescript     |3                  |108                   |250                   |170                      |418                       |false          |3                  |3                  |typescript     |3                  |6                  
          |                   |vscode   |default|52         |false          |4                  |6                     |1                          |4                  |                  |                   |                   |                            |JetBrains                   |default|java           |3                  |26                    |111                   |37                       |210                       |               |                   |                   |java           |3                  |                   
          |                   |         |       |           |               |                   |                      |                           |                   |                  |                   |                   |                            |                            |       |unknown        |1                  |1                     |18                    |1                        |58                        |false          |3                  |3                  |typescriptreact|2                  |                   
          |                   |         |       |           |               |                   |                      |                           |                   |                  |                   |                   |                            |                            |       |dotenv         |0                  |0                     |2                     |0                        |2                         |               |                   |                   |feature        |1                  |                   
          |                   |         |       |           |               |                   |                      |                           |                   |                  |                   |                   |                            |                            |       |               |                   |                      |                      |                         |                          |               |                   |                   |unknown        |1                  |                   
          |                   |         |       |           |               |                   |                      |                           |                   |                  |                   |                   |                            |                            |       |               |                   |                      |                      |                         |                          |               |                   |                   |dotenv         |0                  |                   
""")

    def test_json_to_csv_super_complex2(self):
        """Test another super complex conversion with reformatted JSON."""
        self.assert_r("""[
  {
    "date" : "2025-03-17",
    "total_active_users" : 1,
    "total_engaged_users" : 1,
    "copilot_ide_chat" : {
      "total_engaged_users" : 0
    },
    "copilot_dotcom_chat" : {
      "total_engaged_users" : 0
    },
    "copilot_dotcom_pull_requests" : {
      "total_engaged_users" : 0
    },
    "copilot_ide_code_completions" : {
      "editors" : [
        {
          "models" : [
            {
              "is_custom_model" : false,
              "languages" : [
                {
                  "name" : "json",
                  "total_code_acceptances" : 1,
                  "total_code_lines_accepted" : 1,
                  "total_code_lines_suggested" : 1,
                  "total_code_suggestions" : 1,
                  "total_engaged_users" : 1
                }
              ],
              "name" : "default",
              "total_engaged_users" : 1
            }
          ],
          "name" : "JetBrains",
          "total_engaged_users" : 1
        }
      ],
      "languages" : [
        {
          "name" : "json",
          "total_engaged_users" : 1
        }
      ],
      "total_engaged_users" : 1
    }
  },
  {
    "date" : "2025-03-18",
    "total_active_users" : 5,
    "total_engaged_users" : 3,
    "copilot_ide_chat" : {
      "editors" : [
        {
          "models" : [
            {
              "is_custom_model" : false,
              "name" : "default",
              "total_chat_copy_events" : 1,
              "total_chat_insertion_events" : 0,
              "total_chats" : 4,
              "total_engaged_users" : 1
            }
          ],
          "name" : "JetBrains",
          "total_engaged_users" : 1
        },
        {
          "models" : [
            {
              "is_custom_model" : false,
              "name" : "default",
              "total_chat_copy_events" : 0,
              "total_chat_insertion_events" : 0,
              "total_chats" : 4,
              "total_engaged_users" : 1
            }
          ],
          "name" : "vscode",
          "total_engaged_users" : 1
        }
      ],
      "total_engaged_users" : 2
    },
    "copilot_dotcom_chat" : {
      "total_engaged_users" : 0
    },
    "copilot_dotcom_pull_requests" : {
      "total_engaged_users" : 0
    },
    "copilot_ide_code_completions" : {
      "editors" : [
        {
          "models" : [
            {
              "is_custom_model" : false,
              "languages" : [
                {
                  "name" : "java",
                  "total_code_acceptances" : 12,
                  "total_code_lines_accepted" : 18,
                  "total_code_lines_suggested" : 214,
                  "total_code_suggestions" : 67,
                  "total_engaged_users" : 2
                },
                {
                  "name" : "json",
                  "total_code_acceptances" : 0,
                  "total_code_lines_accepted" : 0,
                  "total_code_lines_suggested" : 13,
                  "total_code_suggestions" : 1,
                  "total_engaged_users" : 0
                },
                {
                  "name" : "unknown",
                  "total_code_acceptances" : 0,
                  "total_code_lines_accepted" : 0,
                  "total_code_lines_suggested" : 21,
                  "total_code_suggestions" : 11,
                  "total_engaged_users" : 0
                }
              ],
              "name" : "default",
              "total_engaged_users" : 2
            }
          ],
          "name" : "JetBrains",
          "total_engaged_users" : 2
        }
      ],
      "languages" : [
        {
          "name" : "java",
          "total_engaged_users" : 2
        },
        {
          "name" : "json",
          "total_engaged_users" : 0
        },
        {
          "name" : "unknown",
          "total_engaged_users" : 0
        }
      ],
      "total_engaged_users" : 2
    }
  }
]


date,total_active_users,total_engaged_users,copilot_ide_chat,,,,,,,,,copilot_dotcom_chat,copilot_dotcom_pull_requests,copilot_ide_code_completions,,,,,,,,,,,,,
,,,total_engaged_users,editors,,,,,,,,total_engaged_users,total_engaged_users,editors,,,,,,,,,,,languages,,total_engaged_users
,,,,models,,,,,,name,total_engaged_users,,,models,,,,,,,,,name,total_engaged_users,name,total_engaged_users,
,,,,is_custom_model,name,total_chat_copy_events,total_chat_insertion_events,total_chats,total_engaged_users,,,,,is_custom_model,languages,,,,,,name,total_engaged_users,,,,,
,,,,,,,,,,,,,,,name,total_code_acceptances,total_code_lines_accepted,total_code_lines_suggested,total_code_suggestions,total_engaged_users,,,,,,,
2025-03-17,1,1,0,,,,,,,,,0,0,false,json,1,1,1,1,1,default,1,JetBrains,1,json,1,1
2025-03-18,5,3,2,false,default,0,0,4,1,vscode,1,0,0,false,java,12,18,214,67,2,default,2,JetBrains,2,java,2,2
,,,,,,,,,,,,,,,json,0,0,13,1,0,,,,,json,0,
,,,,,,,,,,,,,,,unknown,0,0,21,11,0,,,,,unknown,0,


date      |total_active_users|total_engaged_users|copilot_ide_chat   |               |       |                      |                           |           |                   |      |                   |copilot_dotcom_chat|copilot_dotcom_pull_requests|copilot_ide_code_completions|         |                      |                         |                          |                      |                   |       |                   |         |                   |         |                   |                   
          |                  |                   |total_engaged_users|editors        |       |                      |                           |           |                   |      |                   |total_engaged_users|total_engaged_users         |editors                     |         |                      |                         |                          |                      |                   |       |                   |         |                   |languages|                   |total_engaged_users
          |                  |                   |                   |models         |       |                      |                           |           |                   |name  |total_engaged_users|                   |                            |models                      |         |                      |                         |                          |                      |                   |       |                   |name     |total_engaged_users|name     |total_engaged_users|                   
          |                  |                   |                   |is_custom_model|name   |total_chat_copy_events|total_chat_insertion_events|total_chats|total_engaged_users|      |                   |                   |                            |is_custom_model             |languages|                      |                         |                          |                      |                   |name   |total_engaged_users|         |                   |         |                   |                   
          |                  |                   |                   |               |       |                      |                           |           |                   |      |                   |                   |                            |                            |name     |total_code_acceptances|total_code_lines_accepted|total_code_lines_suggested|total_code_suggestions|total_engaged_users|       |                   |         |                   |         |                   |                   
--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
2025-03-17|1                 |1                  |0                  |               |       |                      |                           |           |                   |      |                   |0                  |0                           |false                       |json     |1                     |1                        |1                         |1                     |1                  |default|1                  |JetBrains|1                  |json     |1                  |1                  
2025-03-18|5                 |3                  |2                  |false          |default|0                     |0                          |4          |1                  |vscode|1                  |0                  |0                           |false                       |java     |12                    |18                       |214                       |67                    |2                  |default|2                  |JetBrains|2                  |java     |2                  |2                  
          |                  |                   |                   |               |       |                      |                           |           |                   |      |                   |                   |                            |                            |json     |0                     |0                        |13                        |1                     |0                  |       |                   |         |                   |json     |0                  |                   
          |                  |                   |                   |               |       |                      |                           |           |                   |      |                   |                   |                            |                            |unknown  |0                     |0                        |21                        |11                    |0                  |       |                   |         |                   |unknown  |0                  |                   
""")

    def performance(self):
        """Performance test calling test_json_to_csv_super_complex2 multiple times."""
        import time
        start = time.time()
        for i in range(100):  # Reduced iterations for faster testing
            self.test_json_to_csv_super_complex2()
        end = time.time()
        print(f"Performance test took: {(end - start) * 1000:.0f} ms")

if __name__ == '__main__':
    unittest.main()