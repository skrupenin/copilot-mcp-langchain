"""
Telegram Polling Server - универсальный инструмент для создания Telegram ботов
"""

import asyncio
import json
import uuid
import os
import threading
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

import mcp.types as types
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.error import TelegramError

from mcp_server.logging_config import setup_instance_logger, close_instance_logger

# Логгер будет создаваться только при запуске бота
logger = None

async def tool_info() -> dict:
    """Returns information about the lng_telegram_polling_server tool."""
    return {
        "description": "Telegram Polling Server - универсальный инструмент для работы с Telegram ботами",
        "schema": {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["start", "stop", "status", "send_message"],
                    "description": "Operation to perform"
                },
                "bot_token": {
                    "type": "string",
                    "description": "Telegram bot token (required for start operation)"
                },
                "user_id": {
                    "type": "integer",
                    "description": "User ID for sending messages"
                },
                "message": {
                    "type": "string",
                    "description": "Message text to send"
                },
                "pipeline": {
                    "type": "array",
                    "description": "Pipeline to execute on message received",
                    "items": {
                        "type": "object"
                    }
                }
            },
            "required": ["operation"]
        }
    }

async def run_tool(name: str, parameters: dict) -> list[types.Content]:
    """Executes the Telegram polling server tool."""
    try:
        result = tool_lng_telegram_polling_server(**parameters)
        return [types.TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]
    except Exception as e:
        error_result = {"error": str(e)}
        return [types.TextContent(type="text", text=json.dumps(error_result, ensure_ascii=False))]

class TelegramPollingServer:
    """Сервер для управления Telegram ботом в polling режиме"""
    
    def __init__(self, token: str, pipeline: List[Dict] = None):
        global logger
        # Создаем логгер только при создании экземпляра бота
        logger = setup_instance_logger("polling_server", "telegram")
        self.logger = logger
        
        self.token = token
        self.bot = Bot(token=token)
        self.application = Application.builder().token(token).build()
        self.pipeline = pipeline or []
        self.running = False
        
        # Настройка обработчиков
        self._setup_handlers()
        
    def _setup_handlers(self):
        """Настройка обработчиков сообщений"""
        self.application.add_handler(CommandHandler("start", self._handle_start))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self._handle_message))
        
    def close_logger(self):
        """Закрытие логгера и освобождение файловых дескрипторов"""
        if hasattr(self, 'logger') and self.logger:
            close_instance_logger("polling_server", "telegram")
            self.logger = None
        
    async def _handle_start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка команды /start"""
        try:
            user = update.effective_user
            user_id = user.id
            
            # Получаем параметр сессии из deep link
            session_id = None
            if context.args:
                session_id = context.args[0]
                
            logger.info(f"User {user_id} started bot with session_id: {session_id}")
            
            # Выполняем pipeline для команды start
            start_text = f"/start{' ' + session_id if session_id else ''}"
            await self._process_message_pipeline(user_id, start_text, update)
                
        except Exception as e:
            logger.error(f"Error in start handler: {e}")
            await update.message.reply_text("Произошла ошибка при подключении к боту")
            
    async def _handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка текстовых сообщений"""
        try:
            user_id = update.effective_user.id
            message_text = update.message.text
            
            logger.info(f"Message from {user_id}: {message_text}")
            
            # Выполняем pipeline для обработки сообщения
            await self._process_message_pipeline(user_id, message_text, update)
            
        except Exception as e:
            logger.error(f"Error in message handler: {e}")
            await update.message.reply_text("Произошла ошибка при обработке сообщения")
            
    async def _process_message_pipeline(self, user_id: int, message_text: str, update: Update):
        """Обработка сообщения через pipeline"""
        try:
            # Подготавливаем базовый контекст для pipeline
            user = update.effective_user
            context = {
                "telegram": {
                    "user_id": user_id,
                    "message": message_text,
                    "username": user.username or "",
                    "first_name": user.first_name or "",
                    "last_name": user.last_name or "",
                    "update": update,
                    "bot": self
                }
            }
            
            # Выполняем pipeline если он задан
            if self.pipeline:
                for step in self.pipeline:
                    tool_name = step.get("tool")
                    tool_params = step.get("params", {})
                    
                    # Подставляем контекст в параметры
                    processed_params = self._substitute_context(tool_params, context)
                    
                    try:
                        # TODO: Интеграция с системой выполнения инструментов
                        # result = await execute_tool(tool_name, processed_params)
                        
                        # Временная заглушка для pipeline
                        result = {"tool": tool_name, "params": processed_params}
                        logger.info(f"Pipeline step {tool_name} would be executed with params: {processed_params}")
                        
                        # Сохраняем результат в контекст
                        output_var = step.get("output")
                        if output_var:
                            context[output_var] = result
                            
                    except Exception as e:
                        logger.error(f"Error executing pipeline step {tool_name}: {e}")
                        
        except Exception as e:
            logger.error(f"Error in message pipeline: {e}")
            
    def _substitute_context(self, params: Dict, context: Dict) -> Dict:
        """Подстановка контекста в параметры"""
        result = {}
        for key, value in params.items():
            if isinstance(value, str) and "{!" in value and "!}" in value:
                # Простая подстановка контекста (можно расширить)
                if "{! telegram.message !}" in value:
                    value = value.replace("{! telegram.message !}", context["telegram"]["message"])
                if "{! telegram.user_id !}" in value:
                    value = value.replace("{! telegram.user_id !}", str(context["telegram"]["user_id"]))
            result[key] = value
        return result

