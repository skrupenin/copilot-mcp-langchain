package com.codenjoy.dojo.service.csv;

import com.codenjoy.dojo.utils.csv.JsonToCsv;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;

public class JsonToCsvTest {

    @Test
    public void testJsonToCsv_simple_oneObject_oneFiled() {
        assertR("[\n" +
                "    {\n" +
                "        \"field\": \"value1\"\n" +
                "    }\n" +
                "]\n" +
                "\n" +
                "\n" +
                "field\n" +
                "value1\n" +
                "\n" +
                "\n" +
                "field \n" +
                "------\n" +
                "value1\n");
    }

    @Test
    public void testJsonToCsv_simple_oneObject_oneFiled_caseEscape_caseComma() {
        assertR("[\n" +
                "    {\n" +
                "        \"field\": \"val,ue1\"\n" +
                "    }\n" +
                "]\n" +
                "\n" +
                "\n" +
                "field\n" +
                "\"val,ue1\"\n" +
                "\n" +
                "\n" +
                "field  \n" +
                "-------\n" +
                "val,ue1\n");
    }

    @Test
    public void testJsonToCsv_simple_oneObject_oneFiled_caseEscape_caseQuote() {
        assertR("[\n" +
                "    {\n" +
                "        \"field\": \"val\\\"ue1\"\n" +
                "    }\n" +
                "]\n" +
                "\n" +
                "\n" +
                "field\n" +
                "\"val\"\"ue1\"\n" +
                "\n" +
                "\n" +
                "field  \n" +
                "-------\n" +
                "val\"ue1\n");
    }

    @Test
    public void testJsonToCsv_simple_oneObject_oneFiled_caseEscape_caseNewLine() {
        assertR("[\n" +
                "    {\n" +
                "        \"field\": \"val\\nue1\"\n" +
                "    }\n" +
                "]\n" +
                "\n" +
                "\n" +
                "field\n" +
                "\"val\nue1\"\n" +
                "\n" +
                "\n" +
                "field  \n" +
                "-------\n" +
                "val\nue1\n");
    }

    @Test
    public void testJsonToCsv_simple_twoObjects_oneFiled() {
        assertR("[\n" +
                "    {\n" +
                "        \"field\": \"value1\"\n" +
                "    },\n" +
                "    {\n" +
                "        \"field\": \"value2\"\n" +
                "    }\n" +
                "]\n" +
                "\n" +
                "\n" +
                "field\n" +
                "value1\n" +
                "value2\n" +
                "\n" +
                "\n" +
                "field \n" +
                "------\n" +
                "value1\n" +
                "value2\n");
    }

    @Test
    public void testJsonToCsv_simple_oneObject_twoFields() {
        assertR("[\n" +
                "    {\n" +
                "        \"field1\": \"value1\",\n" +
                "        \"field2\": \"value2\"\n" +
                "    }\n" +
                "]\n" +
                "\n" +
                "\n" +
                "field1,field2\n" +
                "value1,value2\n" +
                "\n" +
                "\n" +
                "field1|field2\n" +
                "-------------\n" +
                "value1|value2\n");
    }

    @Test
    public void testJsonToCsv_simple_twoObjects_twoFields() {
        assertR("[\n" +
                "    {\n" +
                "        \"field1\": \"value1\",\n" +
                "        \"field2\": \"value2\"\n" +
                "    },\n" +
                "    {\n" +
                "        \"field1\": \"value3\",\n" +
                "        \"field2\": \"value4\"\n" +
                "    }\n" +
                "]\n" +
                "\n" +
                "\n" +
                "field1,field2\n" +
                "value1,value2\n" +
                "value3,value4\n" +
                "\n" +
                "\n" +
                "field1|field2\n" +
                "-------------\n" +
                "value1|value2\n" +
                "value3|value4\n");
    }

    @Test
    public void testJsonToCsv_simple() {
        assertR("[\n" +
                "    {\n" +
                "        \"zField\": \"value3\",\n" +
                "        \"aField\": \"value1\"\n" +
                "    },\n" +
                "    {\n" +
                "        \"zField\": \"test\",\n" +
                "        \"name\": \"example\"\n" +
                "    }\n" +
                "]\n" +
                "\n" + 
                "\n" + 
                "zField,aField,name\n" +
                "value3,value1,\n" +
                "test,,example\n" +
                "\n" +
                "\n" +
                "zField|aField|name   \n" +
                "---------------------\n" +
                "value3|value1|       \n" +
                "test  |      |example\n");
    }

    @Test
    public void testJsonToCsv_subArray_caseSimple() {
        assertR("[\n" +
                "    {\n" +
                "        \"field\": \"value1\",\n" +
                "        \"array\": [\"value2\", \"value3\"]\n" +
                "    },\n" +
                "    {\n" +
                "        \"field\": \"value4\",\n" +
                "        \"array\": [\"value5\", \"value6\"]\n" +
                "    }\n" +
                "]\n" +
                "\n" +
                "\n" +
                "field,array\n" +
                "value1,value2\n" +
                ",value3\n" +
                "value4,value5\n" +
                ",value6\n" +
                "\n" +
                "\n" +
                "field |array \n" +
                "-------------\n" +
                "value1|value2\n" +
                "      |value3\n" +
                "value4|value5\n" +
                "      |value6\n");
    }

    @Test
    public void testJsonToCsv_subArray() {
        assertR("[\n" +
                "    {\n" +
                "        \"zField\": \"value3\",\n" +
                "        \"aField\": \"value1\",\n" +
                "        \"numberArray\": [3, 1, 2]\n" +
                "    },\n" +
                "    {\n" +
                "        \"zField\": \"test\",\n" +
                "        \"name\": \"example\",\n" +
                "        \"numberArray\": [10, 2, 30]\n" +
                "    }\n" +
                "]\n" +
                "\n" +
                "\n" +
                "zField,aField,numberArray,name\n" +
                "value3,value1,3,\n" +
                ",,1,\n" +
                ",,2,\n" +
                "test,,10,example\n" +
                ",,2,\n" +
                ",,30,\n" +
                "\n" +
                "\n" +
                "zField|aField|numberArray|name   \n" +
                "---------------------------------\n" +
                "value3|value1|3          |       \n" +
                "      |      |1          |       \n" +
                "      |      |2          |       \n" +
                "test  |      |10         |example\n" +
                "      |      |2          |       \n" +
                "      |      |30         |       \n");
    }

    @Test
    public void testJsonToCsv_subArray_notSameLength() {
        assertR("[\n" +
                "    {\n" +
                "        \"zField\": \"value3\",\n" +
                "        \"aField\": \"value1\",\n" +
                "        \"numberArray\": [3, 1, 2]\n" +
                "    },\n" +
                "    {\n" +
                "        \"zField\": \"test\",\n" +
                "        \"name\": \"example\",\n" +
                "        \"numberArray\": [10, 2, 30]\n" +
                "    },\n" +
                "    {\n" +
                "        \"id\": \"12345\",\n" +
                "        \"aField\": \"value6\",\n" +
                "        \"numberArray\": [1, 10, 100, 1000]\n" +
                "    }\n" +
                "]\n" +
                "\n" +
                "\n" +
                "zField,aField,numberArray,name,id\n" +
                "value3,value1,3,,\n" +
                ",,1,,\n" +
                ",,2,,\n" +
                "test,,10,example,\n" +
                ",,2,,\n" +
                ",,30,,\n" +
                ",value6,1,,12345\n" +
                ",,10,,\n" +
                ",,100,,\n" +
                ",,1000,,\n" +
                "\n" +
                "\n" +
                "zField|aField|numberArray|name   |id   \n" +
                "---------------------------------------\n" +
                "value3|value1|3          |       |     \n" +
                "      |      |1          |       |     \n" +
                "      |      |2          |       |     \n" +
                "test  |      |10         |example|     \n" +
                "      |      |2          |       |     \n" +
                "      |      |30         |       |     \n" +
                "      |value6|1          |       |12345\n" +
                "      |      |10         |       |     \n" +
                "      |      |100        |       |     \n" +
                "      |      |1000       |       |     \n");
    }

    @Test
    public void testJsonToCsv_twoDifferentArrays() {
        assertR("[\n" +
                "    {\n" +
                "        \"filed\": \"name\",\n" +
                "        \"array1\": [1, 2, 3],\n" +
                "        \"array2\": [4, 5, 6]\n" +
                "    }\n" +
                "]\n" +
                "\n" +
                "\n" +
                "filed,array1,array2\n" +
                "name,1,4\n" +
                ",2,5\n" +
                ",3,6\n" +
                "\n" +
                "\n" +
                "filed|array1|array2\n" +
                "-------------------\n" +
                "name |1     |4     \n" +
                "     |2     |5     \n" +
                "     |3     |6     \n");
    }

    @Test
    public void testJsonToCsv_subArrayOfObjects_caseSameArraysLength() {
        assertR("[\n" +
                "    {\n" +
                "        \"zField\": \"value3\",\n" +
                "        \"aField\": \"value1\",\n" +
                "        \"arrayField\": [\n" +
                "            {\"name\": \"banana\", \"color\": \"yellow\"},\n" +
                "            {\"name\": \"apple\", \"color\": \"red\"},\n" +
                "            {\"name\": \"cherry\", \"color\": \"red\"}\n" +
                "        ],\n" +
                "        \"numberArray\": [3, 1, 2]\n" +
                "    },\n" +
                "    {\n" +
                "        \"zField\": \"test\",\n" +
                "        \"name\": \"example\",\n" +
                "        \"numberArray\": [10, 2, 30]\n" +
                "    }\n" +
                "]\n" +
                "\n" +
                "\n" +
                "zField,aField,arrayField,,numberArray,name\n" +
                ",,name,color,,\n" +
                "value3,value1,banana,yellow,3,\n" +
                ",,apple,red,1,\n" +
                ",,cherry,red,2,\n" +
                "test,,,,10,example\n" +
                ",,,,2,\n" +
                ",,,,30,\n" +
                "\n" +
                "\n" +
                "zField|aField|arrayField|      |numberArray|name   \n" +
                "      |      |name      |color |           |       \n" +
                "---------------------------------------------------\n" +
                "value3|value1|banana    |yellow|3          |       \n" +
                "      |      |apple     |red   |1          |       \n" +
                "      |      |cherry    |red   |2          |       \n" +
                "test  |      |          |      |10         |example\n" +
                "      |      |          |      |2          |       \n" +
                "      |      |          |      |30         |       \n");
    }

    @Test
    public void testJsonToCsv_subArrayOfObjects_caseOneIsLess() {
        assertR("[\n" +
                "    {\n" +
                "        \"zField\": \"value3\",\n" +
                "        \"aField\": \"value1\",\n" +
                "        \"arrayField\": [\n" +
                "            {\"name\": \"banana\", \"color\": \"yellow\"},\n" +
                "            {\"name\": \"apple\", \"color\": \"red\"}\n" +
                "        ],\n" +
                "        \"numberArray\": [3, 1, 2]\n" +
                "    },\n" +
                "    {\n" +
                "        \"zField\": \"test\",\n" +
                "        \"name\": \"example\",\n" +
                "        \"numberArray\": [10, 2, 30]\n" +
                "    }\n" +
                "]\n" +
                "\n" +
                "\n" +
                "zField,aField,arrayField,,numberArray,name\n" +
                ",,name,color,,\n" +
                "value3,value1,banana,yellow,3,\n" +
                ",,apple,red,1,\n" +
                ",,,,2,\n" +
                "test,,,,10,example\n" +
                ",,,,2,\n" +
                ",,,,30,\n" +
                "\n" +
                "\n" +
                "zField|aField|arrayField|      |numberArray|name   \n" +
                "      |      |name      |color |           |       \n" +
                "---------------------------------------------------\n" +
                "value3|value1|banana    |yellow|3          |       \n" +
                "      |      |apple     |red   |1          |       \n" +
                "      |      |          |      |2          |       \n" +
                "test  |      |          |      |10         |example\n" +
                "      |      |          |      |2          |       \n" +
                "      |      |          |      |30         |       \n");
    }

    @Test
    public void testJsonToCsv_subArrayOfObjects_caseAnotherIsLess() {
        assertR("[\n" +
                "    {\n" +
                "        \"zField\": \"value3\",\n" +
                "        \"aField\": \"value1\",\n" +
                "        \"arrayField\": [\n" +
                "            {\"name\": \"banana\", \"color\": \"yellow\"},\n" +
                "            {\"name\": \"apple\", \"color\": \"red\"},\n" +
                "            {\"name\": \"cherry\", \"color\": \"red\"}\n" +
                "        ],\n" +
                "        \"numberArray\": [3, 1]\n" +
                "    },\n" +
                "    {\n" +
                "        \"zField\": \"test\",\n" +
                "        \"name\": \"example\",\n" +
                "        \"numberArray\": [10, 2, 30]\n" +
                "    }\n" +
                "]\n" +
                "\n" +
                "\n" +
                "zField,aField,arrayField,,numberArray,name\n" +
                ",,name,color,,\n" +
                "value3,value1,banana,yellow,3,\n" +
                ",,apple,red,1,\n" +
                ",,cherry,red,,\n" +
                "test,,,,10,example\n" +
                ",,,,2,\n" +
                ",,,,30,\n" +
                "\n" +
                "\n" +
                "zField|aField|arrayField|      |numberArray|name   \n" +
                "      |      |name      |color |           |       \n" +
                "---------------------------------------------------\n" +
                "value3|value1|banana    |yellow|3          |       \n" +
                "      |      |apple     |red   |1          |       \n" +
                "      |      |cherry    |red   |           |       \n" +
                "test  |      |          |      |10         |example\n" +
                "      |      |          |      |2          |       \n" +
                "      |      |          |      |30         |       \n");
    }

