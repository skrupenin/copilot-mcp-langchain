"""
Super Empath - бизнес-логика эмоционального переводчика для улучшения коммуникации в отношениях
"""

import json
import uuid
import os
from datetime import datetime
from typing import Dict, Any

import mcp.types as types

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
                "telegram_context": {
                    "type": "object",
                    "description": "Telegram context object with user and message information"
                }
            },
            "required": ["telegram_context"]
        }
    }

class SuperEmpathProcessor:
    """Процессор Super Empath для обработки сообщений"""
    
    def __init__(self):
        self.session_file = "mcp_server/config/telegram/super_empath_sessions.json"
        self._ensure_session_file()
        
    def _ensure_session_file(self):
        """Убеждаемся что файл сессий существует"""
        os.makedirs(os.path.dirname(self.session_file), exist_ok=True)
        if not os.path.exists(self.session_file):
            with open(self.session_file, 'w', encoding='utf-8') as f:
                json.dump({"sessions": {}, "users": {}}, f)
                
    def _load_sessions(self) -> dict:
        """Загрузка сессий из файла"""
        try:
            with open(self.session_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {"sessions": {}, "users": {}}
            
    def _save_sessions(self, data: dict):
        """Сохранение сессий в файл"""
        try:
            with open(self.session_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Failed to save sessions: {e}")
            
    def improve_message(self, message: str) -> str:
        """Улучшение сообщения для более мягкого общения"""
        message_lower = message.lower()
        
        # Агрессивные слова и фразы
        aggressive_patterns = [
            ("достал", "Я чувствую усталость от ситуации, можем это обсудить?"),
            ("бесишь", "Меня что-то расстраивает в этой ситуации"),
            ("надоел", "Мне нужен перерыв, можем поговорить позже?"),
            ("дурак", "У меня есть другое мнение по этому вопросу"),
            ("идиот", "Давайте разберемся в ситуации спокойно"),
            ("тупой", "Мне кажется, здесь есть недопонимание"),
            ("не хочу", "Мне сейчас сложно это делать"),
            ("не буду", "Я предпочел бы другой вариант"),
            ("отстань", "Мне нужно немного времени"),
            ("заткнись", "Давайте сделаем паузу в разговоре"),
            ("противно", "Меня это не очень привлекает"),
            ("ненавижу", "Это вызывает у меня негативные эмоции")
        ]
        
        for pattern, replacement in aggressive_patterns:
            if pattern in message_lower:
                return replacement
                
        # Обработка восклицательных знаков (признак эмоционального напряжения)
        if "!" in message and len(message) > 20:
            improved = message.replace("!", ".").strip()
            return improved + " Что думаешь об этом?"
            
        # Обработка команд/требований
        command_words = ["должен", "обязан", "немедленно", "сейчас же"]
        if any(word in message_lower for word in command_words):
            return f"Мне важно, чтобы: {message.lower().replace('должен', 'мог').replace('обязан', 'смог')}. Как считаешь?"
            
        # Если сообщение нейтральное, добавляем мягкости
        if len(message) > 10 and not message.endswith("?"):
            return f"Я хотел сказать: {message}. Как ты к этому относишься?"
            
        return message
        
    def handle_command(self, telegram_context: dict) -> dict:
        """Обработка команд Super Empath"""
        message = telegram_context.get("message", "").strip()
        user_id = telegram_context.get("user_id")
        
        if message.startswith("/start"):
            return self._handle_start_command(telegram_context)
        elif message == "тамам":
            return self._handle_approve_command(telegram_context)
        elif message == "отбой":
            return self._handle_cancel_command(telegram_context)
        else:
            return self._handle_regular_message(telegram_context)
            
    def _handle_start_command(self, telegram_context: dict) -> dict:
        """Обработка команды /start"""
        user_id = telegram_context.get("user_id")
        first_name = telegram_context.get("first_name", "Пользователь")
        message = telegram_context.get("message", "")
        
        # Извлекаем session_id из deep link
        session_id = None
        if " " in message:
            parts = message.split(" ", 1)
            if len(parts) > 1:
                session_id = parts[1]
                
        data = self._load_sessions()
        
        if session_id:
            # Присоединение к существующей сессии
            if session_id in data["sessions"]:
                session = data["sessions"][session_id]
                if user_id not in session["participants"]:
                    session["participants"].append(user_id)
                    session["last_activity"] = datetime.now().isoformat()
                    
                data["users"][str(user_id)] = {
                    "session_id": session_id,
                    "first_name": first_name,
                    "joined_at": datetime.now().isoformat()
                }
                
                self._save_sessions(data)
                
                return {
                    "response": f"✅ Добро пожаловать в Super Empath, {first_name}!\n\nВы присоединились к сессии {session_id}",
                    "session_id": session_id,
                    "action": "joined_session"
                }
            else:
                return {
                    "response": "❌ Сессия не найдена. Попросите новую ссылку-приглашение.",
                    "action": "session_not_found"
                }
        else:
            # Создание новой сессии
            new_session_id = str(uuid.uuid4())[:8]  # Короткий ID для удобства
            
            data["sessions"][new_session_id] = {
                "participants": [user_id],
                "created_at": datetime.now().isoformat(),
                "last_activity": datetime.now().isoformat(),
                "created_by": user_id
            }
            
            data["users"][str(user_id)] = {
                "session_id": new_session_id,
                "first_name": first_name,
                "joined_at": datetime.now().isoformat()
            }
            
            self._save_sessions(data)
            
            # Генерируем ссылку-приглашение (предполагаем что bot username будет подставлен)
            invite_link = f"https://t.me/BOT_USERNAME?start={new_session_id}"
            
            response = f"""🎯 Добро пожаловать в Super Empath, {first_name}!

**Super Empath** - ваш эмоциональный переводчик для лучшего общения.

Ваша сессия: `{new_session_id}`
Ссылка для приглашения: {invite_link}

**Как пользоваться:**
1. Отправьте эту ссылку вашему собеседнику
2. Пишите сообщения как обычно
3. Бот предложит более мягкие формулировки
4. Говорите "тамам" для отправки или "отбой" для отмены

Начните общение! 💬"""

            return {
                "response": response,
                "session_id": new_session_id,
                "invite_link": invite_link,
                "action": "created_session"
            }
            
    def _handle_regular_message(self, telegram_context: dict) -> dict:
        """Обработка обычного сообщения"""
        message = telegram_context.get("message", "")
        user_id = telegram_context.get("user_id")
        
        # Проверяем, что пользователь в сессии
        data = self._load_sessions()
        user_data = data["users"].get(str(user_id))
        
        if not user_data:
            return {
                "response": "Пожалуйста, сначала выполните команду /start",
                "action": "not_registered"
            }
            
        # Улучшаем сообщение
        improved = self.improve_message(message)
        
        # Сохраняем текущее сообщение для последующего одобрения
        user_data["pending_message"] = {
            "original": message,
            "improved": improved,
            "timestamp": datetime.now().isoformat()
        }
        
        data["users"][str(user_id)] = user_data
        self._save_sessions(data)
        
        response = f"""📝 **Ваше сообщение:**
"{message}"

💡 **Предлагаю переформулировать:**
"{improved}"

Напишите "тамам" для отправки или "отбой" для отмены."""

        return {
            "response": response,
            "original": message,
            "improved": improved,
            "action": "message_processed"
        }
        
    def _handle_approve_command(self, telegram_context: dict) -> dict:
        """Обработка команды одобрения 'тамам'"""
        user_id = telegram_context.get("user_id")
        
        data = self._load_sessions()
        user_data = data["users"].get(str(user_id))
        
        if not user_data or "pending_message" not in user_data:
            return {
                "response": "Нет сообщения для отправки",
                "action": "no_pending_message"
            }
            
        pending = user_data["pending_message"]
        session_id = user_data["session_id"]
        
        if session_id not in data["sessions"]:
            return {
                "response": "Ошибка: сессия не найдена",
                "action": "session_error"
            }
            
        session = data["sessions"][session_id]
        participants = session["participants"]
        
        # Очищаем pending message
        del user_data["pending_message"]
        data["users"][str(user_id)] = user_data
        self._save_sessions(data)
        
        # Возвращаем информацию для отправки другим участникам
        other_participants = [p for p in participants if p != user_id]
        
        return {
            "response": f"✅ Сообщение отправлено {len(other_participants)} участникам",
            "action": "message_approved",
            "improved_message": pending["improved"],
            "original_message": pending["original"],
            "recipients": other_participants,
            "sender_name": user_data.get("first_name", "Участник"),
            # Специальное поле для автоматической обработки транспортным слоем
            "auto_send": {
                "to_users": other_participants,
                "message": f"💬 Сообщение от {user_data.get('first_name', 'Участника')}:\n\n{pending['improved']}"
            }
        }
        
    def _handle_cancel_command(self, telegram_context: dict) -> dict:
        """Обработка команды отмены 'отбой'"""
        user_id = telegram_context.get("user_id")
        
        data = self._load_sessions()
        user_data = data["users"].get(str(user_id))
        
        if not user_data or "pending_message" not in user_data:
            return {
                "response": "Нет активной операции для отмены",
                "action": "no_pending_operation"
            }
            
        # Очищаем pending message
        del user_data["pending_message"]
        data["users"][str(user_id)] = user_data
        self._save_sessions(data)
        
        return {
            "response": "❌ Операция отменена",
            "action": "operation_cancelled"
        }

# Создаем глобальный экземпляр процессора
_processor = SuperEmpathProcessor()

def tool_lng_telegram_super_empath(
    telegram_context: dict
) -> Dict[str, Any]:
    """
    Super Empath - бизнес-логика эмоционального переводчика
    
    Обрабатывает сообщение через эмоциональный переводчик
    Принимает telegram_context как объект или JSON строку
    """
    
    try:
        if not telegram_context:
            return {"error": "telegram_context is required"}
        
        # Универсальная обработка: поддерживаем и объект, и JSON строку
        context_obj = telegram_context
        if isinstance(telegram_context, str):
            import json
            try:
                context_obj = json.loads(telegram_context)
                logger.info("Parsed telegram_context from JSON string")
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON in telegram_context: {e}")
                return {"error": f"Invalid telegram_context JSON: {e}"}
        
        # Проверяем что получили словарь
        if not isinstance(context_obj, dict):
            logger.error(f"telegram_context must be dict or JSON string, got: {type(telegram_context)}")
            return {"error": f"Invalid telegram_context type: {type(telegram_context)}"}
        
        # Обрабатываем сообщение
        result = _processor.handle_command(context_obj)
        
        logger.info(f"Processed message from user {context_obj.get('user_id')}: {context_obj.get('message')}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error in super empath tool: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return {"error": f"Super empath processing failed: {e}"}

async def run_tool(name: str, parameters: dict) -> list[types.Content]:
    """Executes the Super Empath tool."""
    try:
        result = tool_lng_telegram_super_empath(**parameters)
        return [types.TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]
    except Exception as e:
        error_result = {"error": str(e)}
        return [types.TextContent(type="text", text=json.dumps(error_result, ensure_ascii=False))]
