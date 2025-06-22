"""
Скрипт-обертка для запуска MCP сервера с предварительной загрузкой FAISS
"""
import os
import sys
import logging

# Настраиваем логирование
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(os.path.dirname(__file__), 'mcp_server', 'mcp_server.log'), mode='w', encoding='utf-8')
    ]
)
logger = logging.getLogger('mcp_wrapper')

logger.info(f"Python executable: {sys.executable}")
logger.info(f"Python version: {sys.version}")
logger.info(f"Current directory: {os.getcwd()}")

# Добавляем корневую директорию проекта в PYTHONPATH
project_root = os.path.dirname(os.path.abspath(__file__))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
logger.info(f"Added to sys.path: {project_root}")

# Предварительно импортируем FAISS и другие проблемные библиотеки
try:
    logger.info("Attempting to pre-import problematic libraries")
       
    logger.info("Importing FAISS")
    from langchain_community.vectorstores import FAISS
    logger.info("Successfully imported FAISS")
    
    logger.info("Pre-imports completed successfully")
except Exception as e:
    logger.error(f"Error during pre-imports: {e}")
    logger.exception("Stack trace:")

# Запускаем MCP сервер
try:
    logger.info("Importing MCP server")
    from mcp_server.server import main
    logger.info("Starting MCP server")
    main()
except Exception as e:
    logger.error(f"Error running MCP server: {e}")
    logger.exception("Stack trace:")