    @Test
    public void testJsonToCsv_subArrayOfObjects_thatContainsOfObjects() {
        assertR("[\n" +
                "    {\n" +
                "        \"zField\": \"value3\",\n" +
                "        \"aField\": \"value1\",\n" +
                "        \"arrayField\": [\n" +
                "            {\"name\": \"banana\", \"color\":\n" +
                "                {\"id\": \"y\", \"value\": \"yellow\"}\n" +
                "            },\n" +
                "            {\"name\": \"apple\", \"color\":\n" +
                "                {\"id\": \"r\", \"value\": \"red\"}\n" +
                "            },\n" +
                "            {\"name\": \"cherry\", \"color\":\n" +
                "                {\"id\": \"r\", \"value\": \"red\"}\n" +
                "            }\n" +
                "        ],\n" +
                "        \"numberArray\": [3, 1, 2]\n" +
                "    },\n" +
                "    {\n" +
                "        \"zField\": \"test\",\n" +
                "        \"name\": \"example\",\n" +
                "        \"numberArray\": [10, 2, 30]\n" +
                "    }\n" +
                "]\n" +
                "\n" +
                "\n" +
                "zField,aField,arrayField,,,numberArray,name\n" +
                ",,name,color,,,\n" +
                ",,,id,value,,\n" +
                "value3,value1,banana,y,yellow,3,\n" +
                ",,apple,r,red,1,\n" +
                ",,cherry,r,red,2,\n" +
                "test,,,,,10,example\n" +
                ",,,,,2,\n" +
                ",,,,,30,\n" +
                "\n" +
                "\n" +
                "zField|aField|arrayField|     |      |numberArray|name   \n" +
                "      |      |name      |color|      |           |       \n" +
                "      |      |          |id   |value |           |       \n" +
                "---------------------------------------------------------\n" +
                "value3|value1|banana    |y    |yellow|3          |       \n" +
                "      |      |apple     |r    |red   |1          |       \n" +
                "      |      |cherry    |r    |red   |2          |       \n" +
                "test  |      |          |     |      |10         |example\n" +
                "      |      |          |     |      |2          |       \n" +
                "      |      |          |     |      |30         |       \n");
    }

    @Test
    public void testJsonToCsv_subArrayOfObjects_thatContainsOfArrayOfObjects() {
        assertR("[\n" +
                "    {\n" +
                "        \"zField\": \"value3\",\n" +
                "        \"aField\": \"value1\",\n" +
                "        \"arrayField\": [\n" +
                "            {\"name\": \"banana\", \"colors\": [\n" +
                "                {\"id\": \"y\", \"value\": \"yellow\"},\n" +
                "                {\"id\": \"g\", \"value\": \"green\"}\n" +
                "            ]},\n" +
                "            {\"name\": \"apple\", \"colors\": [\n" +
                "                {\"id\": \"m\", \"value\": \"magenta\"}\n" +
                "            ]},\n" +
                "            {\"name\": \"cherry\", \"colors\": [\n" +
                "                {\"id\": \"bl\", \"value\": \"black\"},\n" +
                "                {\"id\": \"w\", \"value\": \"white\"},\n" +
                "                {\"id\": \"br\", \"value\": \"brown\"}\n" +
                "            ]}\n" +
                "        ],\n" +
                "        \"numberArray\": [3, 1, 2]\n" +
                "    },\n" +
                "    {\n" +
                "        \"zField\": \"test\",\n" +
                "        \"name\": \"example\",\n" +
                "        \"numberArray\": [10, 2, 30]\n" +
                "    }\n" +
                "]\n" +
                "\n" +
                "\n" +
                "zField,aField,arrayField,,,numberArray,name\n" +
                ",,name,colors,,,\n" +
                ",,,id,value,,\n" +
                "value3,value1,banana,y,yellow,3,\n" +
                ",,,g,green,1,\n" +
                ",,apple,m,magenta,2,\n" +
                ",,cherry,bl,black,,\n" +
                ",,,w,white,,\n" +
                ",,,br,brown,,\n" +
                "test,,,,,10,example\n" +
                ",,,,,2,\n" +
                ",,,,,30,\n" +
                "\n" +
                "\n" +
                "zField|aField|arrayField|      |       |numberArray|name   \n" +
                "      |      |name      |colors|       |           |       \n" +
                "      |      |          |id    |value  |           |       \n" +
                "-----------------------------------------------------------\n" +
                "value3|value1|banana    |y     |yellow |3          |       \n" +
                "      |      |          |g     |green  |1          |       \n" +
                "      |      |apple     |m     |magenta|2          |       \n" +
                "      |      |cherry    |bl    |black  |           |       \n" +
                "      |      |          |w     |white  |           |       \n" +
                "      |      |          |br    |brown  |           |       \n" +
                "test  |      |          |      |       |10         |example\n" +
                "      |      |          |      |       |2          |       \n" +
                "      |      |          |      |       |30         |       \n");
    }

    @Test
    public void testJsonToCsv_objectWithObject() {
        assertR("[\n" +
                "    {\n" +
                "        \"zField\": \"value3\",\n" +
                "        \"aField\": \"value1\",\n" +
                "        \"objectField\": {\n" +
                "            \"name\": \"banana\",             \"color\": \"yellow\"\n" +
                "        },\n" +
                "        \"numberArray\": [3, 1, 2]\n" +
                "    },\n" +
                "    {\n" +
                "        \"zField\": \"test\",\n" +
                "        \"name\": \"example\",\n" +
                "        \"numberArray\": [10, 2, 30]\n" +
                "    }\n" +
                "]\n" +
                "\n" +
                "\n" +
                "zField,aField,objectField,,numberArray,name\n" +
                ",,name,color,,\n" +
                "value3,value1,banana,yellow,3,\n" +
                ",,,,1,\n" +
                ",,,,2,\n" +
                "test,,,,10,example\n" +
                ",,,,2,\n" +
                ",,,,30,\n" +
                "\n" +
                "\n" +
                "zField|aField|objectField|      |numberArray|name   \n" +
                "      |      |name       |color |           |       \n" +
                "----------------------------------------------------\n" +
                "value3|value1|banana     |yellow|3          |       \n" +
                "      |      |           |      |1          |       \n" +
                "      |      |           |      |2          |       \n" +
                "test  |      |           |      |10         |example\n" +
                "      |      |           |      |2          |       \n" +
                "      |      |           |      |30         |       \n");
    }

    @Test
    public void testJsonToCsv_complex() {
        assertR("[\n" +
                "  {\n" +
                "    \"date\": \"2025-03-17\",\n" +
                "    \"copilot_ide_chat\": {\n" +
                "      \"total_engaged_users\": 0\n" +
                "    },\n" +
                "    \"total_active_users\": 1,\n" +
                "    \"copilot_dotcom_chat\": {\n" +
                "      \"total_engaged_users\": 0\n" +
                "    },\n" +
                "    \"total_engaged_users\": 1,\n" +
                "    \"copilot_dotcom_pull_requests\": {\n" +
                "      \"total_engaged_users\": 0\n" +
                "    },\n" +
                "    \"copilot_ide_code_completions\": {\n" +
                "      \"editors\": [\n" +
                "        {\n" +
                "          \"name\": \"JetBrains\",\n" +
                "          \"models\": [\n" +
                "            {\n" +
                "              \"name\": \"default\",\n" +
                "              \"languages\": [\n" +
                "                {\n" +
                "                  \"name\": \"json\",\n" +
                "                  \"total_engaged_users\": 1,\n" +
                "                  \"total_code_acceptances\": 1,\n" +
                "                  \"total_code_suggestions\": 1,\n" +
                "                  \"total_code_lines_accepted\": 1,\n" +
                "                  \"total_code_lines_suggested\": 1\n" +
                "                }\n" +
                "              ],\n" +
                "              \"is_custom_model\": false,\n" +
                "              \"total_engaged_users\": 1\n" +
                "            }\n" +
                "          ],\n" +
                "          \"total_engaged_users\": 1\n" +
                "        }\n" +
                "      ],\n" +
                "      \"languages\": [\n" +
                "        {\n" +
                "          \"name\": \"json\",\n" +
                "          \"total_engaged_users\": 1\n" +
                "        }\n" +
                "      ],\n" +
                "      \"total_engaged_users\": 1\n" +
                "    }\n" +
                "  },\n" +
                "  {\n" +
                "    \"date\": \"2025-03-18\",\n" +
                "    \"copilot_ide_chat\": {\n" +
                "      \"editors\": [\n" +
                "        {\n" +
                "          \"name\": \"JetBrains\",\n" +
                "          \"models\": [\n" +
                "            {\n" +
                "              \"name\": \"default\",\n" +
                "              \"total_chats\": 4,\n" +
                "              \"is_custom_model\": false,\n" +
                "              \"total_engaged_users\": 1,\n" +
                "              \"total_chat_copy_events\": 1,\n" +
                "              \"total_chat_insertion_events\": 0\n" +
                "            }\n" +
                "          ],\n" +
                "          \"total_engaged_users\": 1\n" +
                "        },\n" +
                "        {\n" +
                "          \"name\": \"vscode\",\n" +
                "          \"models\": [\n" +
                "            {\n" +
                "              \"name\": \"default\",\n" +
                "              \"total_chats\": 4,\n" +
                "              \"is_custom_model\": false,\n" +
                "              \"total_engaged_users\": 1,\n" +
                "              \"total_chat_copy_events\": 0,\n" +
                "              \"total_chat_insertion_events\": 0\n" +
                "            }\n" +
                "          ],\n" +
                "          \"total_engaged_users\": 1\n" +
                "        }\n" +
                "      ],\n" +
                "      \"total_engaged_users\": 2\n" +
                "    },\n" +
                "    \"total_active_users\": 5,\n" +
                "    \"copilot_dotcom_chat\": {\n" +
                "      \"total_engaged_users\": 0\n" +
                "    },\n" +
                "    \"total_engaged_users\": 3,\n" +
                "    \"copilot_dotcom_pull_requests\": {\n" +
                "      \"total_engaged_users\": 0\n" +
                "    },\n" +
                "    \"copilot_ide_code_completions\": {\n" +
                "      \"editors\": [\n" +
                "        {\n" +
                "          \"name\": \"JetBrains\",\n" +
                "          \"models\": [\n" +
                "            {\n" +
                "              \"name\": \"default\",\n" +
                "              \"languages\": [\n" +
                "                {\n" +
                "                  \"name\": \"java\",\n" +
                "                  \"total_engaged_users\": 2,\n" +
                "                  \"total_code_acceptances\": 12,\n" +
                "                  \"total_code_suggestions\": 67,\n" +
                "                  \"total_code_lines_accepted\": 18,\n" +
                "                  \"total_code_lines_suggested\": 214\n" +
                "                },\n" +
                "                {\n" +
                "                  \"name\": \"unknown\",\n" +
                "                  \"total_engaged_users\": 0,\n" +
                "                  \"total_code_acceptances\": 0,\n" +
                "                  \"total_code_suggestions\": 11,\n" +
                "                  \"total_code_lines_accepted\": 0,\n" +
                "                  \"total_code_lines_suggested\": 21\n" +
                "                },\n" +
                "                {\n" +
                "                  \"name\": \"json\",\n" +
                "                  \"total_engaged_users\": 0,\n" +
                "                  \"total_code_acceptances\": 0,\n" +
                "                  \"total_code_suggestions\": 1,\n" +
                "                  \"total_code_lines_accepted\": 0,\n" +
                "                  \"total_code_lines_suggested\": 13\n" +
                "                }\n" +
                "              ],\n" +
                "              \"is_custom_model\": false,\n" +
                "              \"total_engaged_users\": 2\n" +
                "            }\n" +
                "          ],\n" +
                "          \"total_engaged_users\": 2\n" +
                "        }\n" +
                "      ],\n" +
                "      \"languages\": [\n" +
                "        {\n" +
                "          \"name\": \"java\",\n" +
                "          \"total_engaged_users\": 2\n" +
                "        },\n" +
                "        {\n" +
                "          \"name\": \"unknown\",\n" +
                "          \"total_engaged_users\": 0\n" +
                "        },\n" +
                "        {\n" +
                "          \"name\": \"json\",\n" +
                "          \"total_engaged_users\": 0\n" +
                "        }\n" +
                "      ],\n" +
                "      \"total_engaged_users\": 2\n" +
                "    }\n" +
                "  }\n" +
                "]\n" +
                "\n" +
                "\n" +
                "date,copilot_ide_chat,,,,,,,,,total_active_users,copilot_dotcom_chat,total_engaged_users,copilot_dotcom_pull_requests,copilot_ide_code_completions,,,,,,,,,,,,,\n" +
                ",total_engaged_users,editors,,,,,,,,,total_engaged_users,,total_engaged_users,editors,,,,,,,,,,,languages,,total_engaged_users\n" +
                ",,name,models,,,,,,total_engaged_users,,,,,name,models,,,,,,,,,total_engaged_users,name,total_engaged_users,\n" +
                ",,,name,total_chats,is_custom_model,total_engaged_users,total_chat_copy_events,total_chat_insertion_events,,,,,,,name,languages,,,,,,is_custom_model,total_engaged_users,,,,\n" +
                ",,,,,,,,,,,,,,,,name,total_engaged_users,total_code_acceptances,total_code_suggestions,total_code_lines_accepted,total_code_lines_suggested,,,,,,\n" +
                "2025-03-17,0,,,,,,,,,1,0,1,0,JetBrains,default,json,1,1,1,1,1,false,1,1,json,1,1\n" +
                "2025-03-18,2,JetBrains,default,4,false,1,1,0,1,5,0,3,0,JetBrains,default,java,2,12,67,18,214,false,2,2,java,2,2\n" +
                ",,vscode,default,4,false,1,0,0,1,,,,,,,unknown,0,0,11,0,21,,,,unknown,0,\n" +
                ",,,,,,,,,,,,,,,,json,0,0,1,0,13,,,,json,0,\n" +
                "\n" +
                "\n" +
                "date      |copilot_ide_chat   |         |       |           |               |                   |                      |                           |                   |total_active_users|copilot_dotcom_chat|total_engaged_users|copilot_dotcom_pull_requests|copilot_ide_code_completions|       |         |                   |                      |                      |                         |                          |               |                   |                   |         |                   |                   \n" +
                "          |total_engaged_users|editors  |       |           |               |                   |                      |                           |                   |                  |total_engaged_users|                   |total_engaged_users         |editors                     |       |         |                   |                      |                      |                         |                          |               |                   |                   |languages|                   |total_engaged_users\n" +
                "          |                   |name     |models |           |               |                   |                      |                           |total_engaged_users|                  |                   |                   |                            |name                        |models |         |                   |                      |                      |                         |                          |               |                   |total_engaged_users|name     |total_engaged_users|                   \n" +
                "          |                   |         |name   |total_chats|is_custom_model|total_engaged_users|total_chat_copy_events|total_chat_insertion_events|                   |                  |                   |                   |                            |                            |name   |languages|                   |                      |                      |                         |                          |is_custom_model|total_engaged_users|                   |         |                   |                   \n" +
                "          |                   |         |       |           |               |                   |                      |                           |                   |                  |                   |                   |                            |                            |       |name     |total_engaged_users|total_code_acceptances|total_code_suggestions|total_code_lines_accepted|total_code_lines_suggested|               |                   |                   |         |                   |                   \n" +
                "-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------\n" +
                "2025-03-17|0                  |         |       |           |               |                   |                      |                           |                   |1                 |0                  |1                  |0                           |JetBrains                   |default|json     |1                  |1                     |1                     |1                        |1                         |false          |1                  |1                  |json     |1                  |1                  \n" +
                "2025-03-18|2                  |JetBrains|default|4          |false          |1                  |1                     |0                          |1                  |5                 |0                  |3                  |0                           |JetBrains                   |default|java     |2                  |12                    |67                    |18                       |214                       |false          |2                  |2                  |java     |2                  |2                  \n" +
                "          |                   |vscode   |default|4          |false          |1                  |0                     |0                          |1                  |                  |                   |                   |                            |                            |       |unknown  |0                  |0                     |11                    |0                        |21                        |               |                   |                   |unknown  |0                  |                   \n" +
                "          |                   |         |       |           |               |                   |                      |                           |                   |                  |                   |                   |                            |                            |       |json     |0                  |0                     |1                     |0                        |13                        |               |                   |                   |json     |0                  |                   \n");
    }

