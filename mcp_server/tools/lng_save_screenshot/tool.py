import os
from datetime import datetime
import mss
import mss.tools
import mcp.types as types

async def tool_info() -> dict:
    """Возвращает информацию о инструменте lng_save_screenshot."""
    return {
        "description": "Сохраняет скриншоты всех экранов в указанной папке.",
        "schema": {
            "type": "object",
            "properties": {
                "output_dir": {
                    "type": "string",
                    "description": "Папка для сохранения скриншотов. По умолчанию './screenshot'."
                }
            },
            "required": []
        }
    }

async def run_tool(name: str, arguments: dict) -> list[types.Content]:
    """Создаёт скриншоты всех экранов с помощью mss и сохраняет их в корне проекта."""
    project_root = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
    output_dir = arguments.get("output_dir", os.path.join(project_root, "screenshot"))
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

    saved_files = []
    with mss.mss() as sct:
        for i, monitor in enumerate(sct.monitors[1:]):  # sct.monitors[0] — вся область, [1:] — отдельные мониторы
            img = sct.grab(monitor)
            file_name = f"{timestamp}_screen_{i+1}.png"
            file_path = os.path.abspath(os.path.join(output_dir, file_name))
            mss.tools.to_png(img.rgb, img.size, output=file_path)
            saved_files.append(file_path)

    result = {"screenshots": saved_files}
    import json
    return [types.TextContent(type="text", text=json.dumps(result, ensure_ascii=False, indent=2))]
