#!/usr/bin/env python3

import sys
import os
sys.path.append('../../../')

from mcp_server.pipeline.expressions import evaluate_expression, substitute_expressions

def test_dual_expressions():
    # Test data
    variables = {
        'all_file_contents': [
            [{'name': 'file1', 'value': 1}, {'name': 'file2', 'value': 2}],
            [{'name': 'file3', 'value': 3}]
        ],
        'simple_var': 'hello world',
        'number_var': 42,
        'list_numbers': [1, 2, 3, 4, 5],
        'nested_obj': {'level1': {'level2': {'value': 'deep_value'}}}
    }
    
    print("=== Testing Dual Expression System ===\n")
    
    # Test 1: Python expression (flattening nested list)
    print("Test 1: Python list flattening")
    py_expr = "[! [item for sublist in all_file_contents for item in sublist] !]"
    try:
        result = evaluate_expression(py_expr, variables, expected_result_type="python")
        print(f"Expression: {py_expr}")
        print(f"Result: {result}")
        print(f"Result type: {type(result)}")
        print(f"Length: {len(result) if hasattr(result, '__len__') else 'N/A'}")
        assert len(result) == 3, f"Expected 3 items, got {len(result)}"
        print("✅ PASSED")
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Test 2: JavaScript expression (simple variable)
    print("Test 2: JavaScript simple variable")
    js_expr = "{! simple_var !}"
    try:
        result = evaluate_expression(js_expr, variables, expected_result_type="python")
        print(f"Expression: {js_expr}")
        print(f"Result: {result}")
        print(f"Result type: {type(result)}")
        assert result == "hello world", f"Expected 'hello world', got {result}"
        print("✅ PASSED")
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Test 3: Python simple variable
    print("Test 3: Python simple variable")
    py_expr = "[! simple_var !]"
    try:
        result = evaluate_expression(py_expr, variables, expected_result_type="python")
        print(f"Expression: {py_expr}")
        print(f"Result: {result}")
        print(f"Result type: {type(result)}")
        assert result == "hello world", f"Expected 'hello world', got {result}"
        print("✅ PASSED")
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Test 4: JavaScript expression (JSON.stringify)
    print("Test 4: JavaScript JSON.stringify")
    js_expr = "{! JSON.stringify(all_file_contents) !}"
    try:
        result = evaluate_expression(js_expr, variables, expected_result_type="python")
        print(f"Expression: {js_expr}")
        print(f"Result: {result}")
        print(f"Result type: {type(result)}")
        assert isinstance(result, str), f"Expected string result, got {type(result)}"
        print("✅ PASSED")
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    print("\n" + "="*50 + "\n")
    
    # Test 5: Python expression with len()
    print("Test 5: Python len() function")
    py_expr = "[! len(all_file_contents) !]"
    try:
        result = evaluate_expression(py_expr, variables, expected_result_type="python")
        print(f"Expression: {py_expr}")
        print(f"Result: {result}")
        print(f"Result type: {type(result)}")
        assert result == 2, f"Expected 2, got {result}"
        print("✅ PASSED")
    except Exception as e:
        print(f"❌ ERROR: {e}")

def test_advanced_expressions():
    """Test more complex expression scenarios"""
    variables = {
        'numbers': [1, 2, 3, 4, 5],
        'text': 'Hello World Testing',
        'score': 85,
        'items': [
            {'name': 'item1', 'price': 10.5, 'category': 'A'},
            {'name': 'item2', 'price': 25.0, 'category': 'B'},
            {'name': 'item3', 'price': 15.5, 'category': 'A'}
        ]
    }
    
    print("=== Testing Advanced Expressions ===\n")
    
    # Test 6: JavaScript ternary operator
    print("Test 6: JavaScript ternary operator")
    js_expr = "{! score >= 90 ? 'Excellent' : 'Good' !}"
    try:
        result = evaluate_expression(js_expr, variables, expected_result_type="python")
        print(f"Expression: {js_expr}")
        print(f"Result: {result}")
        assert result == "Good", f"Expected 'Good', got {result}"
        print("✅ PASSED")
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    print("\n" + "-"*30 + "\n")
    
    # Test 7: Python filter and sum
    print("Test 7: Python filter and sum")
    py_expr = "[! sum(item['price'] for item in items if item['category'] == 'A') !]"
    try:
        result = evaluate_expression(py_expr, variables, expected_result_type="python")
        print(f"Expression: {py_expr}")
        print(f"Result: {result}")
        assert result == 26.0, f"Expected 26.0, got {result}"
        print("✅ PASSED")
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    print("\n" + "-"*30 + "\n")
    
    # Test 8: JavaScript array operations
    print("Test 8: JavaScript array operations")
    js_expr = "{! numbers.filter(n => n > 3).reduce((a, b) => a + b, 0) !}"
    try:
        result = evaluate_expression(js_expr, variables, expected_result_type="python")
        print(f"Expression: {js_expr}")
        print(f"Result: {result}")
        assert result == 9, f"Expected 9 (4+5), got {result}"
        print("✅ PASSED")
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    print("\n" + "-"*30 + "\n")
    
    # Test 9: Complex nested access
    print("Test 9: Complex nested data access")
    nested_vars = {
        'data': {
            'users': [
                {'id': 1, 'profile': {'name': 'Alice', 'settings': {'theme': 'dark'}}},
                {'id': 2, 'profile': {'name': 'Bob', 'settings': {'theme': 'light'}}}
            ]
        }
    }
    js_expr = "{! data.users.find(u => u.id === 2).profile.name !}"
    try:
        result = evaluate_expression(js_expr, nested_vars, expected_result_type="python")
        print(f"Expression: {js_expr}")
        print(f"Result: {result}")
        assert result == "Bob", f"Expected 'Bob', got {result}"
        print("✅ PASSED")
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    print("\n" + "-"*30 + "\n")
    
    # Test 10: Python equivalent of nested access
    print("Test 10: Python nested access")
    py_expr = "[! data['users'][1]['profile']['name'] !]"  # Direct access to second user (index 1)
    try:
        result = evaluate_expression(py_expr, nested_vars, expected_result_type="python")
        print(f"Expression: {py_expr}")
        print(f"Result: {result}")
        assert result == "Bob", f"Expected 'Bob', got {result}"
        print("✅ PASSED")
    except Exception as e:
        print(f"❌ ERROR: {e}")