    @Test
    public void testJsonToCsv_partiallyFromDifferentLines() {
        assertR("[\n" +
                "  {\n" +
                "    \"date\": \"2025-03-17\",\n" +
                "    \"one\": {\n" +
                "      \"data1\": 0\n" +
                "    },\n" +
                "    \"data2\": 1,\n" +
                "    \"two\": {\n" +
                "      \"data3\": 0\n" +
                "    },\n" +
                "    \"data4\": 1,\n" +
                "    \"three\": {\n" +
                "      \"data5\": 0\n" +
                "    }\n" +
                "  },\n" +
                "  {\n" +
                "    \"date\": \"2025-03-18\",\n" +
                "    \"one\": {\n" +
                "      \"data6\": [\n" +
                "        {\n" +
                "          \"name\": \"JetBrains\"\n" +
                "        },\n" +
                "        {\n" +
                "          \"name\": \"vscode\"\n" +
                "        }\n" +
                "      ]\n" +
                "    },\n" +
                "    \"data2\": 5,\n" +
                "    \"two\": {\n" +
                "      \"data3\": 0\n" +
                "    },\n" +
                "    \"data4\": 3,\n" +
                "    \"three\": {\n" +
                "      \"data5\": 0\n" +
                "    }\n" +
                "  }\n" +
                "]\n" +
                "\n" +
                "\n" +
                "date,one,,data2,two,data4,three\n" +
                ",data1,data6,,data3,,data5\n" +
                ",,name,,,,\n" +
                "2025-03-17,0,,1,0,1,0\n" +
                "2025-03-18,,JetBrains,5,0,3,0\n" +
                ",,vscode,,,,\n" +
                "\n" +
                "\n" +
                "date      |one  |         |data2|two  |data4|three\n" +
                "          |data1|data6    |     |data3|     |data5\n" +
                "          |     |name     |     |     |     |     \n" +
                "--------------------------------------------------\n" +
                "2025-03-17|0    |         |1    |0    |1    |0    \n" +
                "2025-03-18|     |JetBrains|5    |0    |3    |0    \n" +
                "          |     |vscode   |     |     |     |     \n");
    }

    @Test
    public void testJsonToCsv_cornerCase() {
        assertR("[\n" +
                "  {\n" +
                "    \"date\": \"2025-03-17\",\n" +
                "    \"object\": {\n" +
                "      \"field1\": [\n" +
                "        {\n" +
                "          \"name\": \"field1_name\",\n" +
                "          \"array1\": [\n" +
                "            {\n" +
                "              \"name\": \"array1_name\",\n" +
                "              \"array2\": [\n" +
                "                {\n" +
                "                  \"name\": \"array2_name\",\n" +
                "                  \"data3\": 3\n" +
                "                }\n" +
                "              ],\n" +
                "              \"data4\": 4\n" +
                "            }\n" +
                "          ],\n" +
                "          \"data5\": 5\n" +
                "        }\n" +
                "      ],\n" +
                "      \"field2\": [\n" +
                "        {\n" +
                "          \"name\": \"field2_name\",\n" +
                "          \"data6\": 6\n" +
                "        }\n" +
                "      ],\n" +
                "      \"data7\": 7\n" +
                "    }\n" +
                "  }\n" +
                "]\n" +
                "\n" +
                "\n" +
                "date,object,,,,,,,,\n" +
                ",field1,,,,,,field2,,data7\n" +
                ",name,array1,,,,data5,name,data6,\n" +
                ",,name,array2,,data4,,,,\n" +
                ",,,name,data3,,,,,\n" +
                "2025-03-17,field1_name,array1_name,array2_name,3,4,5,field2_name,6,7\n" +
                "\n" +
                "\n" +
                "date      |object     |           |           |     |     |     |           |     |     \n" +
                "          |field1     |           |           |     |     |     |field2     |     |data7\n" +
                "          |name       |array1     |           |     |     |data5|name       |data6|     \n" +
                "          |           |name       |array2     |     |data4|     |           |     |     \n" +
                "          |           |           |name       |data3|     |     |           |     |     \n" +
                "----------------------------------------------------------------------------------------\n" +
                "2025-03-17|field1_name|array1_name|array2_name|3    |4    |5    |field2_name|6    |7    \n");
    }

