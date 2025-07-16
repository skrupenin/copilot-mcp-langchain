#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import asyncio
import logging
import io

# Устанавливаем кодировку вывода UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../mcp_out.log')
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, mode='w', encoding='utf-8')
    ]
)
logger = logging.getLogger('mcp_fake_logger')
input_log_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../mcp_in.log')

async def read_input_file():
    """
    Асинхронное чтение строк из файла (`../mcp_in.log`) в цикле.
    """
    while True:
        try:
            if not os.path.exists(input_log_file):
                await asyncio.sleep(1)  # Ждем, если файла пока нет
                continue
            
            with open(input_log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            if lines:
                # Берем первую строку и удаляем ее из файла
                first_line = lines[0].rstrip('\n\r')
                logger.info(f"[>] {first_line}")
                print(first_line, flush=True)        

                # Записываем обратно оставшиеся строки (удаляем первую)
                with open(input_log_file, 'w', encoding='utf-8') as f:
                    f.writelines(lines[1:])
            else:
                await asyncio.sleep(1)  # Ждем, если файл пуст
        except Exception as e:
            logger.error(f"Ошибка чтения файла {input_log_file}: {e}")
            await asyncio.sleep(1)  # Если произошла ошибка, ждем перед новой попыткой

async def read_stdin():
    """
    Асинхронное чтение данных из stdin.
    """
    while True:
        line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
        line = line.strip()
        if line:
            logger.info(f"[<] {line}")

async def main():
    logger.info("stdin_logger started")
    logger.info(f"Logging to: {log_file}")

    # Параллельный запуск задач
    await asyncio.gather(
        read_stdin(),
        read_input_file()
    )

if __name__ == "__main__":
    asyncio.run(main())