def test_substitution_expressions():
    """Test string substitution with expressions"""
    variables = {
        'name': 'Alice',
        'age': 30,
        'skills': ['Python', 'JavaScript', 'SQL'],
        'score': 95
    }
    
    print("=== Testing Expression Substitution ===\n")
    
    # Test 11: Mixed expressions in text
    print("Test 11: Mixed expression substitution")
    text = "Hello {! name !}, you are [! age !] years old and have {! skills.length !} skills. Grade: {! score >= 90 ? 'A' : 'B' !}"
    try:
        result = substitute_expressions(text, variables, expected_result_type="python")
        print(f"Template: {text}")
        print(f"Result: {result}")
        expected = "Hello Alice, you are 30 years old and have 3 skills. Grade: A"
        assert result == expected, f"Expected '{expected}', got '{result}'"
        print("✅ PASSED")
    except Exception as e:
        print(f"❌ ERROR: {e}")
    
    print("\n" + "-"*30 + "\n")
    
    # Test 12: JSON result type
    print("Test 12: JSON result type")
    py_expr = "[! skills[:2] !]"  # First 2 skills
    try:
        result = evaluate_expression(py_expr, variables, expected_result_type="json")
        print(f"Expression: {py_expr}")
        print(f"Result: {result}")
        print(f"Result type: {type(result)}")
        assert isinstance(result, str), f"Expected string (JSON), got {type(result)}"
        import json
        parsed = json.loads(result)
        assert parsed == ['Python', 'JavaScript'], f"Expected ['Python', 'JavaScript'], got {parsed}"
        print("✅ PASSED")
    except Exception as e:
        print(f"❌ ERROR: {e}")

def test_error_handling():
    """Test error handling scenarios"""
    variables = {'valid_var': 42}
    
    print("=== Testing Error Handling ===\n")
    
    # Test 13: Invalid JavaScript
    print("Test 13: Invalid JavaScript syntax")
    try:
        result = evaluate_expression("{! invalid.syntax.. !}", variables, expected_result_type="python")
        print(f"❌ ERROR: Should have failed but got: {result}")
    except Exception as e:
        print(f"✅ PASSED: Correctly caught error: {type(e).__name__}")
    
    print("\n" + "-"*30 + "\n")
    
    # Test 14: Invalid Python
    print("Test 14: Invalid Python syntax")
    try:
        result = evaluate_expression("[! invalid syntax here !]", variables, expected_result_type="python")
        print(f"❌ ERROR: Should have failed but got: {result}")
    except Exception as e:
        print(f"✅ PASSED: Correctly caught error: {type(e).__name__}")
    
    print("\n" + "-"*30 + "\n")
    
    # Test 15: Undefined variable
    print("Test 15: Undefined variable")
    try:
        result = evaluate_expression("{! undefined_var !}", variables, expected_result_type="python")
        print(f"❌ ERROR: Should have failed but got: {result}")
    except Exception as e:
        print(f"✅ PASSED: Correctly caught error: {type(e).__name__}")

def run_all_tests():
    """Run all test suites"""
    print("🚀 Starting Comprehensive Expression Tests\n")
    
    try:
        test_dual_expressions()
        print("\n" + "="*70 + "\n")
        
        test_advanced_expressions()
        print("\n" + "="*70 + "\n")
        
        test_substitution_expressions()
        print("\n" + "="*70 + "\n")
        
        test_error_handling()
        
        print("\n🎉 All test suites completed!")
        print("Check output above for individual test results.")
        
    except Exception as e:
        print(f"💥 Test suite failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_all_tests()
