"""
Telegram Polling Server - универсальный инструмент для создания Telegram ботов
"""

import asyncio
import json
import uuid
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

import mcp.types as types
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.error import TelegramError

from mcp_server.logging_config import setup_logging

logger = setup_logging("lng_telegram_polling_server")

async def tool_info() -> dict:
    """Returns information about the lng_telegram_polling_server tool."""
    return {
        "description": "Telegram Polling Server - универсальный инструмент для работы с Telegram ботами",
        "schema": {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["start", "stop", "status", "send_message", "send_to_session"],
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
                "session_id": {
                    "type": "string",
                    "description": "Session ID for user management"
                },
                "pipeline": {
                    "type": "array",
                    "description": "Pipeline to execute on message received",
                    "items": {
                        "type": "object"
                    }
                },
                "exclude_user": {
                    "type": "integer",
                    "description": "User ID to exclude when sending to session"
                }
            },
            "required": ["operation"]
        }
    }

def tool_lng_telegram_polling_server(operation: str = "status") -> Dict[str, Any]:
    """Simple telegram polling server tool"""
    try:
        if operation == "status":
            return {"running": False, "message": "Telegram polling server not implemented yet"}
        else:
            return {"error": f"Unknown operation: {operation}"}
    except Exception as e:
        return {"error": str(e)}

async def run_tool(name: str, parameters: dict) -> list[types.Content]:
    """Executes the Telegram polling server tool."""
    try:
        result = tool_lng_telegram_polling_server(**parameters)
        return [types.TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]
    except Exception as e:
        error_result = {"error": str(e)}
        return [types.TextContent(type="text", text=json.dumps(error_result, ensure_ascii=False))]

@dataclass
class UserState:
    """Состояние пользователя"""
    user_id: int
    username: str
    first_name: str
    session_id: Optional[str] = None
    current_message_processing: Optional[str] = None
    joined_at: Optional[str] = None

@dataclass
class SessionState:
    """Состояние сессии"""
    session_id: str
    participants: List[int]
    created_at: str
    last_activity: str
    message_queue: List[Dict] = None

    def __post_init__(self):
        if self.message_queue is None:
            self.message_queue = []

class TelegramPollingServer:
    """Сервер для управления Telegram ботом в polling режиме"""
    
    def __init__(self, token: str, pipeline: List[Dict] = None):
        self.token = token
        self.bot = Bot(token=token)
        self.application = Application.builder().token(token).build()
        self.pipeline = pipeline or []
        
        # Состояния
        self.users: Dict[int, UserState] = {}
        self.sessions: Dict[str, SessionState] = {}
        self.running = False
        
        # Настройка обработчиков
        self._setup_handlers()
        
    def _setup_handlers(self):
        """Настройка обработчиков сообщений"""
        self.application.add_handler(CommandHandler("start", self._handle_start))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self._handle_message))
        
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
            
            # Создаем или обновляем состояние пользователя
            user_state = UserState(
                user_id=user_id,
                username=user.username or "",
                first_name=user.first_name or "",
                session_id=session_id,
                joined_at=datetime.now().isoformat()
            )
            self.users[user_id] = user_state
            
            if session_id:
                # Присоединяемся к существующей сессии
                await self._join_session(user_id, session_id)
            else:
                # Создаем новую сессию
                new_session_id = await self._create_session(user_id)
                await self._send_invitation_link(user_id, new_session_id)
                
        except Exception as e:
            logger.error(f"Error in start handler: {e}")
            await update.message.reply_text("Произошла ошибка при подключении к боту")
            
    async def _handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработка текстовых сообщений"""
        try:
            user_id = update.effective_user.id
            message_text = update.message.text
            
            # Проверяем, что пользователь зарегистрирован
            if user_id not in self.users:
                await update.message.reply_text("Пожалуйста, сначала выполните команду /start")
                return
                
            user_state = self.users[user_id]
            
            # Выполняем pipeline для обработки сообщения
            await self._process_message_pipeline(user_id, message_text, update)
            
        except Exception as e:
            logger.error(f"Error in message handler: {e}")
            await update.message.reply_text("Произошла ошибка при обработке сообщения")
            
    async def _create_session(self, user_id: int) -> str:
        """Создание новой сессии"""
        session_id = str(uuid.uuid4())
        session_state = SessionState(
            session_id=session_id,
            participants=[user_id],
            created_at=datetime.now().isoformat(),
            last_activity=datetime.now().isoformat()
        )
        
        self.sessions[session_id] = session_state
        self.users[user_id].session_id = session_id
        
        logger.info(f"Created session {session_id} for user {user_id}")
        return session_id
        
    async def _join_session(self, user_id: int, session_id: str):
        """Присоединение к существующей сессии"""
        if session_id in self.sessions:
            session = self.sessions[session_id]
            if user_id not in session.participants:
                session.participants.append(user_id)
                session.last_activity = datetime.now().isoformat()
                
            self.users[user_id].session_id = session_id
            
            # Уведомляем всех участников о присоединении
            user_state = self.users[user_id]
            join_message = f"👋 {user_state.first_name} присоединился к сессии"
            
            for participant_id in session.participants:
                if participant_id != user_id:
                    await self.bot.send_message(participant_id, join_message)
                    
            await self.bot.send_message(user_id, f"✅ Вы присоединились к сессии {session_id}")
            logger.info(f"User {user_id} joined session {session_id}")
        else:
            await self.bot.send_message(user_id, "❌ Сессия не найдена")
            
    async def _send_invitation_link(self, user_id: int, session_id: str):
        """Отправка ссылки-приглашения"""
        bot_username = (await self.bot.get_me()).username
        invite_link = f"https://t.me/{bot_username}?start={session_id}"
        
        message = f"""🎯 Сессия создана!
        