    @Test
    public void testJsonToCsv_superComplex() {
        String json = "[{\"date\":\"2025-03-17\",\"copilot_ide_chat\":{\"total_engaged_users\":0},\"total_active_users\":1,\"copilot_dotcom_chat\":{\"total_engaged_users\":0},\"total_engaged_users\":1,\"copilot_dotcom_pull_requests\":{\"total_engaged_users\":0},\"copilot_ide_code_completions\":{\"editors\":[{\"name\":\"JetBrains\",\"models\":[{\"name\":\"default\",\"languages\":[{\"name\":\"json\",\"total_engaged_users\":1,\"total_code_acceptances\":1,\"total_code_suggestions\":1,\"total_code_lines_accepted\":1,\"total_code_lines_suggested\":1}],\"is_custom_model\":false,\"total_engaged_users\":1}],\"total_engaged_users\":1}],\"languages\":[{\"name\":\"json\",\"total_engaged_users\":1}],\"total_engaged_users\":1}},{\"date\":\"2025-03-18\",\"copilot_ide_chat\":{\"editors\":[{\"name\":\"JetBrains\",\"models\":[{\"name\":\"default\",\"total_chats\":4,\"is_custom_model\":false,\"total_engaged_users\":1,\"total_chat_copy_events\":1,\"total_chat_insertion_events\":0}],\"total_engaged_users\":1},{\"name\":\"vscode\",\"models\":[{\"name\":\"default\",\"total_chats\":4,\"is_custom_model\":false,\"total_engaged_users\":1,\"total_chat_copy_events\":0,\"total_chat_insertion_events\":0}],\"total_engaged_users\":1}],\"total_engaged_users\":2},\"total_active_users\":5,\"copilot_dotcom_chat\":{\"total_engaged_users\":0},\"total_engaged_users\":3,\"copilot_dotcom_pull_requests\":{\"total_engaged_users\":0},\"copilot_ide_code_completions\":{\"editors\":[{\"name\":\"JetBrains\",\"models\":[{\"name\":\"default\",\"languages\":[{\"name\":\"java\",\"total_engaged_users\":2,\"total_code_acceptances\":12,\"total_code_suggestions\":67,\"total_code_lines_accepted\":18,\"total_code_lines_suggested\":214},{\"name\":\"unknown\",\"total_engaged_users\":0,\"total_code_acceptances\":0,\"total_code_suggestions\":11,\"total_code_lines_accepted\":0,\"total_code_lines_suggested\":21},{\"name\":\"json\",\"total_engaged_users\":0,\"total_code_acceptances\":0,\"total_code_suggestions\":1,\"total_code_lines_accepted\":0,\"total_code_lines_suggested\":13}],\"is_custom_model\":false,\"total_engaged_users\":2}],\"total_engaged_users\":2}],\"languages\":[{\"name\":\"java\",\"total_engaged_users\":2},{\"name\":\"unknown\",\"total_engaged_users\":0},{\"name\":\"json\",\"total_engaged_users\":0}],\"total_engaged_users\":2}},{\"date\":\"2025-03-19\",\"copilot_ide_chat\":{\"editors\":[{\"name\":\"JetBrains\",\"models\":[{\"name\":\"default\",\"total_chats\":20,\"is_custom_model\":false,\"total_engaged_users\":3,\"total_chat_copy_events\":2,\"total_chat_insertion_events\":3}],\"total_engaged_users\":3},{\"name\":\"vscode\",\"models\":[{\"name\":\"default\",\"total_chats\":14,\"is_custom_model\":false,\"total_engaged_users\":1,\"total_chat_copy_events\":0,\"total_chat_insertion_events\":0}],\"total_engaged_users\":1}],\"total_engaged_users\":4},\"total_active_users\":5,\"copilot_dotcom_chat\":{\"total_engaged_users\":0},\"total_engaged_users\":5,\"copilot_dotcom_pull_requests\":{\"total_engaged_users\":0},\"copilot_ide_code_completions\":{\"editors\":[{\"name\":\"JetBrains\",\"models\":[{\"name\":\"default\",\"languages\":[{\"name\":\"java\",\"total_engaged_users\":2,\"total_code_acceptances\":39,\"total_code_suggestions\":103,\"total_code_lines_accepted\":75,\"total_code_lines_suggested\":185},{\"name\":\"unknown\",\"total_engaged_users\":1,\"total_code_acceptances\":15,\"total_code_suggestions\":24,\"total_code_lines_accepted\":17,\"total_code_lines_suggested\":41},{\"name\":\"json\",\"total_engaged_users\":1,\"total_code_acceptances\":10,\"total_code_suggestions\":13,\"total_code_lines_accepted\":11,\"total_code_lines_suggested\":26},{\"name\":\"yaml\",\"total_engaged_users\":1,\"total_code_acceptances\":3,\"total_code_suggestions\":4,\"total_code_lines_accepted\":6,\"total_code_lines_suggested\":10}],\"is_custom_model\":false,\"total_engaged_users\":3}],\"total_engaged_users\":3},{\"name\":\"vscode\",\"models\":[{\"name\":\"default\",\"languages\":[{\"name\":\"typescriptreact\",\"total_engaged_users\":1,\"total_code_acceptances\":5,\"total_code_suggestions\":25,\"total_code_lines_accepted\":1,\"total_code_lines_suggested\":31},{\"name\":\"typescript\",\"total_engaged_users\":1,\"total_code_acceptances\":12,\"total_code_suggestions\":58,\"total_code_lines_accepted\":9,\"total_code_lines_suggested\":81}],\"is_custom_model\":false,\"total_engaged_users\":1}],\"total_engaged_users\":1}],\"languages\":[{\"name\":\"java\",\"total_engaged_users\":2},{\"name\":\"typescriptreact\",\"total_engaged_users\":1},{\"name\":\"unknown\",\"total_engaged_users\":1},{\"name\":\"typescript\",\"total_engaged_users\":1},{\"name\":\"json\",\"total_engaged_users\":1},{\"name\":\"yaml\",\"total_engaged_users\":1}],\"total_engaged_users\":4}},{\"date\":\"2025-03-20\",\"copilot_ide_chat\":{\"editors\":[{\"name\":\"vscode\",\"models\":[{\"name\":\"default\",\"total_chats\":4,\"is_custom_model\":false,\"total_engaged_users\":1,\"total_chat_copy_events\":0,\"total_chat_insertion_events\":0}],\"total_engaged_users\":1},{\"name\":\"JetBrains\",\"models\":[{\"name\":\"default\",\"total_chats\":30,\"is_custom_model\":false,\"total_engaged_users\":3,\"total_chat_copy_events\":5,\"total_chat_insertion_events\":21}],\"total_engaged_users\":3}],\"total_engaged_users\":4},\"total_active_users\":5,\"copilot_dotcom_chat\":{\"total_engaged_users\":0},\"total_engaged_users\":5,\"copilot_dotcom_pull_requests\":{\"total_engaged_users\":0},\"copilot_ide_code_completions\":{\"editors\":[{\"name\":\"vscode\",\"models\":[{\"name\":\"default\",\"languages\":[{\"name\":\"typescript\",\"total_engaged_users\":1,\"total_code_acceptances\":23,\"total_code_suggestions\":86,\"total_code_lines_accepted\":13,\"total_code_lines_suggested\":118},{\"name\":\"typescriptreact\",\"total_engaged_users\":1,\"total_code_acceptances\":59,\"total_code_suggestions\":136,\"total_code_lines_accepted\":54,\"total_code_lines_suggested\":234},{\"name\":\"json\",\"total_engaged_users\":1,\"total_code_acceptances\":3,\"total_code_suggestions\":12,\"total_code_lines_accepted\":3,\"total_code_lines_suggested\":13}],\"is_custom_model\":false,\"total_engaged_users\":1}],\"total_engaged_users\":1},{\"name\":\"JetBrains\",\"models\":[{\"name\":\"default\",\"languages\":[{\"name\":\"java\",\"total_engaged_users\":3,\"total_code_acceptances\":12,\"total_code_suggestions\":37,\"total_code_lines_accepted\":26,\"total_code_lines_suggested\":88},{\"name\":\"unknown\",\"total_engaged_users\":1,\"total_code_acceptances\":3,\"total_code_suggestions\":13,\"total_code_lines_accepted\":4,\"total_code_lines_suggested\":28}],\"is_custom_model\":false,\"total_engaged_users\":3}],\"total_engaged_users\":3}],\"languages\":[{\"name\":\"typescript\",\"total_engaged_users\":1},{\"name\":\"java\",\"total_engaged_users\":3},{\"name\":\"typescriptreact\",\"total_engaged_users\":1},{\"name\":\"unknown\",\"total_engaged_users\":1},{\"name\":\"json\",\"total_engaged_users\":1}],\"total_engaged_users\":4}},{\"date\":\"2025-03-21\",\"copilot_ide_chat\":{\"editors\":[{\"name\":\"vscode\",\"models\":[{\"name\":\"default\",\"total_chats\":21,\"is_custom_model\":false,\"total_engaged_users\":2,\"total_chat_copy_events\":12,\"total_chat_insertion_events\":0}],\"total_engaged_users\":2},{\"name\":\"JetBrains\",\"models\":[{\"name\":\"default\",\"total_chats\":12,\"is_custom_model\":false,\"total_engaged_users\":3,\"total_chat_copy_events\":0,\"total_chat_insertion_events\":13}],\"total_engaged_users\":3}],\"total_engaged_users\":5},\"total_active_users\":6,\"copilot_dotcom_chat\":{\"total_engaged_users\":0},\"total_engaged_users\":6,\"copilot_dotcom_pull_requests\":{\"total_engaged_users\":0},\"copilot_ide_code_completions\":{\"editors\":[{\"name\":\"vscode\",\"models\":[{\"name\":\"default\",\"languages\":[{\"name\":\"typescript\",\"total_engaged_users\":1,\"total_code_acceptances\":59,\"total_code_suggestions\":238,\"total_code_lines_accepted\":49,\"total_code_lines_suggested\":385},{\"name\":\"typescriptreact\",\"total_engaged_users\":2,\"total_code_acceptances\":89,\"total_code_suggestions\":243,\"total_code_lines_accepted\":108,\"total_code_lines_suggested\":491},{\"name\":\"json\",\"total_engaged_users\":0,\"total_code_acceptances\":0,\"total_code_suggestions\":1,\"total_code_lines_accepted\":0,\"total_code_lines_suggested\":1}],\"is_custom_model\":false,\"total_engaged_users\":2}],\"total_engaged_users\":2},{\"name\":\"JetBrains\",\"models\":[{\"name\":\"default\",\"languages\":[{\"name\":\"java\",\"total_engaged_users\":2,\"total_code_acceptances\":10,\"total_code_suggestions\":39,\"total_code_lines_accepted\":15,\"total_code_lines_suggested\":85},{\"name\":\"unknown\",\"total_engaged_users\":2,\"total_code_acceptances\":45,\"total_code_suggestions\":92,\"total_code_lines_accepted\":48,\"total_code_lines_suggested\":129},{\"name\":\"json\",\"total_engaged_users\":2,\"total_code_acceptances\":5,\"total_code_suggestions\":12,\"total_code_lines_accepted\":5,\"total_code_lines_suggested\":26},{\"name\":\"yaml\",\"total_engaged_users\":0,\"total_code_acceptances\":0,\"total_code_suggestions\":4,\"total_code_lines_accepted\":0,\"total_code_lines_suggested\":4}],\"is_custom_model\":false,\"total_engaged_users\":4}],\"total_engaged_users\":4}],\"languages\":[{\"name\":\"typescript\",\"total_engaged_users\":1},{\"name\":\"typescriptreact\",\"total_engaged_users\":2},{\"name\":\"java\",\"total_engaged_users\":2},{\"name\":\"unknown\",\"total_engaged_users\":2},{\"name\":\"json\",\"total_engaged_users\":2},{\"name\":\"yaml\",\"total_engaged_users\":0}],\"total_engaged_users\":6}},{\"date\":\"2025-03-23\",\"copilot_ide_chat\":{\"editors\":[{\"name\":\"vscode\",\"models\":[{\"name\":\"default\",\"total_chats\":13,\"is_custom_model\":false,\"total_engaged_users\":1,\"total_chat_copy_events\":0,\"total_chat_insertion_events\":0}],\"total_engaged_users\":1}],\"total_engaged_users\":1},\"total_active_users\":1,\"copilot_dotcom_chat\":{\"total_engaged_users\":0},\"total_engaged_users\":1,\"copilot_dotcom_pull_requests\":{\"total_engaged_users\":0},\"copilot_ide_code_completions\":{\"editors\":[{\"name\":\"vscode\",\"models\":[{\"name\":\"default\",\"languages\":[{\"name\":\"typescriptreact\",\"total_engaged_users\":1,\"total_code_acceptances\":54,\"total_code_suggestions\":100,\"total_code_lines_accepted\":47,\"total_code_lines_suggested\":192}],\"is_custom_model\":false,\"total_engaged_users\":1}],\"total_engaged_users\":1}],\"languages\":[{\"name\":\"typescriptreact\",\"total_engaged_users\":1}],\"total_engaged_users\":1}},{\"date\":\"2025-03-24\",\"copilot_ide_chat\":{\"editors\":[{\"name\":\"JetBrains\",\"models\":[{\"name\":\"default\",\"total_chats\":16,\"is_custom_model\":false,\"total_engaged_users\":5,\"total_chat_copy_events\":15,\"total_chat_insertion_events\":10}],\"total_engaged_users\":5},{\"name\":\"vscode\",\"models\":[{\"name\":\"default\",\"total_chats\":12,\"is_custom_model\":false,\"total_engaged_users\":1,\"total_chat_copy_events\":0,\"total_chat_insertion_events\":0}],\"total_engaged_users\":1}],\"total_engaged_users\":6},\"total_active_users\":7,\"copilot_dotcom_chat\":{\"total_engaged_users\":0},\"total_engaged_users\":7,\"copilot_dotcom_pull_requests\":{\"total_engaged_users\":0},\"copilot_ide_code_completions\":{\"editors\":[{\"name\":\"JetBrains\",\"models\":[{\"name\":\"default\",\"languages\":[{\"name\":\"unknown\",\"total_engaged_users\":1,\"total_code_acceptances\":35,\"total_code_suggestions\":79,\"total_code_lines_accepted\":43,\"total_code_lines_suggested\":144},{\"name\":\"json\",\"total_engaged_users\":0,\"total_code_acceptances\":0,\"total_code_suggestions\":2,\"total_code_lines_accepted\":0,\"total_code_lines_suggested\":4},{\"name\":\"java\",\"total_engaged_users\":2,\"total_code_acceptances\":3,\"total_code_suggestions\":17,\"total_code_lines_accepted\":3,\"total_code_lines_suggested\":24},{\"name\":\"markdown\",\"total_engaged_users\":0,\"total_code_acceptances\":0,\"total_code_suggestions\":1,\"total_code_lines_accepted\":0,\"total_code_lines_suggested\":1},{\"name\":\"xml\",\"total_engaged_users\":1,\"total_code_acceptances\":1,\"total_code_suggestions\":4,\"total_code_lines_accepted\":1,\"total_code_lines_suggested\":5}],\"is_custom_model\":false,\"total_engaged_users\":2}],\"total_engaged_users\":2},{\"name\":\"vscode\",\"models\":[{\"name\":\"default\",\"languages\":[{\"name\":\"typescript\",\"total_engaged_users\":2,\"total_code_acceptances\":34,\"total_code_suggestions\":156,\"total_code_lines_accepted\":12,\"total_code_lines_suggested\":218},{\"name\":\"typescriptreact\",\"total_engaged_users\":2,\"total_code_acceptances\":61,\"total_code_suggestions\":205,\"total_code_lines_accepted\":70,\"total_code_lines_suggested\":396}],\"is_custom_model\":false,\"total_engaged_users\":2}],\"total_engaged_users\":2}],\"languages\":[{\"name\":\"unknown\",\"total_engaged_users\":1},{\"name\":\"typescript\",\"total_engaged_users\":2},{\"name\":\"typescriptreact\",\"total_engaged_users\":2},{\"name\":\"json\",\"total_engaged_users\":0},{\"name\":\"java\",\"total_engaged_users\":2},{\"name\":\"markdown\",\"total_engaged_users\":0},{\"name\":\"xml\",\"total_engaged_users\":1}],\"total_engaged_users\":4}},{\"date\":\"2025-03-25\",\"copilot_ide_chat\":{\"editors\":[{\"name\":\"vscode\",\"models\":[{\"name\":\"default\",\"total_chats\":20,\"is_custom_model\":false,\"total_engaged_users\":2,\"total_chat_copy_events\":2,\"total_chat_insertion_events\":0}],\"total_engaged_users\":2},{\"name\":\"JetBrains\",\"models\":[{\"name\":\"default\",\"total_chats\":27,\"is_custom_model\":false,\"total_engaged_users\":4,\"total_chat_copy_events\":10,\"total_chat_insertion_events\":10}],\"total_engaged_users\":4}],\"total_engaged_users\":6},\"total_active_users\":7,\"copilot_dotcom_chat\":{\"total_engaged_users\":0},\"total_engaged_users\":7,\"copilot_dotcom_pull_requests\":{\"total_engaged_users\":0},\"copilot_ide_code_completions\":{\"editors\":[{\"name\":\"JetBrains\",\"models\":[{\"name\":\"default\",\"languages\":[{\"name\":\"java\",\"total_engaged_users\":5,\"total_code_acceptances\":47,\"total_code_suggestions\":145,\"total_code_lines_accepted\":96,\"total_code_lines_suggested\":363},{\"name\":\"unknown\",\"total_engaged_users\":1,\"total_code_acceptances\":9,\"total_code_suggestions\":23,\"total_code_lines_accepted\":9,\"total_code_lines_suggested\":43},{\"name\":\"json\",\"total_engaged_users\":1,\"total_code_acceptances\":1,\"total_code_suggestions\":2,\"total_code_lines_accepted\":1,\"total_code_lines_suggested\":4}],\"is_custom_model\":false,\"total_engaged_users\":5}],\"total_engaged_users\":5},{\"name\":\"vscode\",\"models\":[{\"name\":\"default\",\"languages\":[{\"name\":\"typescriptreact\",\"total_engaged_users\":2,\"total_code_acceptances\":78,\"total_code_suggestions\":225,\"total_code_lines_accepted\":128,\"total_code_lines_suggested\":491},{\"name\":\"typescript\",\"total_engaged_users\":2,\"total_code_acceptances\":40,\"total_code_suggestions\":126,\"total_code_lines_accepted\":39,\"total_code_lines_suggested\":154}],\"is_custom_model\":false,\"total_engaged_users\":2}],\"total_engaged_users\":2}],\"languages\":[{\"name\":\"typescriptreact\",\"total_engaged_users\":2},{\"name\":\"java\",\"total_engaged_users\":5},{\"name\":\"typescript\",\"total_engaged_users\":2},{\"name\":\"unknown\",\"total_engaged_users\":1},{\"name\":\"json\",\"total_engaged_users\":1}],\"total_engaged_users\":7}},{\"date\":\"2025-03-26\",\"copilot_ide_chat\":{\"editors\":[{\"name\":\"vscode\",\"models\":[{\"name\":\"default\",\"total_chats\":14,\"is_custom_model\":false,\"total_engaged_users\":2,\"total_chat_copy_events\":2,\"total_chat_insertion_events\":0}],\"total_engaged_users\":2},{\"name\":\"JetBrains\",\"models\":[{\"name\":\"default\",\"total_chats\":19,\"is_custom_model\":false,\"total_engaged_users\":2,\"total_chat_copy_events\":8,\"total_chat_insertion_events\":5}],\"total_engaged_users\":2}],\"total_engaged_users\":4},\"total_active_users\":7,\"copilot_dotcom_chat\":{\"total_engaged_users\":0},\"total_engaged_users\":6,\"copilot_dotcom_pull_requests\":{\"total_engaged_users\":0},\"copilot_ide_code_completions\":{\"editors\":[{\"name\":\"vscode\",\"models\":[{\"name\":\"default\",\"languages\":[{\"name\":\"typescript\",\"total_engaged_users\":3,\"total_code_acceptances\":220,\"total_code_suggestions\":421,\"total_code_lines_accepted\":275,\"total_code_lines_suggested\":733},{\"name\":\"typescriptreact\",\"total_engaged_users\":2,\"total_code_acceptances\":151,\"total_code_suggestions\":392,\"total_code_lines_accepted\":157,\"total_code_lines_suggested\":582},{\"name\":\"unknown\",\"total_engaged_users\":1,\"total_code_acceptances\":2,\"total_code_suggestions\":20,\"total_code_lines_accepted\":14,\"total_code_lines_suggested\":167}],\"is_custom_model\":false,\"total_engaged_users\":3}],\"total_engaged_users\":3},{\"name\":\"JetBrains\",\"models\":[{\"name\":\"default\",\"languages\":[{\"name\":\"java\",\"total_engaged_users\":1,\"total_code_acceptances\":11,\"total_code_suggestions\":39,\"total_code_lines_accepted\":92,\"total_code_lines_suggested\":237},{\"name\":\"xml\",\"total_engaged_users\":1,\"total_code_acceptances\":1,\"total_code_suggestions\":9,\"total_code_lines_accepted\":1,\"total_code_lines_suggested\":9},{\"name\":\"json\",\"total_engaged_users\":0,\"total_code_acceptances\":0,\"total_code_suggestions\":2,\"total_code_lines_accepted\":0,\"total_code_lines_suggested\":2}],\"is_custom_model\":false,\"total_engaged_users\":2}],\"total_engaged_users\":2}],\"languages\":[{\"name\":\"typescript\",\"total_engaged_users\":3},{\"name\":\"java\",\"total_engaged_users\":1},{\"name\":\"typescriptreact\",\"total_engaged_users\":2},{\"name\":\"xml\",\"total_engaged_users\":1},{\"name\":\"unknown\",\"total_engaged_users\":1},{\"name\":\"json\",\"total_engaged_users\":0}],\"total_engaged_users\":5}},{\"date\":\"2025-03-27\",\"copilot_ide_chat\":{\"editors\":[{\"name\":\"vscode\",\"models\":[{\"name\":\"default\",\"total_chats\":26,\"is_custom_model\":false,\"total_engaged_users\":2,\"total_chat_copy_events\":0,\"total_chat_insertion_events\":0}],\"total_engaged_users\":2},{\"name\":\"JetBrains\",\"models\":[{\"name\":\"default\",\"total_chats\":25,\"is_custom_model\":false,\"total_engaged_users\":3,\"total_chat_copy_events\":11,\"total_chat_insertion_events\":9}],\"total_engaged_users\":3}],\"total_engaged_users\":5},\"total_active_users\":7,\"copilot_dotcom_chat\":{\"total_engaged_users\":0},\"total_engaged_users\":7,\"copilot_dotcom_pull_requests\":{\"total_engaged_users\":0},\"copilot_ide_code_completions\":{\"editors\":[{\"name\":\"JetBrains\",\"models\":[{\"name\":\"default\",\"languages\":[{\"name\":\"unknown\",\"total_engaged_users\":2,\"total_code_acceptances\":38,\"total_code_suggestions\":77,\"total_code_lines_accepted\":50,\"total_code_lines_suggested\":110},{\"name\":\"java\",\"total_engaged_users\":3,\"total_code_acceptances\":45,\"total_code_suggestions\":156,\"total_code_lines_accepted\":123,\"total_code_lines_suggested\":509}],\"is_custom_model\":false,\"total_engaged_users\":4}],\"total_engaged_users\":4},{\"name\":\"vscode\",\"models\":[{\"name\":\"default\",\"languages\":[{\"name\":\"typescriptreact\",\"total_engaged_users\":2,\"total_code_acceptances\":26,\"total_code_suggestions\":87,\"total_code_lines_accepted\":28,\"total_code_lines_suggested\":131},{\"name\":\"unknown\",\"total_engaged_users\":1,\"total_code_acceptances\":2,\"total_code_suggestions\":42,\"total_code_lines_accepted\":2,\"total_code_lines_suggested\":99},{\"name\":\"typescript\",\"total_engaged_users\":3,\"total_code_acceptances\":16,\"total_code_suggestions\":62,\"total_code_lines_accepted\":12,\"total_code_lines_suggested\":83}],\"is_custom_model\":false,\"total_engaged_users\":3}],\"total_engaged_users\":3}],\"languages\":[{\"name\":\"unknown\",\"total_engaged_users\":3},{\"name\":\"java\",\"total_engaged_users\":3},{\"name\":\"typescriptreact\",\"total_engaged_users\":2},{\"name\":\"typescript\",\"total_engaged_users\":3}],\"total_engaged_users\":7}},{\"date\":\"2025-03-28\",\"copilot_ide_chat\":{\"editors\":[{\"name\":\"vscode\",\"models\":[{\"name\":\"default\",\"total_chats\":7,\"is_custom_model\":false,\"total_engaged_users\":2,\"total_chat_copy_events\":0,\"total_chat_insertion_events\":0}],\"total_engaged_users\":2},{\"name\":\"JetBrains\",\"models\":[{\"name\":\"default\",\"total_chats\":18,\"is_custom_model\":false,\"total_engaged_users\":2,\"total_chat_copy_events\":2,\"total_chat_insertion_events\":18}],\"total_engaged_users\":2}],\"total_engaged_users\":4},\"total_active_users\":6,\"copilot_dotcom_chat\":{\"total_engaged_users\":0},\"total_engaged_users\":6,\"copilot_dotcom_pull_requests\":{\"total_engaged_users\":0},\"copilot_ide_code_completions\":{\"editors\":[{\"name\":\"JetBrains\",\"models\":[{\"name\":\"default\",\"languages\":[{\"name\":\"java\",\"total_engaged_users\":2,\"total_code_acceptances\":35,\"total_code_suggestions\":132,\"total_code_lines_accepted\":91,\"total_code_lines_suggested\":449},{\"name\":\"unknown\",\"total_engaged_users\":2,\"total_code_acceptances\":8,\"total_code_suggestions\":20,\"total_code_lines_accepted\":8,\"total_code_lines_suggested\":22},{\"name\":\"json\",\"total_engaged_users\":1,\"total_code_acceptances\":2,\"total_code_suggestions\":2,\"total_code_lines_accepted\":2,\"total_code_lines_suggested\":2}],\"is_custom_model\":false,\"total_engaged_users\":4}],\"total_engaged_users\":4},{\"name\":\"vscode\",\"models\":[{\"name\":\"default\",\"languages\":[{\"name\":\"feature\",\"total_engaged_users\":1,\"total_code_acceptances\":2,\"total_code_suggestions\":14,\"total_code_lines_accepted\":2,\"total_code_lines_suggested\":27},{\"name\":\"typescript\",\"total_engaged_users\":1,\"total_code_acceptances\":6,\"total_code_suggestions\":22,\"total_code_lines_accepted\":5,\"total_code_lines_suggested\":30}],\"is_custom_model\":false,\"total_engaged_users\":1}],\"total_engaged_users\":1}],\"languages\":[{\"name\":\"java\",\"total_engaged_users\":2},{\"name\":\"unknown\",\"total_engaged_users\":2},{\"name\":\"feature\",\"total_engaged_users\":1},{\"name\":\"typescript\",\"total_engaged_users\":1},{\"name\":\"json\",\"total_engaged_users\":1}],\"total_engaged_users\":5}},{\"date\":\"2025-03-31\",\"copilot_ide_chat\":{\"editors\":[{\"name\":\"vscode\",\"models\":[{\"name\":\"default\",\"total_chats\":8,\"is_custom_model\":false,\"total_engaged_users\":2,\"total_chat_copy_events\":0,\"total_chat_insertion_events\":0}],\"total_engaged_users\":2},{\"name\":\"JetBrains\",\"models\":[{\"name\":\"default\",\"total_chats\":16,\"is_custom_model\":false,\"total_engaged_users\":4,\"total_chat_copy_events\":5,\"total_chat_insertion_events\":13}],\"total_engaged_users\":4}],\"total_engaged_users\":6},\"total_active_users\":7,\"copilot_dotcom_chat\":{\"total_engaged_users\":0},\"total_engaged_users\":7,\"copilot_dotcom_pull_requests\":{\"total_engaged_users\":0},\"copilot_ide_code_completions\":{\"editors\":[{\"name\":\"vscode\",\"models\":[{\"name\":\"default\",\"languages\":[{\"name\":\"typescript\",\"total_engaged_users\":2,\"total_code_acceptances\":72,\"total_code_suggestions\":153,\"total_code_lines_accepted\":64,\"total_code_lines_suggested\":185},{\"name\":\"feature\",\"total_engaged_users\":0,\"total_code_acceptances\":0,\"total_code_suggestions\":10,\"total_code_lines_accepted\":0,\"total_code_lines_suggested\":32},{\"name\":\"csv\",\"total_engaged_users\":0,\"total_code_acceptances\":0,\"total_code_suggestions\":3,\"total_code_lines_accepted\":0,\"total_code_lines_suggested\":5},{\"name\":\"json\",\"total_engaged_users\":0,\"total_code_acceptances\":0,\"total_code_suggestions\":3,\"total_code_lines_accepted\":0,\"total_code_lines_suggested\":4}],\"is_custom_model\":false,\"total_engaged_users\":2}],\"total_engaged_users\":2},{\"name\":\"JetBrains\",\"models\":[{\"name\":\"default\",\"languages\":[{\"name\":\"java\",\"total_engaged_users\":4,\"total_code_acceptances\":41,\"total_code_suggestions\":168,\"total_code_lines_accepted\":95,\"total_code_lines_suggested\":460},{\"name\":\"unknown\",\"total_engaged_users\":1,\"total_code_acceptances\":2,\"total_code_suggestions\":9,\"total_code_lines_accepted\":2,\"total_code_lines_suggested\":10},{\"name\":\"json\",\"total_engaged_users\":0,\"total_code_acceptances\":0,\"total_code_suggestions\":1,\"total_code_lines_accepted\":0,\"total_code_lines_suggested\":1}],\"is_custom_model\":false,\"total_engaged_users\":4}],\"total_engaged_users\":4}],\"languages\":[{\"name\":\"typescript\",\"total_engaged_users\":2},{\"name\":\"java\",\"total_engaged_users\":4},{\"name\":\"feature\",\"total_engaged_users\":0},{\"name\":\"unknown\",\"total_engaged_users\":1},{\"name\":\"csv\",\"total_engaged_users\":0},{\"name\":\"json\",\"total_engaged_users\":0}],\"total_engaged_users\":6}},{\"date\":\"2025-04-01\",\"copilot_ide_chat\":{\"editors\":[{\"name\":\"JetBrains\",\"models\":[{\"name\":\"default\",\"total_chats\":20,\"is_custom_model\":false,\"total_engaged_users\":2,\"total_chat_copy_events\":4,\"total_chat_insertion_events\":21}],\"total_engaged_users\":2},{\"name\":\"vscode\",\"models\":[{\"name\":\"default\",\"total_chats\":10,\"is_custom_model\":false,\"total_engaged_users\":1,\"total_chat_copy_events\":0,\"total_chat_insertion_events\":0}],\"total_engaged_users\":1}],\"total_engaged_users\":3},\"total_active_users\":6,\"copilot_dotcom_chat\":{\"total_engaged_users\":0},\"total_engaged_users\":6,\"copilot_dotcom_pull_requests\":{\"total_engaged_users\":0},\"copilot_ide_code_completions\":{\"editors\":[{\"name\":\"vscode\",\"models\":[{\"name\":\"default\",\"languages\":[{\"name\":\"typescript\",\"total_engaged_users\":2,\"total_code_acceptances\":101,\"total_code_suggestions\":231,\"total_code_lines_accepted\":92,\"total_code_lines_suggested\":313},{\"name\":\"feature\",\"total_engaged_users\":1,\"total_code_acceptances\":2,\"total_code_suggestions\":21,\"total_code_lines_accepted\":0,\"total_code_lines_suggested\":74},{\"name\":\"csv\",\"total_engaged_users\":1,\"total_code_acceptances\":1,\"total_code_suggestions\":3,\"total_code_lines_accepted\":1,\"total_code_lines_suggested\":3}],\"is_custom_model\":false,\"total_engaged_users\":2}],\"total_engaged_users\":2},{\"name\":\"JetBrains\",\"models\":[{\"name\":\"default\",\"languages\":[{\"name\":\"java\",\"total_engaged_users\":3,\"total_code_acceptances\":53,\"total_code_suggestions\":273,\"total_code_lines_accepted\":86,\"total_code_lines_suggested\":912},{\"name\":\"unknown\",\"total_engaged_users\":2,\"total_code_acceptances\":3,\"total_code_suggestions\":7,\"total_code_lines_accepted\":3,\"total_code_lines_suggested\":11},{\"name\":\"json\",\"total_engaged_users\":0,\"total_code_acceptances\":0,\"total_code_suggestions\":3,\"total_code_lines_accepted\":0,\"total_code_lines_suggested\":4}],\"is_custom_model\":false,\"total_engaged_users\":3}],\"total_engaged_users\":3}],\"languages\":[{\"name\":\"typescript\",\"total_engaged_users\":2},{\"name\":\"java\",\"total_engaged_users\":3},{\"name\":\"feature\",\"total_engaged_users\":1},{\"name\":\"unknown\",\"total_engaged_users\":2},{\"name\":\"json\",\"total_engaged_users\":0},{\"name\":\"csv\",\"total_engaged_users\":1}],\"total_engaged_users\":5}},{\"date\":\"2025-04-02\",\"copilot_ide_chat\":{\"editors\":[{\"name\":\"vscode\",\"models\":[{\"name\":\"default\",\"total_chats\":51,\"is_custom_model\":false,\"total_engaged_users\":6,\"total_chat_copy_events\":12,\"total_chat_insertion_events\":0}],\"total_engaged_users\":6},{\"name\":\"JetBrains\",\"models\":[{\"name\":\"default\",\"total_chats\":11,\"is_custom_model\":false,\"total_engaged_users\":3,\"total_chat_copy_events\":9,\"total_chat_insertion_events\":1}],\"total_engaged_users\":3}],\"total_engaged_users\":9},\"total_active_users\":9,\"copilot_dotcom_chat\":{\"total_engaged_users\":0},\"total_engaged_users\":9,\"copilot_dotcom_pull_requests\":{\"total_engaged_users\":0},\"copilot_ide_code_completions\":{\"editors\":[{\"name\":\"vscode\",\"models\":[{\"name\":\"default\",\"languages\":[{\"name\":\"typescript\",\"total_engaged_users\":2,\"total_code_acceptances\":96,\"total_code_suggestions\":221,\"total_code_lines_accepted\":103,\"total_code_lines_suggested\":332},{\"name\":\"typescriptreact\",\"total_engaged_users\":1,\"total_code_acceptances\":14,\"total_code_suggestions\":57,\"total_code_lines_accepted\":16,\"total_code_lines_suggested\":127},{\"name\":\"feature\",\"total_engaged_users\":1,\"total_code_acceptances\":1,\"total_code_suggestions\":25,\"total_code_lines_accepted\":2,\"total_code_lines_suggested\":70},{\"name\":\"json\",\"total_engaged_users\":0,\"total_code_acceptances\":0,\"total_code_suggestions\":7,\"total_code_lines_accepted\":0,\"total_code_lines_suggested\":9},{\"name\":\"java\",\"total_engaged_users\":1,\"total_code_acceptances\":1,\"total_code_suggestions\":5,\"total_code_lines_accepted\":0,\"total_code_lines_suggested\":7}],\"is_custom_model\":false,\"total_engaged_users\":4}],\"total_engaged_users\":4},{\"name\":\"JetBrains\",\"models\":[{\"name\":\"default\",\"languages\":[{\"name\":\"java\",\"total_engaged_users\":3,\"total_code_acceptances\":54,\"total_code_suggestions\":244,\"total_code_lines_accepted\":89,\"total_code_lines_suggested\":626},{\"name\":\"yaml\",\"total_engaged_users\":1,\"total_code_acceptances\":5,\"total_code_suggestions\":6,\"total_code_lines_accepted\":17,\"total_code_lines_suggested\":18},{\"name\":\"unknown\",\"total_engaged_users\":1,\"total_code_acceptances\":3,\"total_code_suggestions\":7,\"total_code_lines_accepted\":3,\"total_code_lines_suggested\":7},{\"name\":\"json\",\"total_engaged_users\":0,\"total_code_acceptances\":0,\"total_code_suggestions\":1,\"total_code_lines_accepted\":0,\"total_code_lines_suggested\":2}],\"is_custom_model\":false,\"total_engaged_users\":4}],\"total_engaged_users\":4}],\"languages\":[{\"name\":\"typescript\",\"total_engaged_users\":2},{\"name\":\"java\",\"total_engaged_users\":4},{\"name\":\"typescriptreact\",\"total_engaged_users\":1},{\"name\":\"feature\",\"total_engaged_users\":1},{\"name\":\"yaml\",\"total_engaged_users\":1},{\"name\":\"json\",\"total_engaged_users\":0},{\"name\":\"unknown\",\"total_engaged_users\":1}],\"total_engaged_users\":7}},{\"date\":\"2025-04-03\",\"copilot_ide_chat\":{\"editors\":[{\"name\":\"JetBrains\",\"models\":[{\"name\":\"default\",\"total_chats\":18,\"is_custom_model\":false,\"total_engaged_users\":4,\"total_chat_copy_events\":5,\"total_chat_insertion_events\":6}],\"total_engaged_users\":4},{\"name\":\"vscode\",\"models\":[{\"name\":\"default\",\"total_chats\":52,\"is_custom_model\":false,\"total_engaged_users\":4,\"total_chat_copy_events\":6,\"total_chat_insertion_events\":1}],\"total_engaged_users\":4}],\"total_engaged_users\":8},\"total_active_users\":8,\"copilot_dotcom_chat\":{\"total_engaged_users\":0},\"total_engaged_users\":8,\"copilot_dotcom_pull_requests\":{\"total_engaged_users\":0},\"copilot_ide_code_completions\":{\"editors\":[{\"name\":\"vscode\",\"models\":[{\"name\":\"default\",\"languages\":[{\"name\":\"typescript\",\"total_engaged_users\":3,\"total_code_acceptances\":108,\"total_code_suggestions\":250,\"total_code_lines_accepted\":170,\"total_code_lines_suggested\":418},{\"name\":\"typescriptreact\",\"total_engaged_users\":2,\"total_code_acceptances\":37,\"total_code_suggestions\":165,\"total_code_lines_accepted\":33,\"total_code_lines_suggested\":303},{\"name\":\"feature\",\"total_engaged_users\":1,\"total_code_acceptances\":1,\"total_code_suggestions\":22,\"total_code_lines_accepted\":1,\"total_code_lines_suggested\":38},{\"name\":\"dotenv\",\"total_engaged_users\":0,\"total_code_acceptances\":0,\"total_code_suggestions\":2,\"total_code_lines_accepted\":0,\"total_code_lines_suggested\":2}],\"is_custom_model\":false,\"total_engaged_users\":3}],\"total_engaged_users\":3},{\"name\":\"JetBrains\",\"models\":[{\"name\":\"default\",\"languages\":[{\"name\":\"java\",\"total_engaged_users\":3,\"total_code_acceptances\":26,\"total_code_suggestions\":111,\"total_code_lines_accepted\":37,\"total_code_lines_suggested\":210},{\"name\":\"unknown\",\"total_engaged_users\":1,\"total_code_acceptances\":1,\"total_code_suggestions\":18,\"total_code_lines_accepted\":1,\"total_code_lines_suggested\":58}],\"is_custom_model\":false,\"total_engaged_users\":3}],\"total_engaged_users\":3}],\"languages\":[{\"name\":\"typescript\",\"total_engaged_users\":3},{\"name\":\"java\",\"total_engaged_users\":3},{\"name\":\"typescriptreact\",\"total_engaged_users\":2},{\"name\":\"feature\",\"total_engaged_users\":1},{\"name\":\"unknown\",\"total_engaged_users\":1},{\"name\":\"dotenv\",\"total_engaged_users\":0}],\"total_engaged_users\":6}}]\n";
        assertR(json +
                "\n" +
                "\n" +
                "date,copilot_ide_chat,,,,,,,,,total_active_users,copilot_dotcom_chat,total_engaged_users,copilot_dotcom_pull_requests,copilot_ide_code_completions,,,,,,,,,,,,,\n" +
                ",total_engaged_users,editors,,,,,,,,,total_engaged_users,,total_engaged_users,editors,,,,,,,,,,,languages,,total_engaged_users\n" +
                ",,name,models,,,,,,total_engaged_users,,,,,name,models,,,,,,,,,total_engaged_users,name,total_engaged_users,\n" +
                ",,,name,total_chats,is_custom_model,total_engaged_users,total_chat_copy_events,total_chat_insertion_events,,,,,,,name,languages,,,,,,is_custom_model,total_engaged_users,,,,\n" +
                ",,,,,,,,,,,,,,,,name,total_engaged_users,total_code_acceptances,total_code_suggestions,total_code_lines_accepted,total_code_lines_suggested,,,,,,\n" +
                "2025-03-17,0,,,,,,,,,1,0,1,0,JetBrains,default,json,1,1,1,1,1,false,1,1,json,1,1\n" +
                "2025-03-18,2,JetBrains,default,4,false,1,1,0,1,5,0,3,0,JetBrains,default,java,2,12,67,18,214,false,2,2,java,2,2\n" +
                ",,vscode,default,4,false,1,0,0,1,,,,,,,unknown,0,0,11,0,21,,,,unknown,0,\n" +
                ",,,,,,,,,,,,,,,,json,0,0,1,0,13,,,,json,0,\n" +
                "2025-03-19,4,JetBrains,default,20,false,3,2,3,3,5,0,5,0,JetBrains,default,java,2,39,103,75,185,false,3,3,java,2,4\n" +
                ",,vscode,default,14,false,1,0,0,1,,,,,vscode,default,typescriptreact,1,5,25,1,31,,,,typescriptreact,1,\n" +
                ",,,,,,,,,,,,,,,,typescript,1,12,58,9,81,false,1,1,unknown,1,\n" +
                ",,,,,,,,,,,,,,,,yaml,1,3,4,6,10,,,,typescript,1,\n" +
                ",,,,,,,,,,,,,,,,,,,,,,,,,json,1,\n" +
                ",,,,,,,,,,,,,,,,,,,,,,,,,yaml,1,\n" +
                "2025-03-20,4,vscode,default,4,false,1,0,0,1,5,0,5,0,vscode,default,typescript,1,23,86,13,118,false,1,1,typescript,1,4\n" +
                ",,JetBrains,default,30,false,3,5,21,3,,,,,JetBrains,default,java,3,12,37,26,88,,,,java,3,\n" +
                ",,,,,,,,,,,,,,,,unknown,1,3,13,4,28,false,3,3,typescriptreact,1,\n" +
                ",,,,,,,,,,,,,,,,,,,,,,,,,unknown,1,\n" +
                ",,,,,,,,,,,,,,,,,,,,,,,,,json,1,\n" +
                "2025-03-21,5,vscode,default,21,false,2,12,0,2,6,0,6,0,vscode,default,typescript,1,59,238,49,385,false,2,2,typescript,1,6\n" +
                ",,JetBrains,default,12,false,3,0,13,3,,,,,JetBrains,default,java,2,10,39,15,85,,,,typescriptreact,2,\n" +
                ",,,,,,,,,,,,,,,,unknown,2,45,92,48,129,,,,java,2,\n" +
                ",,,,,,,,,,,,,,,,json,2,5,12,5,26,,,,unknown,2,\n" +
                ",,,,,,,,,,,,,,,,yaml,0,0,4,0,4,false,4,4,json,2,\n" +
                ",,,,,,,,,,,,,,,,,,,,,,,,,yaml,0,\n" +
                "2025-03-23,1,vscode,default,13,false,1,0,0,1,1,0,1,0,vscode,default,typescriptreact,1,54,100,47,192,false,1,1,typescriptreact,1,1\n" +
                "2025-03-24,6,JetBrains,default,16,false,5,15,10,5,7,0,7,0,JetBrains,default,unknown,1,35,79,43,144,false,2,2,unknown,1,4\n" +
                ",,vscode,default,12,false,1,0,0,1,,,,,vscode,default,typescript,2,34,156,12,218,,,,typescript,2,\n" +
                ",,,,,,,,,,,,,,,,typescriptreact,2,61,205,70,396,false,2,2,typescriptreact,2,\n" +
                ",,,,,,,,,,,,,,,,markdown,0,0,1,0,1,,,,json,0,\n" +
                ",,,,,,,,,,,,,,,,xml,1,1,4,1,5,,,,java,2,\n" +
                ",,,,,,,,,,,,,,,,,,,,,,,,,markdown,0,\n" +
                ",,,,,,,,,,,,,,,,,,,,,,,,,xml,1,\n" +
                "2025-03-25,6,vscode,default,20,false,2,2,0,2,7,0,7,0,JetBrains,default,java,5,47,145,96,363,false,5,5,typescriptreact,2,7\n" +
                ",,JetBrains,default,27,false,4,10,10,4,,,,,vscode,default,typescriptreact,2,78,225,128,491,,,,java,5,\n" +
                ",,,,,,,,,,,,,,,,typescript,2,40,126,39,154,false,2,2,typescript,2,\n" +
                ",,,,,,,,,,,,,,,,,,,,,,,,,unknown,1,\n" +
                ",,,,,,,,,,,,,,,,,,,,,,,,,json,1,\n" +
                "2025-03-26,4,vscode,default,14,false,2,2,0,2,7,0,6,0,vscode,default,typescript,3,220,421,275,733,false,3,3,typescript,3,5\n" +
                ",,JetBrains,default,19,false,2,8,5,2,,,,,JetBrains,default,java,1,11,39,92,237,,,,java,1,\n" +
                ",,,,,,,,,,,,,,,,xml,1,1,9,1,9,,,,typescriptreact,2,\n" +
                ",,,,,,,,,,,,,,,,json,0,0,2,0,2,false,2,2,xml,1,\n" +
                ",,,,,,,,,,,,,,,,,,,,,,,,,unknown,1,\n" +
                ",,,,,,,,,,,,,,,,,,,,,,,,,json,0,\n" +
                "2025-03-27,5,vscode,default,26,false,2,0,0,2,7,0,7,0,JetBrains,default,unknown,2,38,77,50,110,false,4,4,unknown,3,7\n" +
                ",,JetBrains,default,25,false,3,11,9,3,,,,,vscode,default,typescriptreact,2,26,87,28,131,,,,java,3,\n" +
                ",,,,,,,,,,,,,,,,unknown,1,2,42,2,99,,,,typescriptreact,2,\n" +
                ",,,,,,,,,,,,,,,,typescript,3,16,62,12,83,false,3,3,typescript,3,\n" +
                "2025-03-28,4,vscode,default,7,false,2,0,0,2,6,0,6,0,JetBrains,default,java,2,35,132,91,449,false,4,4,java,2,5\n" +
                ",,JetBrains,default,18,false,2,2,18,2,,,,,vscode,default,feature,1,2,14,2,27,,,,unknown,2,\n" +
                ",,,,,,,,,,,,,,,,typescript,1,6,22,5,30,false,1,1,feature,1,\n" +
                ",,,,,,,,,,,,,,,,,,,,,,,,,typescript,1,\n" +
                ",,,,,,,,,,,,,,,,,,,,,,,,,json,1,\n" +
                "2025-03-31,6,vscode,default,8,false,2,0,0,2,7,0,7,0,vscode,default,typescript,2,72,153,64,185,false,2,2,typescript,2,6\n" +
                ",,JetBrains,default,16,false,4,5,13,4,,,,,JetBrains,default,java,4,41,168,95,460,,,,java,4,\n" +
                ",,,,,,,,,,,,,,,,unknown,1,2,9,2,10,,,,feature,0,\n" +
                ",,,,,,,,,,,,,,,,json,0,0,1,0,1,false,4,4,unknown,1,\n" +
                ",,,,,,,,,,,,,,,,,,,,,,,,,csv,0,\n" +
                ",,,,,,,,,,,,,,,,,,,,,,,,,json,0,\n" +
                "2025-04-01,3,JetBrains,default,20,false,2,4,21,2,6,0,6,0,vscode,default,typescript,2,101,231,92,313,false,2,2,typescript,2,5\n" +
                ",,vscode,default,10,false,1,0,0,1,,,,,JetBrains,default,java,3,53,273,86,912,,,,java,3,\n" +
                ",,,,,,,,,,,,,,,,unknown,2,3,7,3,11,,,,feature,1,\n" +
                ",,,,,,,,,,,,,,,,json,0,0,3,0,4,false,3,3,unknown,2,\n" +
                ",,,,,,,,,,,,,,,,,,,,,,,,,json,0,\n" +
                ",,,,,,,,,,,,,,,,,,,,,,,,,csv,1,\n" +
                "2025-04-02,9,vscode,default,51,false,6,12,0,6,9,0,9,0,vscode,default,typescript,2,96,221,103,332,false,4,4,typescript,2,7\n" +
                ",,JetBrains,default,11,false,3,9,1,3,,,,,JetBrains,default,java,3,54,244,89,626,,,,java,4,\n" +
                ",,,,,,,,,,,,,,,,yaml,1,5,6,17,18,,,,typescriptreact,1,\n" +
                ",,,,,,,,,,,,,,,,unknown,1,3,7,3,7,,,,feature,1,\n" +
                ",,,,,,,,,,,,,,,,json,0,0,1,0,2,false,4,4,yaml,1,\n" +
                ",,,,,,,,,,,,,,,,,,,,,,,,,json,0,\n" +
                ",,,,,,,,,,,,,,,,,,,,,,,,,unknown,1,\n" +
                "2025-04-03,8,JetBrains,default,18,false,4,5,6,4,8,0,8,0,vscode,default,typescript,3,108,250,170,418,false,3,3,typescript,3,6\n" +
                ",,vscode,default,52,false,4,6,1,4,,,,,JetBrains,default,java,3,26,111,37,210,,,,java,3,\n" +
                ",,,,,,,,,,,,,,,,unknown,1,1,18,1,58,false,3,3,typescriptreact,2,\n" +
                ",,,,,,,,,,,,,,,,dotenv,0,0,2,0,2,,,,feature,1,\n" +
                ",,,,,,,,,,,,,,,,,,,,,,,,,unknown,1,\n" +
                ",,,,,,,,,,,,,,,,,,,,,,,,,dotenv,0,\n" +
                "\n" +
                "\n" +
                "date      |copilot_ide_chat   |         |       |           |               |                   |                      |                           |                   |total_active_users|copilot_dotcom_chat|total_engaged_users|copilot_dotcom_pull_requests|copilot_ide_code_completions|       |               |                   |                      |                      |                         |                          |               |                   |                   |               |                   |                   \n" +
                "          |total_engaged_users|editors  |       |           |               |                   |                      |                           |                   |                  |total_engaged_users|                   |total_engaged_users         |editors                     |       |               |                   |                      |                      |                         |                          |               |                   |                   |languages      |                   |total_engaged_users\n" +
                "          |                   |name     |models |           |               |                   |                      |                           |total_engaged_users|                  |                   |                   |                            |name                        |models |               |                   |                      |                      |                         |                          |               |                   |total_engaged_users|name           |total_engaged_users|                   \n" +
                "          |                   |         |name   |total_chats|is_custom_model|total_engaged_users|total_chat_copy_events|total_chat_insertion_events|                   |                  |                   |                   |                            |                            |name   |languages      |                   |                      |                      |                         |                          |is_custom_model|total_engaged_users|                   |               |                   |                   \n" +
                "          |                   |         |       |           |               |                   |                      |                           |                   |                  |                   |                   |                            |                            |       |name           |total_engaged_users|total_code_acceptances|total_code_suggestions|total_code_lines_accepted|total_code_lines_suggested|               |                   |                   |               |                   |                   \n" +
                "-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------\n" +
                "2025-03-17|0                  |         |       |           |               |                   |                      |                           |                   |1                 |0                  |1                  |0                           |JetBrains                   |default|json           |1                  |1                     |1                     |1                        |1                         |false          |1                  |1                  |json           |1                  |1                  \n" +
                "2025-03-18|2                  |JetBrains|default|4          |false          |1                  |1                     |0                          |1                  |5                 |0                  |3                  |0                           |JetBrains                   |default|java           |2                  |12                    |67                    |18                       |214                       |false          |2                  |2                  |java           |2                  |2                  \n" +
                "          |                   |vscode   |default|4          |false          |1                  |0                     |0                          |1                  |                  |                   |                   |                            |                            |       |unknown        |0                  |0                     |11                    |0                        |21                        |               |                   |                   |unknown        |0                  |                   \n" +
                "          |                   |         |       |           |               |                   |                      |                           |                   |                  |                   |                   |                            |                            |       |json           |0                  |0                     |1                     |0                        |13                        |               |                   |                   |json           |0                  |                   \n" +
                "2025-03-19|4                  |JetBrains|default|20         |false          |3                  |2                     |3                          |3                  |5                 |0                  |5                  |0                           |JetBrains                   |default|java           |2                  |39                    |103                   |75                       |185                       |false          |3                  |3                  |java           |2                  |4                  \n" +
                "          |                   |vscode   |default|14         |false          |1                  |0                     |0                          |1                  |                  |                   |                   |                            |vscode                      |default|typescriptreact|1                  |5                     |25                    |1                        |31                        |               |                   |                   |typescriptreact|1                  |                   \n" +
                "          |                   |         |       |           |               |                   |                      |                           |                   |                  |                   |                   |                            |                            |       |typescript     |1                  |12                    |58                    |9                        |81                        |false          |1                  |1                  |unknown        |1                  |                   \n" +
                "          |                   |         |       |           |               |                   |                      |                           |                   |                  |                   |                   |                            |                            |       |yaml           |1                  |3                     |4                     |6                        |10                        |               |                   |                   |typescript     |1                  |                   \n" +
                "          |                   |         |       |           |               |                   |                      |                           |                   |                  |                   |                   |                            |                            |       |               |                   |                      |                      |                         |                          |               |                   |                   |json           |1                  |                   \n" +
                "          |                   |         |       |           |               |                   |                      |                           |                   |                  |                   |                   |                            |                            |       |               |                   |                      |                      |                         |                          |               |                   |                   |yaml           |1                  |                   \n" +
                "2025-03-20|4                  |vscode   |default|4          |false          |1                  |0                     |0                          |1                  |5                 |0                  |5                  |0                           |vscode                      |default|typescript     |1                  |23                    |86                    |13                       |118                       |false          |1                  |1                  |typescript     |1                  |4                  \n" +
                "          |                   |JetBrains|default|30         |false          |3                  |5                     |21                         |3                  |                  |                   |                   |                            |JetBrains                   |default|java           |3                  |12                    |37                    |26                       |88                        |               |                   |                   |java           |3                  |                   \n" +
                "          |                   |         |       |           |               |                   |                      |                           |                   |                  |                   |                   |                            |                            |       |unknown        |1                  |3                     |13                    |4                        |28                        |false          |3                  |3                  |typescriptreact|1                  |                   \n" +
                "          |                   |         |       |           |               |                   |                      |                           |                   |                  |                   |                   |                            |                            |       |               |                   |                      |                      |                         |                          |               |                   |                   |unknown        |1                  |                   \n" +
                "          |                   |         |       |           |               |                   |                      |                           |                   |                  |                   |                   |                            |                            |       |               |                   |                      |                      |                         |                          |               |                   |                   |json           |1                  |                   \n" +
                "2025-03-21|5                  |vscode   |default|21         |false          |2                  |12                    |0                          |2                  |6                 |0                  |6                  |0                           |vscode                      |default|typescript     |1                  |59                    |238                   |49                       |385                       |false          |2                  |2                  |typescript     |1                  |6                  \n" +
                "          |                   |JetBrains|default|12         |false          |3                  |0                     |13                         |3                  |                  |                   |                   |                            |JetBrains                   |default|java           |2                  |10                    |39                    |15                       |85                        |               |                   |                   |typescriptreact|2                  |                   \n" +
                "          |                   |         |       |           |               |                   |                      |                           |                   |                  |                   |                   |                            |                            |       |unknown        |2                  |45                    |92                    |48                       |129                       |               |                   |                   |java           |2                  |                   \n" +
                "          |                   |         |       |           |               |                   |                      |                           |                   |                  |                   |                   |                            |                            |       |json           |2                  |5                     |12                    |5                        |26                        |               |                   |                   |unknown        |2                  |                   \n" +
                "          |                   |         |       |           |               |                   |                      |                           |                   |                  |                   |                   |                            |                            |       |yaml           |0                  |0                     |4                     |0                        |4                         |false          |4                  |4                  |json           |2                  |                   \n" +
                "          |                   |         |       |           |               |                   |                      |                           |                   |                  |                   |                   |                            |                            |       |               |                   |                      |                      |                         |                          |               |                   |                   |yaml           |0                  |                   \n" +
                "2025-03-23|1                  |vscode   |default|13         |false          |1                  |0                     |0                          |1                  |1                 |0                  |1                  |0                           |vscode                      |default|typescriptreact|1                  |54                    |100                   |47                       |192                       |false          |1                  |1                  |typescriptreact|1                  |1                  \n" +
                "2025-03-24|6                  |JetBrains|default|16         |false          |5                  |15                    |10                         |5                  |7                 |0                  |7                  |0                           |JetBrains                   |default|unknown        |1                  |35                    |79                    |43                       |144                       |false          |2                  |2                  |unknown        |1                  |4                  \n" +
                "          |                   |vscode   |default|12         |false          |1                  |0                     |0                          |1                  |                  |                   |                   |                            |vscode                      |default|typescript     |2                  |34                    |156                   |12                       |218                       |               |                   |                   |typescript     |2                  |                   \n" +
                "          |                   |         |       |           |               |                   |                      |                           |                   |                  |                   |                   |                            |                            |       |typescriptreact|2                  |61                    |205                   |70                       |396                       |false          |2                  |2                  |typescriptreact|2                  |                   \n" +
                "          |                   |         |       |           |               |                   |                      |                           |                   |                  |                   |                   |                            |                            |       |markdown       |0                  |0                     |1                     |0                        |1                         |               |                   |                   |json           |0                  |                   \n" +
                "          |                   |         |       |           |               |                   |                      |                           |                   |                  |                   |                   |                            |                            |       |xml            |1                  |1                     |4                     |1                        |5                         |               |                   |                   |java           |2                  |                   \n" +
                "          |                   |         |       |           |               |                   |                      |                           |                   |                  |                   |                   |                            |                            |       |               |                   |                      |                      |                         |                          |               |                   |                   |markdown       |0                  |                   \n" +
                "          |                   |         |       |           |               |                   |                      |                           |                   |                  |                   |                   |                            |                            |       |               |                   |                      |                      |                         |                          |               |                   |                   |xml            |1                  |                   \n" +
                "2025-03-25|6                  |vscode   |default|20         |false          |2                  |2                     |0                          |2                  |7                 |0                  |7                  |0                           |JetBrains                   |default|java           |5                  |47                    |145                   |96                       |363                       |false          |5                  |5                  |typescriptreact|2                  |7                  \n" +
                "          |                   |JetBrains|default|27         |false          |4                  |10                    |10                         |4                  |                  |                   |                   |                            |vscode                      |default|typescriptreact|2                  |78                    |225                   |128                      |491                       |               |                   |                   |java           |5                  |                   \n" +
                "          |                   |         |       |           |               |                   |                      |                           |                   |                  |                   |                   |                            |                            |       |typescript     |2                  |40                    |126                   |39                       |154                       |false          |2                  |2                  |typescript     |2                  |                   \n" +
                "          |                   |         |       |           |               |                   |                      |                           |                   |                  |                   |                   |                            |                            |       |               |                   |                      |                      |                         |                          |               |                   |                   |unknown        |1                  |                   \n" +
                "          |                   |         |       |           |               |                   |                      |                           |                   |                  |                   |                   |                            |                            |       |               |                   |                      |                      |                         |                          |               |                   |                   |json           |1                  |                   \n" +
                "2025-03-26|4                  |vscode   |default|14         |false          |2                  |2                     |0                          |2                  |7                 |0                  |6                  |0                           |vscode                      |default|typescript     |3                  |220                   |421                   |275                      |733                       |false          |3                  |3                  |typescript     |3                  |5                  \n" +
                "          |                   |JetBrains|default|19         |false          |2                  |8                     |5                          |2                  |                  |                   |                   |                            |JetBrains                   |default|java           |1                  |11                    |39                    |92                       |237                       |               |                   |                   |java           |1                  |                   \n" +
                "          |                   |         |       |           |               |                   |                      |                           |                   |                  |                   |                   |                            |                            |       |xml            |1                  |1                     |9                     |1                        |9                         |               |                   |                   |typescriptreact|2                  |                   \n" +
                "          |                   |         |       |           |               |                   |                      |                           |                   |                  |                   |                   |                            |                            |       |json           |0                  |0                     |2                     |0                        |2                         |false          |2                  |2                  |xml            |1                  |                   \n" +
                "          |                   |         |       |           |               |                   |                      |                           |                   |                  |                   |                   |                            |                            |       |               |                   |                      |                      |                         |                          |               |                   |                   |unknown        |1                  |                   \n" +
                "          |                   |         |       |           |               |                   |                      |                           |                   |                  |                   |                   |                            |                            |       |               |                   |                      |                      |                         |                          |               |                   |                   |json           |0                  |                   \n" +
                "2025-03-27|5                  |vscode   |default|26         |false          |2                  |0                     |0                          |2                  |7                 |0                  |7                  |0                           |JetBrains                   |default|unknown        |2                  |38                    |77                    |50                       |110                       |false          |4                  |4                  |unknown        |3                  |7                  \n" +
                "          |                   |JetBrains|default|25         |false          |3                  |11                    |9                          |3                  |                  |                   |                   |                            |vscode                      |default|typescriptreact|2                  |26                    |87                    |28                       |131                       |               |                   |                   |java           |3                  |                   \n" +
                "          |                   |         |       |           |               |                   |                      |                           |                   |                  |                   |                   |                            |                            |       |unknown        |1                  |2                     |42                    |2                        |99                        |               |                   |                   |typescriptreact|2                  |                   \n" +
                "          |                   |         |       |           |               |                   |                      |                           |                   |                  |                   |                   |                            |                            |       |typescript     |3                  |16                    |62                    |12                       |83                        |false          |3                  |3                  |typescript     |3                  |                   \n" +
                "2025-03-28|4                  |vscode   |default|7          |false          |2                  |0                     |0                          |2                  |6                 |0                  |6                  |0                           |JetBrains                   |default|java           |2                  |35                    |132                   |91                       |449                       |false          |4                  |4                  |java           |2                  |5                  \n" +
                "          |                   |JetBrains|default|18         |false          |2                  |2                     |18                         |2                  |                  |                   |                   |                            |vscode                      |default|feature        |1                  |2                     |14                    |2                        |27                        |               |                   |                   |unknown        |2                  |                   \n" +
                "          |                   |         |       |           |               |                   |                      |                           |                   |                  |                   |                   |                            |                            |       |typescript     |1                  |6                     |22                    |5                        |30                        |false          |1                  |1                  |feature        |1                  |                   \n" +
                "          |                   |         |       |           |               |                   |                      |                           |                   |                  |                   |                   |                            |                            |       |               |                   |                      |                      |                         |                          |               |                   |                   |typescript     |1                  |                   \n" +
                "          |                   |         |       |           |               |                   |                      |                           |                   |                  |                   |                   |                            |                            |       |               |                   |                      |                      |                         |                          |               |                   |                   |json           |1                  |                   \n" +
                "2025-03-31|6                  |vscode   |default|8          |false          |2                  |0                     |0                          |2                  |7                 |0                  |7                  |0                           |vscode                      |default|typescript     |2                  |72                    |153                   |64                       |185                       |false          |2                  |2                  |typescript     |2                  |6                  \n" +
                "          |                   |JetBrains|default|16         |false          |4                  |5                     |13                         |4                  |                  |                   |                   |                            |JetBrains                   |default|java           |4                  |41                    |168                   |95                       |460                       |               |                   |                   |java           |4                  |                   \n" +
                "          |                   |         |       |           |               |                   |                      |                           |                   |                  |                   |                   |                            |                            |       |unknown        |1                  |2                     |9                     |2                        |10                        |               |                   |                   |feature        |0                  |                   \n" +
                "          |                   |         |       |           |               |                   |                      |                           |                   |                  |                   |                   |                            |                            |       |json           |0                  |0                     |1                     |0                        |1                         |false          |4                  |4                  |unknown        |1                  |                   \n" +
                "          |                   |         |       |           |               |                   |                      |                           |                   |                  |                   |                   |                            |                            |       |               |                   |                      |                      |                         |                          |               |                   |                   |csv            |0                  |                   \n" +
                "          |                   |         |       |           |               |                   |                      |                           |                   |                  |                   |                   |                            |                            |       |               |                   |                      |                      |                         |                          |               |                   |                   |json           |0                  |                   \n" +
                "2025-04-01|3                  |JetBrains|default|20         |false          |2                  |4                     |21                         |2                  |6                 |0                  |6                  |0                           |vscode                      |default|typescript     |2                  |101                   |231                   |92                       |313                       |false          |2                  |2                  |typescript     |2                  |5                  \n" +
                "          |                   |vscode   |default|10         |false          |1                  |0                     |0                          |1                  |                  |                   |                   |                            |JetBrains                   |default|java           |3                  |53                    |273                   |86                       |912                       |               |                   |                   |java           |3                  |                   \n" +
                "          |                   |         |       |           |               |                   |                      |                           |                   |                  |                   |                   |                            |                            |       |unknown        |2                  |3                     |7                     |3                        |11                        |               |                   |                   |feature        |1                  |                   \n" +
                "          |                   |         |       |           |               |                   |                      |                           |                   |                  |                   |                   |                            |                            |       |json           |0                  |0                     |3                     |0                        |4                         |false          |3                  |3                  |unknown        |2                  |                   \n" +
                "          |                   |         |       |           |               |                   |                      |                           |                   |                  |                   |                   |                            |                            |       |               |                   |                      |                      |                         |                          |               |                   |                   |json           |0                  |                   \n" +
                "          |                   |         |       |           |               |                   |                      |                           |                   |                  |                   |                   |                            |                            |       |               |                   |                      |                      |                         |                          |               |                   |                   |csv            |1                  |                   \n" +
                "2025-04-02|9                  |vscode   |default|51         |false          |6                  |12                    |0                          |6                  |9                 |0                  |9                  |0                           |vscode                      |default|typescript     |2                  |96                    |221                   |103                      |332                       |false          |4                  |4                  |typescript     |2                  |7                  \n" +
                "          |                   |JetBrains|default|11         |false          |3                  |9                     |1                          |3                  |                  |                   |                   |                            |JetBrains                   |default|java           |3                  |54                    |244                   |89                       |626                       |               |                   |                   |java           |4                  |                   \n" +
                "          |                   |         |       |           |               |                   |                      |                           |                   |                  |                   |                   |                            |                            |       |yaml           |1                  |5                     |6                     |17                       |18                        |               |                   |                   |typescriptreact|1                  |                   \n" +
                "          |                   |         |       |           |               |                   |                      |                           |                   |                  |                   |                   |                            |                            |       |unknown        |1                  |3                     |7                     |3                        |7                         |               |                   |                   |feature        |1                  |                   \n" +
                "          |                   |         |       |           |               |                   |                      |                           |                   |                  |                   |                   |                            |                            |       |json           |0                  |0                     |1                     |0                        |2                         |false          |4                  |4                  |yaml           |1                  |                   \n" +
                "          |                   |         |       |           |               |                   |                      |                           |                   |                  |                   |                   |                            |                            |       |               |                   |                      |                      |                         |                          |               |                   |                   |json           |0                  |                   \n" +
                "          |                   |         |       |           |               |                   |                      |                           |                   |                  |                   |                   |                            |                            |       |               |                   |                      |                      |                         |                          |               |                   |                   |unknown        |1                  |                   \n" +
                "2025-04-03|8                  |JetBrains|default|18         |false          |4                  |5                     |6                          |4                  |8                 |0                  |8                  |0                           |vscode                      |default|typescript     |3                  |108                   |250                   |170                      |418                       |false          |3                  |3                  |typescript     |3                  |6                  \n" +
                "          |                   |vscode   |default|52         |false          |4                  |6                     |1                          |4                  |                  |                   |                   |                            |JetBrains                   |default|java           |3                  |26                    |111                   |37                       |210                       |               |                   |                   |java           |3                  |                   \n" +
                "          |                   |         |       |           |               |                   |                      |                           |                   |                  |                   |                   |                            |                            |       |unknown        |1                  |1                     |18                    |1                        |58                        |false          |3                  |3                  |typescriptreact|2                  |                   \n" +
                "          |                   |         |       |           |               |                   |                      |                           |                   |                  |                   |                   |                            |                            |       |dotenv         |0                  |0                     |2                     |0                        |2                         |               |                   |                   |feature        |1                  |                   \n" +
                "          |                   |         |       |           |               |                   |                      |                           |                   |                  |                   |                   |                            |                            |       |               |                   |                      |                      |                         |                          |               |                   |                   |unknown        |1                  |                   \n" +
                "          |                   |         |       |           |               |                   |                      |                           |                   |                  |                   |                   |                            |                            |       |               |                   |                      |                      |                         |                          |               |                   |                   |dotenv         |0                  |                   \n");
    }

