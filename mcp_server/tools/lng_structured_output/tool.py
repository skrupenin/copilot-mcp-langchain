import json
from typing import Dict, Any, List
import mcp.types as types
from pydantic import BaseModel, Field
from mcp_server.llm import llm

from langchain.output_parsers import (
    StructuredOutputParser,
    ResponseSchema,
    PydanticOutputParser, 
    XMLOutputParser,
    OutputFixingParser
)
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import yaml

async def tool_info() -> dict:
    """Returns information about the lng_structured_output tool."""
    return {
        "name": "lng_structured_output",
        "description": """Демонстрирует различные форматы структурированного вывода LangChain с использованием OutputParser.

**Parameters:**
- `question` (string, required): Вопрос о фильме, на который нужно ответить в структурированном формате
- `output_format` (string, required): Формат вывода данных (json, xml, csv, yaml, pydantic)

**Example Usage:**
- Provide a question about a movie and specify the desired output format
- The system will return structured information about the movie in the requested format
- Use different formats to see how LangChain structures the same information

This tool demonstrates the OutputParser capabilities in LangChain for transforming LLM outputs into structured formats.""",
        "schema": {
            "type": "object",
            "required": ["question", "output_format"],
            "properties": {
                "question": {
                    "type": "string",
                    "description": "Вопрос о фильме, на который нужно ответить в структурированном формате",
                },
                "output_format": {
                    "type": "string",
                    "description": "Формат вывода данных",
                    "enum": ["json", "xml", "csv", "yaml", "pydantic"]
                }
            },
        }
    }

class MovieReview(BaseModel):
    """Обзор фильма"""
    title: str = Field(description="Название фильма")
    director: str = Field(description="Режиссер фильма")
    year: int = Field(description="Год выпуска")
    rating: float = Field(description="Оценка фильма по шкале от 1 до 10")
    genres: List[str] = Field(description="Жанры фильма")
    review: str = Field(description="Краткий обзор фильма")


async def format_as_json(question: str) -> str:
    """Форматирует ответ в JSON с использованием StructuredOutputParser."""
    model = llm()
    
    # Определяем схему ответа для фильма
    response_schemas = [
        ResponseSchema(name="title", description="Название фильма"),
        ResponseSchema(name="director", description="Режиссер фильма"),
        ResponseSchema(name="year", description="Год выпуска (число)"),
        ResponseSchema(name="rating", description="Оценка по шкале от 1 до 10 (число)"),
        ResponseSchema(name="genres", description="Список жанров, разделенный запятыми"),
        ResponseSchema(name="review", description="Краткий обзор фильма")
    ]
    
    # Создаем парсер и шаблон промпта
    parser = StructuredOutputParser.from_response_schemas(response_schemas)
    format_instructions = parser.get_format_instructions()
    
    template = """
    Ответь на следующий вопрос о фильме с предоставлением структурированной информации:
    
    {question}
    
    {format_instructions}
    """
    
    prompt = PromptTemplate(
        template=template,
        input_variables=["question"],
        partial_variables={"format_instructions": format_instructions}
    )
    
    # Создаем и запускаем цепочку
    chain = LLMChain(llm=model, prompt=prompt)
    result = await chain.arun(question=question)
    
    # Парсим результат и форматируем его в JSON
    try:
        parsed_result = parser.parse(result)
        # Преобразуем списки из строк в реальные списки
        if isinstance(parsed_result.get("genres"), str) and "," in parsed_result.get("genres", ""):
            parsed_result["genres"] = [item.strip() for item in parsed_result["genres"].split(",")]
        
        return json.dumps(parsed_result, ensure_ascii=False, indent=2)
    except Exception as e:
        # Если парсинг не удался, используем OutputFixingParser для исправления
        fixing_parser = OutputFixingParser.from_llm(parser=parser, llm=model)
        try:
            fixed_result = fixing_parser.parse(result)
            if isinstance(fixed_result.get("genres"), str) and "," in fixed_result.get("genres", ""):
                fixed_result["genres"] = [item.strip() for item in fixed_result["genres"].split(",")]
            return json.dumps(fixed_result, ensure_ascii=False, indent=2)
        except Exception as e2:
            return f"Ошибка парсинга: {str(e2)}\nИсходный ответ:\n{result}"


