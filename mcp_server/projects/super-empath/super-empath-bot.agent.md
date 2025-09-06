# Super Empath Telegram Bot Instructions

## Запуск Super Empath бота

Для запуска Super Empath Telegram бота выполните следующие шаги:

### 1. Перезапуск MCP сервера
**Важно!** Всегда перезапускайте MCP сервер перед запуском бота, чтобы убедиться, что все последние изменения в инструментах и конфигурациях применены.
```powershell
Get-Process python* | Where-Object { $_.ProcessName -like "*python*" } | Stop-Process -Force
```

### 2. Запуск именованного бота из конфигурации
Используйте `lng_batch_run` pipeline с именованным ботом для избежания конфликтов:
```json
{
  "pipeline_file": "mcp_server/projects/super-empath/config/telegram_pipeline.json"
}
```

### 3. Проверка статуса именованного бота
Для проверки статуса конкретного бота используйте `lng_telegram_polling_server` с указанием имени бота:
```json
{
  "operation": "status",
  "bot_name": "super_empath"
}
```

### 4. Остановка именованного бота (при необходимости)
Для остановки конкретного бота используйте `lng_telegram_polling_server` с указанием имени бота:
```json
{
  "operation": "stop",
  "bot_name": "super_empath"
}
```

## Структура конфигурации

### Основной pipeline (telegram_pipeline.json):
1. **Загрузка промпта** - `lng_file_read` из `prompt/default_super_empath.txt`
2. **Сохранение темплейта** - `lng_llm_prompt_template save` как "default_super_empath"
3. **Остановка старого бота** - `lng_telegram_polling_server stop` с именем "super_empath"
4. **Запуск нового бота** - `lng_telegram_polling_server start` с именем "super_empath" и `pipeline_file`

### Message pipeline (message_pipeline.json):
1. **LLM обработка** - `lng_llm_prompt_template use` с telegram контекстом

## Особенности реализации

### Именованные боты
- Каждый бот имеет уникальное имя (`bot_name: "super_empath"`)
- Автоматическая очистка конфликтующих экземпляров
- Предотвращение ошибки "Conflict: terminated by other getUpdates request"

### Pipeline_file подход
- Основной pipeline использует `pipeline_file` вместо inline конфигурации
- Expressions `{! JSON.stringify(telegram) !}` обрабатываются во время получения сообщений
- Telegram контекст доступен на момент обработки expressions

### LLM интеграция
- Промпт темплейт загружается из файла и сохраняется при старте бота
- Каждое сообщение обрабатывается через LLM с полной историей переписки
- Структурированный JSON вывод с полями `explanation` и `suggestion`

## Отладка

Логи сохраняются в:
- `mcp_server/logs/telegram/polling_server_*.log` - логи транспортного слоя
- `mcp_server/logs/telegram/super_empath_*.log` - логи бизнес-логики

### История сессий
Пользовательская история сохраняется в:
- `mcp_server/config/telegram/sessions/<user_id>.txt`
- Формат: `[USER_ID|USER_NAME] (timestamp): message content`

## Примечания

- MCP сервер запускается автоматически при первом вызове инструмента
- Бот автоматически загружает токен из переменной окружения `TELEGRAM_BOT_TOKEN`
- Все expressions обрабатываются динамически во время получения сообщений
- Система поддерживает множественные именованные боты без конфликтов
