import mcp.types as types
import json
import re
import math
import operator

async def tool_info() -> dict:
    """Returns information about the lng_math_calculator tool."""
    return {
        "name": "lng_math_calculator",
        "description": """Виконує математичні обчислення і операції.

**Параметри:**
- `expression` (string, required): Математичний вираз для обчислення.

**Підтримувані операції:**
- Базові арифметичні операції: +, -, *, /
- Степінь: ** або ^
- Дужки для групування: ()
- Математичні функції: sin, cos, tan, log, ln, sqrt, abs
- Константи: pi, e
- Цілочисельне ділення: //
- Остача від ділення: %

**Приклади використання:**
- "2 + 3 * 4" → 14
- "sqrt(16) + 2^3" → 12
- "sin(pi/2)" → 1
- "(10 + 5) * 2" → 30
- "log(100)" → 2

Цей інструмент корисний для виконання складних математичних обчислень.""",
        "schema": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "Математичний вираз для обчислення"
                }
            },
            "required": ["expression"]
        }
    }

async def run_tool(name: str, parameters: dict) -> list[types.Content]:
    """Виконує математичні обчислення."""
    try:
        # Отримуємо вираз
        expression = parameters.get("expression", "")
        
        if not expression:
            return [types.TextContent(type="text", text='{"error": "Не надано математичний вираз для обчислення."}')]
        
        # Очищуємо та підготовлюємо вираз
        cleaned_expression = clean_expression(expression)
        
        # Обчислюємо результат
        result = safe_eval(cleaned_expression)
        
        # Створюємо JSON результат
        result_dict = {
            "originalExpression": expression,
            "cleanedExpression": cleaned_expression,
            "result": result,
            "resultType": type(result).__name__
        }
        
        # Конвертуємо в JSON рядок
        json_result = json.dumps(result_dict, indent=2, ensure_ascii=False)
        
        return [types.TextContent(type="text", text=json_result)]
        
    except Exception as e:
        error_result = {
            "error": f"Помилка при обчисленні: {str(e)}",
            "originalExpression": parameters.get("expression", "")
        }
        return [types.TextContent(type="text", text=json.dumps(error_result, ensure_ascii=False))]

def clean_expression(expr: str) -> str:
    """Очищає та підготовлює математичний вираз."""
    # Видаляємо зайві пробіли
    expr = expr.strip()
    
    # Замінюємо ^ на **
    expr = expr.replace('^', '**')
    
    # Замінюємо константи
    expr = expr.replace('pi', str(math.pi))
    expr = expr.replace('e', str(math.e))
    
    # Замінюємо математичні функції
    math_functions = {
        'sin': 'math.sin',
        'cos': 'math.cos',
        'tan': 'math.tan',
        'log': 'math.log10',
        'ln': 'math.log',
        'sqrt': 'math.sqrt',
        'abs': 'abs',
        'floor': 'math.floor',
        'ceil': 'math.ceil',
        'round': 'round'
    }
    
    for func, replacement in math_functions.items():
        # Використовуємо регулярні вирази для точної заміни функцій
        pattern = r'\b' + func + r'\b'
        expr = re.sub(pattern, replacement, expr)
    
    return expr

def safe_eval(expr: str):
    """Безпечно обчислює математичний вираз."""
    # Список дозволених імен
    allowed_names = {
        '__builtins__': {},
        'math': math,
        'abs': abs,
        'round': round,
        'min': min,
        'max': max,
        'sum': sum,
        'pow': pow
    }
    
    # Список заборонених символів/функцій
    forbidden = ['import', '__', 'exec', 'eval', 'open', 'file', 'input', 'raw_input']
    
    # Перевіряємо на заборонені елементи
    for item in forbidden:
        if item in expr:
            raise ValueError(f"Заборонений елемент '{item}' у виразі")
    
    try:
        # Безпечно обчислюємо вираз
        result = eval(expr, allowed_names, {})
        
        # Перевіряємо тип результату
        if isinstance(result, (int, float, complex)):
            # Округлюємо float до розумної кількості знаків після коми
            if isinstance(result, float):
                return round(result, 10)
            return result
        else:
            raise ValueError(f"Неочікуваний тип результату: {type(result)}")
            
    except ZeroDivisionError:
        raise ValueError("Ділення на нуль")
    except OverflowError:
        raise ValueError("Результат занадто великий")
    except ValueError as e:
        raise ValueError(f"Помилка значення: {str(e)}")
    except Exception as e:
        raise ValueError(f"Помилка обчислення: {str(e)}")
