# Super Empath Telegram Bot Instructions

## Запуск Super Empath бота

Для запуска Super Empath Telegram бота выполните следующие шаги:

### 1. Перезапуск MCP сервера
**Важно!** Всегда перезапускайте MCP сервер перед запуском бота, чтобы убедиться, что все последние изменения в инструментах и конфигурациях применены.
```powershell
Get-Process python* | Where-Object { $_.ProcessName -like "*python*" } | Stop-Process -Force
```

### 2. Запуск бота из конфигурации
Используйте MCP инструмент `lng_telegram_polling_server` с параметрами:
```json
{
  "operation": "start",
  "pipeline_file": "mcp_server/projects/super-empath/config/telegram_pipeline.json"
}
```

## Другие команды (при необходимости)
Проверка статуса:
```json
{"operation": "status"}
```
Остановка бота:
```json
{"operation": "stop"}
```

## Структура конфигурации

Конфигурационный файл должен содержать:
- `operation`: "start" 
- `pipeline`: массив шагов обработки сообщений
- Каждый шаг содержит:
  - `tool`: имя инструмента (lng_telegram_super_empath)
  - `params`: параметры с telegram_context
  - `output`: переменная для сохранения результата

## Отладка

Логи сохраняются в:
- `mcp_server/logs/telegram/polling_server_*.log` - логи транспортного слоя
- `mcp_server/logs/telegram/super_empath_*.log` - логи бизнес-логики

## Примечания

- MCP сервер запускается автоматически при первом вызове инструмента
- Бот использует токен из переменной окружения TELEGRAM_BOT_TOKEN
- Конфигурация позволяет гибко настраивать pipeline обработки
