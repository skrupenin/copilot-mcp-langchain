"""
Super Empath - бизнес-логика эмоционального переводчика
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

from mcp_server.logging_config import setup_instance_logger, close_instance_logger

# Логгер будет создан при первом использовании
logger = setup_instance_logger("super_empath", "telegram")

async def tool_info() -> dict:
    """Returns information about the lng_telegram_super_empath tool."""
    return {
        "description": "Super Empath - бизнес-логика эмоционального переводчика для улучшения коммуникации в отношениях",
        "schema": {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["start_bot", "stop_bot", "status", "process_message"],
                    "description": "Operation to perform"
                },
                "message": {
                    "type": "string",
                    "description": "Message to process"
                },
                "user_id": {
                    "type": "integer",
                    "description": "User ID"
                },
                "session_id": {
                    "type": "string", 
                    "description": "Session ID"
                },
                "pipeline": {
                    "type": "array",
                    "description": "Pipeline to execute for message processing",
                    "items": {
                        "type": "object"
                    }
                }
            },
            "required": ["operation"]
        }
    }

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

class SuperEmpathBot:
    """Бизнес-логика Super Empath бота"""
    
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
            
            # Обрабатываем команды Super Empath
            if message_text == "тамам":
                await self._approve_message(user_id, update)
            elif message_text == "отбой":
                await self._cancel_message(user_id, update)
            else:
                # Обрабатываем обычное сообщение
                await self._process_user_message(user_id, message_text, update)
            
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
            join_message = f"👋 {user_state.first_name} присоединился к сессии Super Empath"
            
            for participant_id in session.participants:
                if participant_id != user_id:
                    await self.bot.send_message(participant_id, join_message)
                    
            await self.bot.send_message(user_id, f"✅ Добро пожаловать в Super Empath!\n\nВы присоединились к сессии {session_id}")
            logger.info(f"User {user_id} joined session {session_id}")
        else:
            await self.bot.send_message(user_id, "❌ Сессия не найдена")
            
    async def _send_invitation_link(self, user_id: int, session_id: str):
        """Отправка ссылки-приглашения"""
        bot_username = (await self.bot.get_me()).username
        invite_link = f"https://t.me/{bot_username}?start={session_id}"
        
        message = f"""🎯 Добро пожаловать в Super Empath!

**Super Empath** - ваш эмоциональный переводчик для лучшего общения.

Ваша сессия: `{session_id}`
Ссылка для приглашения: {invite_link}

**Как пользоваться:**
1. Отправьте эту ссылку вашему собеседнику
2. Пишите сообщения как обычно
3. Бот предложит более мягкие формулировки
4. Говорите "тамам" для отправки или "отбой" для отмены

Начните общение! 💬"""
        
        await self.bot.send_message(user_id, message, parse_mode='Markdown')

    async def _process_user_message(self, user_id: int, message_text: str, update: Update):
        """Обработка пользовательского сообщения через pipeline"""
        try:
            # Сохраняем текущее сообщение для обработки
            self.users[user_id].current_message_processing = message_text
            
            # Выполняем pipeline для обработки сообщения (заглушка)
            # TODO: Интеграция с lng_batch_run
            
            # Простая демо-обработка
            improved_message = await self._demo_improve_message(message_text)
            
            response = f"""📝 **Ваше сообщение:**
"{message_text}"

💡 **Предлагаю переформулировать:**
"{improved_message}"