# Глобальный инстанс сервера
_server_instance: Optional[TelegramPollingServer] = None

async def start_polling_server(token: str, pipeline: List[Dict] = None) -> TelegramPollingServer:
    """Запуск polling сервера"""
    global _server_instance
    
    if _server_instance and _server_instance.running:
        logger.warning("Polling server already running")
        return _server_instance
        
    _server_instance = TelegramPollingServer(token, pipeline)
    _server_instance.running = True
    
    logger.info("Starting Telegram polling server...")
    await _server_instance.application.run_polling()
    
    return _server_instance

async def stop_polling_server():
    """Остановка polling сервера"""
    global _server_instance
    
    if _server_instance and _server_instance.running:
        logger.info("Stopping Telegram polling server...")
        await _server_instance.application.stop()
        _server_instance.running = False
        _server_instance = None

async def send_message(user_id: int, text: str) -> bool:
    """Отправка сообщения пользователю"""
    global _server_instance
    
    if not _server_instance:
        logger.error("Polling server not running")
        return False
        
    try:
        await _server_instance.bot.send_message(user_id, text)
        return True
    except TelegramError as e:
        logger.error(f"Error sending message to {user_id}: {e}")
        return False



def get_server_status() -> Dict:
    """Получение статуса сервера"""
    global _server_instance
    
    if not _server_instance:
        return {"running": False, "pipeline_count": 0}
        
    return {
        "running": _server_instance.running,
        "pipeline_count": len(_server_instance.pipeline)
    }

