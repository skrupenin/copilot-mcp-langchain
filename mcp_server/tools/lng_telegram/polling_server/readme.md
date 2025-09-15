# Telegram Polling Server

Универсальный инструмент для создания Telegram ботов с поддержкой сессий и pipeline интеграции.

## Возможности

### 🤖 Основной функционал
- **Polling режим** - получение сообщений от Telegram API
- **Управление сессиями** - создание и управление групповыми чатами с UUID
- **Deep Links** - подключение пользователей через ссылки вида `https://t.me/bot?start=uuid`
- **Pipeline интеграция** - автоматическая обработка сообщений через другие MCP инструменты
- **Состояния пользователей** - отслеживание активности и контекста

### 🔧 Операции

#### `start` - Запуск сервера
```json
{
  "operation": "start",
  "token": "YOUR_BOT_TOKEN",
  "pipeline": [
    {
      "tool": "lng_count_words",
      "params": {"input_text": "{! telegram.message !}"},
      "output": "word_stats"
    }
  ]
}
```

#### `stop` - Остановка сервера
```json
{
  "operation": "stop"
}
```

#### `send_message` - Отправка сообщения пользователю
```json
{
  "operation": "send_message",
  "user_id": 123456789,
  "message": "Привет! Как дела?"
}
```

#### `send_to_session` - Отправка сообщения всем в сессии
```json
{
  "operation": "send_to_session",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Сообщение для всех участников",
  "exclude_user": 123456789
}
```

#### `status` - Получение статуса сервера
```json
{
  "operation": "status"
}
```

## Процесс работы

### 1. Создание сессии
```
Пользователь А → /start → Бот создает UUID сессию → Отправляет ссылку-приглашение
```

### 2. Присоединение к сессии  
```
Пользователь Б → Переходит по ссылке → Автоматически присоединяется к сессии
```

### 3. Обработка сообщений
```
Сообщение → Pipeline обработка → Результат через MCP инструменты
```

## Конфигурация

### Переменные окружения (.env)
```env
TELEGRAM_BOT_TOKEN=your_bot_token_here
```

### Pipeline контекст
В pipeline доступны следующие переменные:
```json
{
  "telegram": {
    "user_id": 123456789,
    "message": "текст сообщения",
    "user_state": {...},
    "session_state": {...},
    "update": "telegram_update_object",
    "bot": "server_instance"
  }
}
```

## Примеры использования

### Простой эхо-бот
```json
{
  "operation": "start",
  "pipeline": [
    {
      "tool": "lng_telegram_polling_server",
      "params": {
        "operation": "send_message",
        "user_id": "{! telegram.user_id !}",
        "message": "Вы написали: {! telegram.message !}"
      }
    }
  ]
}
```

### Обработка через LLM
```json
{
  "operation": "start",
  "pipeline": [
    {
      "tool": "lng_llm_chain_of_thought",
      "params": {
        "question": "{! telegram.message !}"
      },
      "output": "llm_response"
    },
    {
      "tool": "lng_telegram_polling_server", 
      "params": {
        "operation": "send_message",
        "user_id": "{! telegram.user_id !}",
        "message": "{! llm_response.answer !}"
      }
    }
  ]
}
```

## Структура состояний

### UserState
```python
@dataclass
class UserState:
    user_id: int
    username: str
    first_name: str
    session_id: Optional[str] = None
    current_message_processing: Optional[str] = None
    joined_at: Optional[str] = None
```

### SessionState  
```python
@dataclass
class SessionState:
    session_id: str
    participants: List[int]
    created_at: str
    last_activity: str
    message_queue: List[Dict] = None
```

## Требования

- `python-telegram-bot` - для работы с Telegram API
- `asyncio` - для асинхронной обработки
- `python-dotenv` - для загрузки переменных окружения

## Безопасность

- Токен бота храните в `.env` файле
- UUID сессии обеспечивают уникальность и безопасность
- Нет хранения персональных данных пользователей