Напишите "тамам" для отправки или "отбой" для отмены."""
            
            await update.message.reply_text(response, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            await update.message.reply_text("Ошибка при обработке сообщения")

    async def _demo_improve_message(self, message: str) -> str:
        """Демо-функция улучшения сообщения (заглушка для LLM)"""
        # Простые правила для демо
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["достал", "бесишь", "надоел"]):
            return "Я чувствую усталость от ситуации, можем это обсудить?"
        elif any(word in message_lower for word in ["дурак", "идиот", "тупой"]):
            return "У меня есть другое мнение по этому вопросу, давайте разберемся"
        elif any(word in message_lower for word in ["не хочу", "не буду", "отстань"]):
            return "Мне сейчас сложно это делать, можем найти компромисс?"
        elif "!" in message and len(message) > 20:
            return message.replace("!", ".").strip() + " Что думаешь?"
        else:
            return f"Я хотел сказать: {message}. Как считаешь?"

    async def _approve_message(self, user_id: int, update: Update):
        """Одобрение и отправка сообщения"""
        user_state = self.users[user_id]
        
        if not user_state.current_message_processing:
            await update.message.reply_text("Нет сообщения для отправки")
            return
            
        if not user_state.session_id:
            await update.message.reply_text("Вы не подключены к сессии")
            return
            
        # Получаем улучшенное сообщение
        improved_message = await self._demo_improve_message(user_state.current_message_processing)
        
        # Отправляем всем участникам сессии кроме отправителя
        session = self.sessions[user_state.session_id]
        sent_count = 0
        
        for participant_id in session.participants:
            if participant_id != user_id:
                try:
                    await self.bot.send_message(
                        participant_id, 
                        f"💬 Сообщение от {user_state.first_name}:\n\n{improved_message}"
                    )
                    sent_count += 1
                except Exception as e:
                    logger.error(f"Failed to send message to {participant_id}: {e}")
        
        # Подтверждение отправителю
        await update.message.reply_text(f"✅ Сообщение отправлено {sent_count} участникам")
        
        # Очищаем состояние
        user_state.current_message_processing = None

    async def _cancel_message(self, user_id: int, update: Update):
        """Отмена обработки сообщения"""
        user_state = self.users[user_id]
        
        if user_state.current_message_processing:
            user_state.current_message_processing = None
            await update.message.reply_text("❌ Операция отменена")
        else:
            await update.message.reply_text("Нет активной операции для отмены")

# Глобальный инстанс
_bot_instance: Optional[SuperEmpathBot] = None

def close_super_empath_logger():
    """Закрытие логгера super_empath"""
    try:
        close_instance_logger("super_empath", "telegram")
    except Exception as e:
        print(f"Error closing super_empath logger: {e}")

def get_bot_status() -> Dict:
    """Получение статуса бота"""
    global _bot_instance
    
    if not _bot_instance:
        return {"running": False, "users": 0, "sessions": 0}
        
    return {
        "running": _bot_instance.running,
        "users": len(_bot_instance.users),
        "sessions": len(_bot_instance.sessions),
        "user_list": list(_bot_instance.users.keys()),
        "session_list": list(_bot_instance.sessions.keys())
    }

def tool_lng_telegram_super_empath(
    operation: str,
    message: str = None,
    user_id: int = None,
    session_id: str = None,
    pipeline: List[Dict] = None
) -> Dict[str, Any]:
    """
    Super Empath - бизнес-логика эмоционального переводчика
    
    Operations:
    - start_bot: Запуск бота Super Empath
    - stop_bot: Остановка бота
    - status: Получение статуса
    - process_message: Обработка сообщения через LLM
    """
    
    try:
        if operation == "start_bot":
            # Пересоздаем логгер при запуске
            global logger
            close_super_empath_logger()
            logger = setup_instance_logger("super_empath", "telegram")
            
            # Получаем токен из .env
            from dotenv import load_dotenv
            load_dotenv()
            token = os.getenv("TELEGRAM_BOT_TOKEN")
            
            if not token:
                return {"error": "TELEGRAM_BOT_TOKEN not found in .env file"}
            
            # Запускаем через lng_telegram_polling_server
            import subprocess
            import sys
            
            # Создаем конфигурацию для запуска
            config = {
                "operation": "start",
                "token": token,
                "pipeline": pipeline or [
                    {
                        "tool": "lng_telegram_super_empath",
                        "params": {
                            "operation": "process_message",
                            "message": "{! telegram.message !}",
                            "user_id": "{! telegram.user_id !}"
                        },
                        "output": "processed_result"
                    }
                ]
            }
            
            # Используем existing polling server
            from mcp_server.tools.lng_telegram.polling_server.tool import tool_lng_telegram_polling_server
            
            result = tool_lng_telegram_polling_server(**config)
            
            if "error" not in result:
                return {
                    "status": "started",
                    "message": "Super Empath bot started successfully",
                    "details": result
                }
            else:
                return result
                
        elif operation == "stop_bot":
            from mcp_server.tools.lng_telegram.polling_server.tool import tool_lng_telegram_polling_server
            
            result = tool_lng_telegram_polling_server(operation="stop")
            
            # Закрываем логгер super_empath при остановке
            close_super_empath_logger()
            
            return result
            
        elif operation == "status":
            status = get_bot_status()
            
            # Проверяем также статус polling server
            from mcp_server.tools.lng_telegram.polling_server.tool import tool_lng_telegram_polling_server
            polling_status = tool_lng_telegram_polling_server(operation="status")
            
            return {
                "super_empath": status,
                "polling_server": polling_status
            }
            
        elif operation == "process_message":
            if not message:
                return {"error": "message is required for process_message operation"}
            
            # Простая обработка сообщения (синхронная версия для демо)
            def improve_message_sync(msg: str) -> str:
                """Синхронная версия улучшения сообщения"""
                msg_lower = msg.lower()
                
                if any(word in msg_lower for word in ["достал", "бесишь", "надоел"]):
                    return "Я чувствую усталость от ситуации, можем это обсудить?"
                elif any(word in msg_lower for word in ["дурак", "идиот", "тупой"]):
                    return "У меня есть другое мнение по этому вопросу, давайте разберемся"
                elif any(word in msg_lower for word in ["не хочу", "не буду", "отстань"]):
                    return "Мне сейчас сложно это делать, можем найти компромисс?"
                elif "!" in msg and len(msg) > 20:
                    return msg.replace("!", ".").strip() + " Что думаешь?"
                else:
                    return f"Я хотел сказать: {msg}. Как считаешь?"
            
            improved = improve_message_sync(message)
            
            return {
                "original": message,
                "improved": improved,
                "status": "processed"
            }
            
        else:
            return {"error": f"Unknown operation: {operation}"}
            
    except Exception as e:
        logger.error(f"Error in super empath tool: {e}")
        return {"error": str(e)}

async def run_tool(name: str, parameters: dict) -> list[types.Content]:
    """Executes the Super Empath tool."""
    try:
        result = tool_lng_telegram_super_empath(**parameters)
        return [types.TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]
    except Exception as e:
        error_result = {"error": str(e)}
        return [types.TextContent(type="text", text=json.dumps(error_result, ensure_ascii=False))]