async def format_as_xml(question: str) -> str:
    """Форматирует ответ в XML с использованием XMLOutputParser."""
    model = llm()
    
    # Используем XMLOutputParser
    parser = XMLOutputParser(root_tag="response")
    
    xml_format = """
    <response>
      <movie>
        <title>Название фильма</title>
        <director>Режиссер</director>
        <year>Год выпуска (число)</year>
        <rating>Оценка (число от 1 до 10)</rating>
        <genres>
          <genre>Жанр 1</genre>
          <genre>Жанр 2</genre>
          <!-- Дополнительные жанры -->
        </genres>
        <review>Краткий обзор фильма</review>
      </movie>
    </response>
    """
    
    instructions = """
    Ответь на вопрос о фильме в формате XML. Используй следующую структуру:
    
    <response>
      <movie>
        <title>Название фильма</title>
        <director>Режиссер</director>
        <year>Год выпуска (только число)</year>
        <rating>Оценка (только число от 1 до 10)</rating>
        <genres>
          <genre>Жанр 1</genre>
          <genre>Жанр 2</genre>
          <!-- Добавь больше жанров при необходимости -->
        </genres>
        <review>Краткий обзор фильма</review>
      </movie>
    </response>
    """
    
    # Создаем шаблон промпта
    template = """
    {instructions}
    
    Вопрос о фильме: {question}
    
    Ответ в XML:
    """
    
    prompt = PromptTemplate(
        template=template,
        input_variables=["question"],
        partial_variables={"instructions": instructions}
    )
    
    # Создаем и запускаем цепочку
    chain = LLMChain(llm=model, prompt=prompt)
    result = await chain.arun(question=question)
    
    # Обрабатываем результат
    try:
        # Удаляем всё перед первым '<' и после последнего '>'
        start_idx = result.find("<")
        end_idx = result.rfind(">") + 1
        if start_idx >= 0 and end_idx > 0:
            clean_xml = result[start_idx:end_idx]
            return clean_xml
        return result
    except Exception as e:
        return f"Ошибка при форматировании XML: {str(e)}\nИсходный ответ:\n{result}"


async def format_as_csv(question: str) -> str:
    """Форматирует ответ в CSV."""
    model = llm()
    
    headers = "title,director,year,rating,genres,review"
    instructions = f"""
    Ответь на вопрос о фильме в формате CSV. Первая строка должна содержать заголовки:
    {headers}
    
    Во второй строке должны быть значения. Год и оценка должны быть числами.
    Жанры должны быть перечислены в одной ячейке, разделенные точкой с запятой.
    """
    
    # Создаем шаблон промпта
    template = """
    {instructions}
    
    Вопрос о фильме: {question}
    
    Ответ в CSV:
    """
    
    prompt = PromptTemplate(
        template=template,
        input_variables=["question"],
        partial_variables={"instructions": instructions}
    )
    
    # Создаем и запускаем цепочку
    chain = LLMChain(llm=model, prompt=prompt)
    result = await chain.arun(question=question)
    
    # Обрабатываем результат
    try:
        # Удаляем лишние строки до и после CSV
        lines = [line.strip() for line in result.split("\n") if line.strip()]
        csv_lines = []
        
        # Ищем строки, которые похожи на CSV (содержат запятые)
        for line in lines:
            if "," in line:
                csv_lines.append(line)
        
        if len(csv_lines) >= 2:  # У нас должно быть как минимум 2 строки (заголовки и данные)
            return "\n".join(csv_lines[:2])  # Берем только первые две строки
        else:
            return result  # Возвращаем исходный результат, если не удалось извлечь CSV
    except Exception as e:
        return f"Ошибка при форматировании CSV: {str(e)}\nИсходный ответ:\n{result}"