Ваш ID сессии: `{session_id}`
Ссылка для приглашения: {invite_link}

Отправьте эту ссылку вашему собеседнику для присоединения к сессии."""
        
        await self.bot.send_message(user_id, message, parse_mode='Markdown')
        
    async def _process_message_pipeline(self, user_id: int, message_text: str, update: Update):
        """Обработка сообщения через pipeline"""
        try:
            # Подготавливаем контекст для pipeline
            user_state = self.users[user_id]
            session_state = self.sessions.get(user_state.session_id) if user_state.session_id else None
            
            context = {
                "telegram": {
                    "user_id": user_id,
                    "message": message_text,
                    "user_state": asdict(user_state),
                    "session_state": asdict(session_state) if session_state else None,
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

async def send_to_session(session_id: str, text: str, exclude_user: Optional[int] = None) -> int:
    """Отправка сообщения всем участникам сессии"""
    global _server_instance
    
    if not _server_instance:
        logger.error("Polling server not running")
        return 0
        
    if session_id not in _server_instance.sessions:
        logger.error(f"Session {session_id} not found")
        return 0
        
    session = _server_instance.sessions[session_id]
    sent_count = 0
    
    for user_id in session.participants:
        if exclude_user and user_id == exclude_user:
            continue
            
        if await send_message(user_id, text):
            sent_count += 1
            
    return sent_count

def get_server_status() -> Dict:
    """Получение статуса сервера"""
    global _server_instance
    
    if not _server_instance:
        return {"running": False, "users": 0, "sessions": 0}
        
    return {
        "running": _server_instance.running,
        "users": len(_server_instance.users),
        "sessions": len(_server_instance.sessions),
        "user_list": list(_server_instance.users.keys()),
        "session_list": list(_server_instance.sessions.keys())
    }

def tool_lng_telegram_polling_server(
    operation: str,
    token: str = None,
    user_id: int = None,
    session_id: str = None,
    message: str = None,
    pipeline: List[Dict] = None,
    exclude_user: int = None
) -> Dict[str, Any]:
    """
    Telegram Polling Server - универсальный инструмент для работы с Telegram ботами
    
    Operations:
    - start: Запуск polling сервера (запускается в фоновом режиме)
    - stop: Остановка сервера  
    - send_message: Отправка сообщения пользователю
    - send_to_session: Отправка сообщения всем в сессии
    - status: Получение статуса сервера
    """
    
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
            
            # Запуск в фоновом процессе
            import subprocess
            import sys
            import json
            
            # Создаем временный скрипт для запуска бота
            script_content = f'''
import asyncio
import os
import sys
sys.path.append(r"{os.getcwd()}")

from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import uuid
from datetime import datetime

TOKEN = "{token}"
users = {{}}
sessions = {{}}

async def handle_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    
    session_id = None
    if context.args:
        session_id = context.args[0]
    
    print(f"User {{user_id}} started bot with session_id: {{session_id}}")
    
    if session_id:
        # Присоединение к сессии
        if session_id in sessions:
            if user_id not in sessions[session_id]["participants"]:
                sessions[session_id]["participants"].append(user_id)
            await update.message.reply_text(f"✅ Присоединились к сессии {{session_id}}")
        else:
            await update.message.reply_text("❌ Сессия не найдена")
    else:
        # Создание новой сессии
        new_session_id = str(uuid.uuid4())
        sessions[new_session_id] = {{
            "participants": [user_id],
            "created_at": datetime.now().isoformat()
        }}
        
        bot_username = (await context.bot.get_me()).username
        invite_link = f"https://t.me/{{bot_username}}?start={{new_session_id}}"
        
        message = f"""🎯 Добро пожаловать в Super Empath Bot!