    @Test
    public void performance() {
        long start = System.currentTimeMillis();
        for (int i = 0; i < 100000; i++) {
            testJsonToCsv_superComplex2();
        }
        long end = System.currentTimeMillis();
        System.out.println("Performance test took: " + (end - start) + " ms");
    }

    @Test
    public void testJsonToCsv_superComplex2() {
        String json = "[\n" +
                "  {\n" +
                "    \"date\" : \"2025-03-17\",\n" +
                "    \"total_active_users\" : 1,\n" +
                "    \"total_engaged_users\" : 1,\n" +
                "    \"copilot_ide_chat\" : {\n" +
                "      \"total_engaged_users\" : 0\n" +
                "    },\n" +
                "    \"copilot_dotcom_chat\" : {\n" +
                "      \"total_engaged_users\" : 0\n" +
                "    },\n" +
                "    \"copilot_dotcom_pull_requests\" : {\n" +
                "      \"total_engaged_users\" : 0\n" +
                "    },\n" +
                "    \"copilot_ide_code_completions\" : {\n" +
                "      \"editors\" : [\n" +
                "        {\n" +
                "          \"models\" : [\n" +
                "            {\n" +
                "              \"is_custom_model\" : false,\n" +
                "              \"languages\" : [\n" +
                "                {\n" +
                "                  \"name\" : \"json\",\n" +
                "                  \"total_code_acceptances\" : 1,\n" +
                "                  \"total_code_lines_accepted\" : 1,\n" +
                "                  \"total_code_lines_suggested\" : 1,\n" +
                "                  \"total_code_suggestions\" : 1,\n" +
                "                  \"total_engaged_users\" : 1\n" +
                "                }\n" +
                "              ],\n" +
                "              \"name\" : \"default\",\n" +
                "              \"total_engaged_users\" : 1\n" +
                "            }\n" +
                "          ],\n" +
                "          \"name\" : \"JetBrains\",\n" +
                "          \"total_engaged_users\" : 1\n" +
                "        }\n" +
                "      ],\n" +
                "      \"languages\" : [\n" +
                "        {\n" +
                "          \"name\" : \"json\",\n" +
                "          \"total_engaged_users\" : 1\n" +
                "        }\n" +
                "      ],\n" +
                "      \"total_engaged_users\" : 1\n" +
                "    }\n" +
                "  },\n" +
                "  {\n" +
                "    \"date\" : \"2025-03-18\",\n" +
                "    \"total_active_users\" : 5,\n" +
                "    \"total_engaged_users\" : 3,\n" +
                "    \"copilot_ide_chat\" : {\n" +
                "      \"editors\" : [\n" +
                "        {\n" +
                "          \"models\" : [\n" +
                "            {\n" +
                "              \"is_custom_model\" : false,\n" +
                "              \"name\" : \"default\",\n" +
                "              \"total_chat_copy_events\" : 1,\n" +
                "              \"total_chat_insertion_events\" : 0,\n" +
                "              \"total_chats\" : 4,\n" +
                "              \"total_engaged_users\" : 1\n" +
                "            }\n" +
                "          ],\n" +
                "          \"name\" : \"JetBrains\",\n" +
                "          \"total_engaged_users\" : 1\n" +
                "        },\n" +
                "        {\n" +
                "          \"models\" : [\n" +
                "            {\n" +
                "              \"is_custom_model\" : false,\n" +
                "              \"name\" : \"default\",\n" +
                "              \"total_chat_copy_events\" : 0,\n" +
                "              \"total_chat_insertion_events\" : 0,\n" +
                "              \"total_chats\" : 4,\n" +
                "              \"total_engaged_users\" : 1\n" +
                "            }\n" +
                "          ],\n" +
                "          \"name\" : \"vscode\",\n" +
                "          \"total_engaged_users\" : 1\n" +
                "        }\n" +
                "      ],\n" +
                "      \"total_engaged_users\" : 2\n" +
                "    },\n" +
                "    \"copilot_dotcom_chat\" : {\n" +
                "      \"total_engaged_users\" : 0\n" +
                "    },\n" +
                "    \"copilot_dotcom_pull_requests\" : {\n" +
                "      \"total_engaged_users\" : 0\n" +
                "    },\n" +
                "    \"copilot_ide_code_completions\" : {\n" +
                "      \"editors\" : [\n" +
                "        {\n" +
                "          \"models\" : [\n" +
                "            {\n" +
                "              \"is_custom_model\" : false,\n" +
                "              \"languages\" : [\n" +
                "                {\n" +
                "                  \"name\" : \"java\",\n" +
                "                  \"total_code_acceptances\" : 12,\n" +
                "                  \"total_code_lines_accepted\" : 18,\n" +
                "                  \"total_code_lines_suggested\" : 214,\n" +
                "                  \"total_code_suggestions\" : 67,\n" +
                "                  \"total_engaged_users\" : 2\n" +
                "                },\n" +
                "                {\n" +
                "                  \"name\" : \"json\",\n" +
                "                  \"total_code_acceptances\" : 0,\n" +
                "                  \"total_code_lines_accepted\" : 0,\n" +
                "                  \"total_code_lines_suggested\" : 13,\n" +
                "                  \"total_code_suggestions\" : 1,\n" +
                "                  \"total_engaged_users\" : 0\n" +
                "                },\n" +
                "                {\n" +
                "                  \"name\" : \"unknown\",\n" +
                "                  \"total_code_acceptances\" : 0,\n" +
                "                  \"total_code_lines_accepted\" : 0,\n" +
                "                  \"total_code_lines_suggested\" : 21,\n" +
                "                  \"total_code_suggestions\" : 11,\n" +
                "                  \"total_engaged_users\" : 0\n" +
                "                }\n" +
                "              ],\n" +
                "              \"name\" : \"default\",\n" +
                "              \"total_engaged_users\" : 2\n" +
                "            }\n" +
                "          ],\n" +
                "          \"name\" : \"JetBrains\",\n" +
                "          \"total_engaged_users\" : 2\n" +
                "        }\n" +
                "      ],\n" +
                "      \"languages\" : [\n" +
                "        {\n" +
                "          \"name\" : \"java\",\n" +
                "          \"total_engaged_users\" : 2\n" +
                "        },\n" +
                "        {\n" +
                "          \"name\" : \"json\",\n" +
                "          \"total_engaged_users\" : 0\n" +
                "        },\n" +
                "        {\n" +
                "          \"name\" : \"unknown\",\n" +
                "          \"total_engaged_users\" : 0\n" +
                "        }\n" +
                "      ],\n" +
                "      \"total_engaged_users\" : 2\n" +
                "    }\n" +
                "  }\n" +
                "]\n";

        assertR(json +
                "\n" +
                "\n" +
                "date,total_active_users,total_engaged_users,copilot_ide_chat,,,,,,,,,copilot_dotcom_chat,copilot_dotcom_pull_requests,copilot_ide_code_completions,,,,,,,,,,,,,\n" +
                ",,,total_engaged_users,editors,,,,,,,,total_engaged_users,total_engaged_users,editors,,,,,,,,,,,languages,,total_engaged_users\n" +
                ",,,,models,,,,,,name,total_engaged_users,,,models,,,,,,,,,name,total_engaged_users,name,total_engaged_users,\n" +
                ",,,,is_custom_model,name,total_chat_copy_events,total_chat_insertion_events,total_chats,total_engaged_users,,,,,is_custom_model,languages,,,,,,name,total_engaged_users,,,,,\n" +
                ",,,,,,,,,,,,,,,name,total_code_acceptances,total_code_lines_accepted,total_code_lines_suggested,total_code_suggestions,total_engaged_users,,,,,,,\n" +
                "2025-03-17,1,1,0,,,,,,,,,0,0,false,json,1,1,1,1,1,default,1,JetBrains,1,json,1,1\n" +
                "2025-03-18,5,3,2,false,default,0,0,4,1,vscode,1,0,0,false,java,12,18,214,67,2,default,2,JetBrains,2,java,2,2\n" +
                ",,,,,,,,,,,,,,,json,0,0,13,1,0,,,,,json,0,\n" +
                ",,,,,,,,,,,,,,,unknown,0,0,21,11,0,,,,,unknown,0,\n" +
                "\n" +
                "\n" +
                "date      |total_active_users|total_engaged_users|copilot_ide_chat   |               |       |                      |                           |           |                   |      |                   |copilot_dotcom_chat|copilot_dotcom_pull_requests|copilot_ide_code_completions|         |                      |                         |                          |                      |                   |       |                   |         |                   |         |                   |                   \n" +
                "          |                  |                   |total_engaged_users|editors        |       |                      |                           |           |                   |      |                   |total_engaged_users|total_engaged_users         |editors                     |         |                      |                         |                          |                      |                   |       |                   |         |                   |languages|                   |total_engaged_users\n" +
                "          |                  |                   |                   |models         |       |                      |                           |           |                   |name  |total_engaged_users|                   |                            |models                      |         |                      |                         |                          |                      |                   |       |                   |name     |total_engaged_users|name     |total_engaged_users|                   \n" +
                "          |                  |                   |                   |is_custom_model|name   |total_chat_copy_events|total_chat_insertion_events|total_chats|total_engaged_users|      |                   |                   |                            |is_custom_model             |languages|                      |                         |                          |                      |                   |name   |total_engaged_users|         |                   |         |                   |                   \n" +
                "          |                  |                   |                   |               |       |                      |                           |           |                   |      |                   |                   |                            |                            |name     |total_code_acceptances|total_code_lines_accepted|total_code_lines_suggested|total_code_suggestions|total_engaged_users|       |                   |         |                   |         |                   |                   \n" +
                "--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------\n" +
                "2025-03-17|1                 |1                  |0                  |               |       |                      |                           |           |                   |      |                   |0                  |0                           |false                       |json     |1                     |1                        |1                         |1                     |1                  |default|1                  |JetBrains|1                  |json     |1                  |1                  \n" +
                "2025-03-18|5                 |3                  |2                  |false          |default|0                     |0                          |4          |1                  |vscode|1                  |0                  |0                           |false                       |java     |12                    |18                       |214                       |67                    |2                  |default|2                  |JetBrains|2                  |java     |2                  |2                  \n" +
                "          |                  |                   |                   |               |       |                      |                           |           |                   |      |                   |                   |                            |                            |json     |0                     |0                        |13                        |1                     |0                  |       |                   |         |                   |json     |0                  |                   \n" +
                "          |                  |                   |                   |               |       |                      |                           |           |                   |      |                   |                   |                            |                            |unknown  |0                     |0                        |21                        |11                    |0                  |       |                   |         |                   |unknown  |0                  |                   \n");
    }

    public void assertR(String expected) {
        String input = expected.split("\n\n")[0];
        String actual = input + "\n\n\n" +
                JsonToCsv.jsonToCsv(input) + "\n\n" +
                JsonToCsv.jsonToMarkdown(input);
        assertEquals(expected, actual);
    }
}