def tool_lng_telegram_polling_server(
    operation: str,
    token: str = None,
    user_id: int = None,
    message: str = None,
    pipeline: List[Dict] = None
) -> Dict[str, Any]:
    """
    Telegram Polling Server - универсальный инструмент для работы с Telegram ботами
    
    Operations:
    - start: Запуск polling сервера (запускается в фоновом режиме)
    - stop: Остановка сервера  
    - send_message: Отправка сообщения пользователю
    - status: Получение статуса сервера
    """
    
    global _server_instance
    
    try:
        if operation == "start":
            if not token:
                # Пытаемся получить токен из .env
                from dotenv import load_dotenv
                load_dotenv()
                token = os.getenv("TELEGRAM_BOT_TOKEN")
                
                if not token:
                    return {"error": "Token is required for start operation"}
            
            # Простая проверка валидности токена
            if ":" not in token or len(token.split(":")) != 2:
                return {"error": "Invalid bot token format"}
            
            # Запуск бота с pipeline поддержкой
            if _server_instance and _server_instance.running:
                return {"error": "Server already running"}
            
            # Принудительная очистка перед запуском
            if _server_instance:
                try:
                    _server_instance.close_logger()
                except:
                    pass
                _server_instance = None
            
            try:
                import asyncio
                import threading
                import time
                
                def run_bot():
                    global _server_instance, logger
                    
                    # Создаем полностью новый event loop
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    
                    try:
                        # Создаем новый экземпляр сервера
                        _server_instance = TelegramPollingServer(token, pipeline or [])
                        _server_instance.running = True
                        
                        # Обновляем глобальный логгер
                        logger = _server_instance.logger
                        logger.info("Starting Telegram polling server...")
                        
                        # Запускаем polling
                        _server_instance.application.run_polling(
                            close_loop=False,  # Не закрываем loop автоматически
                            stop_signals=None  # Отключаем обработку сигналов
                        )
                        
                    except Exception as e:
                        if logger:
                            logger.error(f"Bot error: {e}")
                        if _server_instance:
                            _server_instance.running = False
                    finally:
                        # Принудительная очистка loop
                        try:
                            pending = asyncio.all_tasks(loop)
                            for task in pending:
                                task.cancel()
                            if pending:
                                loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
                        except:
                            pass
                        loop.close()
                
                # Запускаем в отдельном потоке
                bot_thread = threading.Thread(target=run_bot, daemon=True)
                bot_thread.start()
                
                # Небольшая задержка для инициализации
                time.sleep(0.5)
                
                return {
                    "status": "started",
                    "message": "Telegram bot started with pipeline support",
                    "pipeline_count": len(pipeline or [])
                }
                
            except Exception as e:
                return {"error": f"Failed to start bot: {str(e)}"}
                
        elif operation == "stop":
            if _server_instance and _server_instance.running:
                try:
                    logger.info("Stopping Telegram polling server...")
                    _server_instance.running = False
                    
                    if _server_instance.application:
                        # Более тщательная остановка
                        import asyncio
                        import threading
                        import time
                        
                        def stop_bot():
                            try:
                                # Создаем новый event loop для остановки
                                loop = asyncio.new_event_loop()
                                asyncio.set_event_loop(loop)
                                
                                # Останавливаем приложение
                                loop.run_until_complete(_server_instance.application.stop())
                                
                                # Дополнительная очистка
                                if hasattr(_server_instance.application, 'updater'):
                                    loop.run_until_complete(_server_instance.application.updater.stop())
                                
                                # Закрываем все задачи
                                pending = asyncio.all_tasks(loop)
                                for task in pending:
                                    task.cancel()
                                
                                if pending:
                                    loop.run_until_complete(asyncio.gather(*pending, return_exceptions=True))
                                    
                            except Exception as e:
                                logger.error(f"Error stopping bot: {e}")
                            finally:
                                loop.close()
                        
                        # Запускаем остановку в отдельном потоке
                        stop_thread = threading.Thread(target=stop_bot, daemon=True)
                        stop_thread.start()
                        stop_thread.join(timeout=10)  # Увеличили timeout
                        
                        # Принудительно очищаем ссылку на приложение
                        _server_instance.application = None
                    
                    # Закрываем логгер
                    _server_instance.close_logger()
                    
                    # Очищаем глобальную ссылку
                    _server_instance = None
                    
                    return {"status": "stopped", "message": "Telegram bot stopped"}
                except Exception as e:
                    return {"error": f"Failed to stop bot: {str(e)}"}
            else:
                return {"status": "not_running", "message": "Bot is not running"}
            
        elif operation == "send_message":
            if not user_id or not message:
                return {"error": "user_id and message are required"}
            
            try:
                import asyncio
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                success = loop.run_until_complete(send_message(user_id, message))
                return {
                    "status": "sent" if success else "failed",
                    "user_id": user_id,
                    "message": message
                }
            except Exception as e:
                return {"error": f"Failed to send message: {str(e)}"}
            
        elif operation == "status":
            return get_server_status()
            
        else:
            return {"error": f"Unknown operation: {operation}"}
            
    except Exception as e:
        logger.error(f"Error in telegram polling server: {e}")
        return {"error": str(e)}