Ваша сессия создана: `{{new_session_id}}`
Ссылка для приглашения: {{invite_link}}

Отправьте эту ссылку вашему собеседнику для присоединения к сессии.
"""
        await update.message.reply_text(message, parse_mode='Markdown')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    message_text = update.message.text
    
    print(f"Message from {{user_id}}: {{message_text}}")
    
    # Простая обработка команд
    if message_text == "тамам":
        await update.message.reply_text("✅ Сообщение будет отправлено (функция в разработке)")
    elif message_text == "отбой":
        await update.message.reply_text("❌ Операция отменена")
    else:
        await update.message.reply_text(f"📝 Обрабатываю ваше сообщение: '{{message_text}}'\\n\\nПредложение: Попробуйте сформулировать мягче. Напишите 'тамам' для отправки или 'отбой' для отмены.")

def main():
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", handle_start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print(f"Starting Telegram bot {{TOKEN[:10]}}...")
    application.run_polling()

if __name__ == "__main__":
    main()
'''
            
            # Записываем скрипт во временный файл
            script_path = "temp_telegram_bot.py"
            with open(script_path, "w", encoding="utf-8") as f:
                f.write(script_content)
            
            # Запускаем бота в фоновом процессе
            process = subprocess.Popen([
                sys.executable, script_path
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Даем время на запуск
            import time
            time.sleep(2)
            
            if process.poll() is None:  # Процесс запущен
                return {
                    "status": "started",
                    "message": f"Super Empath Bot запущен! Найдите бота @{token.split(':')[0]} в Telegram",
                    "bot_username": f"Ваш бот: @super_empath_bot (или найдите по токену {token.split(':')[0]})",
                    "process_id": process.pid,
                    "instructions": [
                        "1. Найдите вашего бота в Telegram",
                        "2. Нажмите /start для создания сессии", 
                        "3. Отправьте ссылку-приглашение собеседнику",
                        "4. Начните общаться - бот будет предлагать улучшения"
                    ]
                }
            else:
                return {"error": "Failed to start bot", "details": process.stderr.read().decode()}
                
        elif operation == "stop":
            # Находим и останавливаем процесс бота
            import psutil
            stopped_count = 0
            
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if 'python' in proc.info['name'].lower() and 'temp_telegram_bot.py' in str(proc.info['cmdline']):
                        proc.terminate()
                        stopped_count += 1
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            # Удаляем временный файл
            if os.path.exists("temp_telegram_bot.py"):
                os.remove("temp_telegram_bot.py")
            
            return {
                "status": "stopped", 
                "message": f"Остановлено {stopped_count} процессов бота"
            }
            
        elif operation == "send_message":
            return {"error": "send_message operation not implemented in simplified version"}
            
        elif operation == "send_to_session":
            return {"error": "send_to_session operation not implemented in simplified version"}
            
        elif operation == "status":
            # Проверяем запущенные процессы бота
            import psutil
            running_bots = 0
            
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    if 'python' in proc.info['name'].lower() and 'temp_telegram_bot.py' in str(proc.info['cmdline']):
                        running_bots += 1
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    pass
            
            return {
                "running": running_bots > 0,
                "running_bots": running_bots,
                "message": f"Найдено {running_bots} запущенных ботов"
            }
            
        elif operation == "status":
            status = get_server_status()
            return status
            
        else:
            return {"error": f"Unknown operation: {operation}"}
            
    except Exception as e:
        logger.error(f"Error in telegram polling server: {e}")
        return {"error": str(e)}
