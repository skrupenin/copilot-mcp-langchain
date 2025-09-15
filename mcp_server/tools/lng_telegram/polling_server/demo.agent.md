# # Демонстрация lng_telegram_polling_server

## Описание
Telegram Polling Server - универсальный инструмент для создания Telegram ботов с поддержкой сессий, пользователей и интеграции с pipeline.

## Основные возможности
- 🤖 **Polling режим** - работает без webhook, подходит для локальной разработки
- 👥 **Управление сессиями** - создание UUID-сессий и присоединение пользователей
- 🔗 **Deep Links** - автоматическое создание ссылок-приглашений
- 📨 **Отправка сообщений** - индивидуальные и групповые сообщения
- ⚙️ **Pipeline интеграция** - выполнение pipeline при получении сообщений
- 📊 **Мониторинг** - отслеживание статуса сервера, пользователей и сессий

## Демонстрация использования

### 1. Проверка статуса сервера
```json
{
  "operation": "status"
}
```

### 2. Запуск сервера
```json
{
  "operation": "start",
  "token": "YOUR_BOT_TOKEN",
  "pipeline": [
    {
      "tool": "lng_count_words",
      "params": {
        "input_text": "{! telegram.message !}"
      },
      "output": "word_stats"
    }
  ]
}
```

### 3. Отправка сообщения пользователю
```json
{
  "operation": "send_message",
  "user_id": 123456789,
  "message": "Привет! Это сообщение от бота."
}
```

### 4. Отправка сообщения всем в сессии
```json
{
  "operation": "send_to_session",
  "session_id": "550e8400-e29b-41d4-a716-446655440000",
  "message": "Сообщение для всех участников сессии",
  "exclude_user": 123456789
}
```

### 5. Остановка сервера
```json
{
  "operation": "stop"
}
```

## Workflow для пользователей

### Создание новой сессии
1. Пользователь запускает бота `/start`
2. Бот создает UUID-сессию
3. Бот отправляет ссылку-приглашение: `https://t.me/yourbot?start=uuid`

### Присоединение к сессии
1. Пользователь переходит по ссылке
2. Автоматически выполняется `/start uuid`
3. Пользователь присоединяется к существующей сессии
4. Все участники получают уведомление

### Обработка сообщений
1. Пользователь отправляет сообщение
2. Выполняется настроенный pipeline
3. Результат обработки доступен для бизнес-логики

## Интеграция с проектом super-empath

Этот инструмент идеально подходит для проекта super-empath:

```json
{
  "operation": "start",
  "pipeline": [
    {
      "tool": "lng_llm_rag_search",
      "params": {
        "query": "{! telegram.message !}",
        "prompt_template": "empathy_filter"
      },
      "output": "filtered_message"
    },
    {
      "tool": "lng_telegram_polling_server",
      "params": {
        "operation": "send_message",
        "user_id": "{! telegram.user_id !}",
        "message": "Предлагаю переформулировать: {! filtered_message.response !}"
      }
    }
  ]
}
```

## Настройка

1. Создайте бота через @BotFather в Telegram
2. Добавьте токен в `.env` файл:
   ```
   TELEGRAM_BOT_TOKEN=your_bot_token_here
   ```
3. Запустите инструмент с операцией `start`

## Примечания
- Сервер работает в polling режиме (опрашивает Telegram API)
- Подходит для разработки и небольших проектов
- Для продакшена рекомендуется webhook режим
- Pipeline выполняется для каждого входящего сообщения

Этот файл содержит примеры использования инструмента для создания Telegram ботов.

## Базовое тестирование

### 1. Проверка статуса сервера
```json
{
  "operation": "status"
}
```

### 2. Запуск сервера (требует токен в .env)
```json
{
  "operation": "start",
  "token": "YOUR_BOT_TOKEN"
}
```

### 3. Отправка сообщения пользователю
```json
{
  "operation": "send_message", 
  "user_id": 123456789,
  "message": "Привет из MCP!"
}
```

### 4. Остановка сервера
```json
{
  "operation": "stop"
}
```

## Интеграция с pipeline

### Эхо-бот с обработкой
```json
{
  "operation": "start",
  "pipeline": [
    {
      "tool": "lng_count_words",
      "params": {"input_text": "{! telegram.message !}"},
      "output": "stats"
    },
    {
      "tool": "lng_telegram_polling_server",
      "params": {
        "operation": "send_message",
        "user_id": "{! telegram.user_id !}",
        "message": "Вы написали {! stats.word_count !} слов: {! telegram.message !}"
      }
    }
  ]
}
```

### LLM интеграция
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

## Настройка для проекта Super Empath

### Pipeline для эмоциональной обработки
```json
{
  "operation": "start",
  "pipeline": [
    {
      "type": "condition",
      "condition": "{! telegram.message === 'тамам' !}",
      "then": [
        {
          "tool": "lng_telegram_polling_server",
          "params": {
            "operation": "send_to_session",
            "session_id": "{! telegram.user_state.session_id !}",
            "message": "{! telegram.user_state.current_message_processing !}",
            "exclude_user": "{! telegram.user_id !}"
          }
        }
      ],
      "else": [
        {
          "type": "condition", 
          "condition": "{! telegram.message === 'отбой' !}",
          "then": [
            {
              "tool": "lng_telegram_polling_server",
              "params": {
                "operation": "send_message",
                "user_id": "{! telegram.user_id !}",
                "message": "❌ Текущая обработка отменена"
              }
            }
          ],
          "else": [
            {
              "tool": "lng_llm_prompt_template",
              "params": {
                "command": "use",
                "template_name": "empath_processor",
                "original_message": "{! telegram.message !}",
                "user_context": "{! telegram.user_state !}"
              },
              "output": "processed_message"
            },
            {
              "tool": "lng_telegram_polling_server",
              "params": {
                "operation": "send_message",
                "user_id": "{! telegram.user_id !}",
                "message": "💭 Предлагаю отправить:\n\n{! processed_message.result !}\n\n✅ Напишите 'тамам' для отправки\n🔄 Или попросите изменить"
              }
            }
          ]
        }
      ]
    }
  ]
}
```

## Требования для запуска

1. **Создание бота в Telegram:**
   - Напишите @BotFather в Telegram
   - Выполните `/newbot` 
   - Укажите имя и username бота
   - Получите токен

2. **Настройка окружения:**
   ```env
   TELEGRAM_BOT_TOKEN=your_bot_token_here
   ```

3. **Тестирование:**
   - Запустите сервер через MCP
   - Найдите бота в Telegram
   - Отправьте `/start` для создания сессии
   - Поделитесь ссылкой с собеседником