async def format_as_yaml(question: str) -> str:
    """Форматирует ответ в YAML."""
    model = llm()
    
    yaml_example = """
    movie:
      title: Название фильма
      director: Режиссер
      year: 2020  # Год выпуска (число)
      rating: 8.5  # Оценка (число от 1 до 10)
      genres:
        - Жанр 1
        - Жанр 2
      review: Краткий обзор фильма
    """
    
    instructions = """
    Ответь на вопрос о фильме в формате YAML. Используй следующую структуру:
    
    movie:
      title: Название фильма
      director: Режиссер
      year: 2020  # должно быть числом
      rating: 8.5  # должно быть числом от 1 до 10
      genres:
        - Жанр 1
        - Жанр 2
      review: Краткий обзор фильма
    """
    
    # Создаем шаблон промпта
    template = """
    {instructions}
    
    Вопрос о фильме: {question}
    
    Ответ в YAML:
    """
    
    prompt = PromptTemplate(
        template=template,
        input_variables=["question"],
        partial_variables={"instructions": instructions}
    )
    
    # Создаем и запускаем цепочку
    chain = LLMChain(llm=model, prompt=prompt)
    result = await chain.arun(question=question)
    
    # Обрабатываем результат
    try:
        # Извлекаем YAML из ответа
        lines = result.split("\n")
        yaml_lines = []
        in_yaml = False
        
        for line in lines:
            # Ищем начало YAML блока
            if not in_yaml and line.strip().startswith("movie:"):
                in_yaml = True
            
            if in_yaml:
                yaml_lines.append(line)
        
        if yaml_lines:
            yaml_content = "\n".join(yaml_lines)
            # Проверяем, что это валидный YAML, загрузив его и затем снова сериализовав
            parsed_yaml = yaml.safe_load(yaml_content)
            formatted_yaml = yaml.dump(parsed_yaml, default_flow_style=False, allow_unicode=True)
            return formatted_yaml
        else:
            return result
    except Exception as e:
        return f"Ошибка при форматировании YAML: {str(e)}\nИсходный ответ:\n{result}"


async def format_as_pydantic(question: str) -> str:
    """Форматирует ответ с использованием PydanticOutputParser."""
    model = llm()
    
    # Используем модель MovieReview
    parser = PydanticOutputParser(pydantic_object=MovieReview)
    
    # Получаем инструкции для форматирования
    format_instructions = parser.get_format_instructions()
    
    # Создаем шаблон промпта
    template = """
    Ответь на следующий вопрос о фильме, используя структурированный формат:
    
    {question}
    
    {format_instructions}
    """
    
    prompt = PromptTemplate(
        template=template,
        input_variables=["question"],
        partial_variables={"format_instructions": format_instructions}
    )
    
    # Создаем и запускаем цепочку
    chain = LLMChain(llm=model, prompt=prompt)
    result = await chain.arun(question=question)
    
    # Парсим результат
    try:
        parsed_obj = parser.parse(result)
        return parsed_obj.json(ensure_ascii=False, indent=2)
    except Exception as e:
        # Если парсинг не удался, используем OutputFixingParser
        fixing_parser = OutputFixingParser.from_llm(parser=parser, llm=model)
        try:
            fixed_obj = fixing_parser.parse(result)
            return fixed_obj.json(ensure_ascii=False, indent=2)
        except Exception as e2:
            return f"Ошибка парсинга: {str(e2)}\nИсходный ответ:\n{result}"


async def run_tool(name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
    """Запускает инструмент с указанными аргументами."""
    question = arguments.get("question", "")
    output_format = arguments.get("output_format", "json")
    
    try:
        if output_format == "json":
            result = await format_as_json(question)
        elif output_format == "xml":
            result = await format_as_xml(question)
        elif output_format == "csv":
            result = await format_as_csv(question)
        elif output_format == "yaml":
            result = await format_as_yaml(question)
        elif output_format == "pydantic":
            result = await format_as_pydantic(question)
        else:
            result = f"Неподдерживаемый формат: {output_format}"
        
        return {
            "result": result,
            "format": output_format
        }
    except Exception as e:
        return {
            "error": str(e),
            "format": output_format
        }