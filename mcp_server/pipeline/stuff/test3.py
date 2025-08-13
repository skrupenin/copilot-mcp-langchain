#!/usr/bin/env python3

import sys
import os
sys.path.append('../../../')

from mcp_server.pipeline.expressions import evaluate_expression

def get_test_context():
    """Get test context - all native Python objects"""
    return {
        'users': ['Alice', 'Bob', 'Charlie'],
        'config': {'debug': True, 'timeout': 30},
        'count': 5,
        'message': 'Hello World',
        'is_active': True,
        'data': None,
        'nested': {
            'items': [
                {'name': 'item1', 'value': 10},
                {'name': 'item2', 'value': 20}
            ]
        }
    }

def test_javascript_to_python():
    """Test 1: JavaScript expressions returning Python objects"""
    print("🧪 Test 1: JavaScript {!  !} expressions → Python objects")
    print("-" * 50)
    
    context = get_test_context()
    tests = [
        ("{! users !}", ['Alice', 'Bob', 'Charlie']),
        ("{! users.length !}", 3),  
        ("{! config.debug !}", True),
        ("{! count > 3 !}", True),
        ("{! message + ' - ' + users[0] !}", "Hello World - Alice"),
        ("{! nested.items.map(x => x.value).reduce((a,b) => a+b, 0) !}", 30),
    ]
    
    for expr, expected in tests:
        try:
            result = evaluate_expression(expr, context, "python")
            print(f"  {expr:<50} → {result} ({type(result).__name__})")
            assert result == expected, f"Expected {expected}, got {result}"
        except Exception as e:
            print(f"  {expr:<50} → ERROR: {e}")
            raise
    print("✅ PASSED: All JavaScript → Python tests\n")

def test_javascript_to_json():
    """Test 2: JavaScript expressions returning JSON strings"""
    print("🧪 Test 2: JavaScript {!  !} expressions → JSON strings")
    print("-" * 50)
    
    context = get_test_context()
    tests = [
        ("{! users !}", '["Alice", "Bob", "Charlie"]'),
        ("{! users.length !}", '3'),  
        ("{! config.debug !}", 'true'),
        ("{! count > 3 !}", 'true'),
        ("{! message + ' - ' + users[0] !}", '"Hello World - Alice"'),
        ("{! nested.items.map(x => x.value).reduce((a,b) => a+b, 0) !}", '30'),
    ]
    
    for expr, expected in tests:
        try:
            result = evaluate_expression(expr, context, "json") 
            print(f"  {expr:<50} → {result}")
            assert result == expected, f"Expected {expected}, got {result}"
        except Exception as e:
            print(f"  {expr:<50} → ERROR: {e}")
            raise
    print("✅ PASSED: All JavaScript → JSON tests\n")

def test_python_to_python():
    """Test 3: Python expressions returning Python objects"""
    print("🧪 Test 3: Python [!  !] expressions → Python objects")
    print("-" * 50)
    
    context = get_test_context()
    tests = [
        ("[! users !]", ['Alice', 'Bob', 'Charlie']),
        ("[! len(users) !]", 3),
        ("[! config['debug'] !]", True), 
        ("[! count > 3 !]", True),
        ("[! message + ' - ' + users[0] !]", "Hello World - Alice"),
        ("[! sum(item['value'] for item in nested['items']) !]", 30),
        ("[! [item['name'] for item in nested['items'] if item['value'] > 15] !]", ['item2']),
    ]
    
    for expr, expected in tests:
        try:
            result = evaluate_expression(expr, context, "python")
            print(f"  {expr:<50} → {result} ({type(result).__name__})")
            assert result == expected, f"Expected {expected}, got {result}"
        except Exception as e:
            print(f"  {expr:<50} → ERROR: {e}")
            raise
    print("✅ PASSED: All Python → Python tests\n")

def test_python_to_json():
    """Test 4: Python expressions returning JSON strings"""
    print("🧪 Test 4: Python [!  !] expressions → JSON strings")
    print("-" * 50)
    
    context = get_test_context()
    tests = [
        ("[! users !]", '["Alice", "Bob", "Charlie"]'),
        ("[! len(users) !]", '3'),
        ("[! config['debug'] !]", 'true'), 
        ("[! count > 3 !]", 'true'),
        ("[! message + ' - ' + users[0] !]", '"Hello World - Alice"'),
        ("[! sum(item['value'] for item in nested['items']) !]", '30'),
        ("[! [item['name'] for item in nested['items'] if item['value'] > 15] !]", '["item2"]'),
    ]
    
    for expr, expected in tests:
        try:
            result = evaluate_expression(expr, context, "json")
            print(f"  {expr:<50} → {result}")
            assert result == expected, f"Expected {expected}, got {result}"
        except Exception as e:
            print(f"  {expr:<50} → ERROR: {e}")
            raise
    print("✅ PASSED: All Python → JSON tests\n")

def test_fallback_plain_text():
    """Test 5: Fallback for plain text"""
    print("🧪 Test 5: Fallback for plain text")
    print("-" * 50)
    
    context = get_test_context()
    tests = [
        ("plain text", "plain text", '"plain text"'),
        ("no expressions here", "no expressions here", '"no expressions here"'),
        ("just a string", "just a string", '"just a string"')
    ]
    
    for text, expected_py, expected_json in tests:
        result_py = evaluate_expression(text, context, "python")
        result_json = evaluate_expression(text, context, "json")
        print(f"  '{text}' → python: {result_py}, json: {result_json}")
        assert result_py == expected_py, f"Expected python: {expected_py}, got {result_py}"
        assert result_json == expected_json, f"Expected json: {expected_json}, got {result_json}"
    print("✅ PASSED: All Fallback tests\n")

def run_all_tests():
    """Run all expression system tests"""
    import sys
    import os
    sys.path.append('../../../')  # Добавляем корневую папку проекта в sys.path
    
    print("🚀 Expression System Comprehensive Test Suite")
    print("=" * 70)
    
    tests = [
        test_javascript_to_python,
        test_javascript_to_json,
        test_python_to_python,
        test_python_to_json,
        test_fallback_plain_text
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            test_func()
            passed += 1
        except Exception as e:
            print(f"❌ FAILED: {test_func.__name__}: {e}")
            failed += 1
    
    print("=" * 70)
    print(f"📊 Test Results:")
    print(f"  ✅ Passed: {passed}")
    print(f"  ❌ Failed: {failed}")
    print(f"  📈 Success Rate: {passed/(passed + failed)*100:.1f}%")
    
    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! Expression system is working perfectly! 🚀")
    else:
        print(f"\n⚠️ {failed} test(s) failed. Check output above.")
    
    return failed == 0

if __name__ == "__main__":
    import sys
    import os
    sys.path.append('../../../')  # Добавляем корневую папку проекта в sys.path
    run_all_tests()
