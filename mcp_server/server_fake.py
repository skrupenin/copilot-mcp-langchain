#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import asyncio
import logging
import io

# Set UTF-8 output encoding
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
    Asynchronously reads lines from file (`../mcp_in.log`) in a loop.
    """
    while True:
        try:
            if not os.path.exists(input_log_file):
                await asyncio.sleep(1)  # Wait if file doesn't exist yet
                continue
            
            with open(input_log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            if lines:
                # Take the first line and remove it from the file
                first_line = lines[0].rstrip('\n\r')
                logger.info(f"[>] {first_line}")
                print(first_line, flush=True)                
                # Write back remaining lines (remove the first one)
                with open(input_log_file, 'w', encoding='utf-8') as f:
                    f.writelines(lines[1:])
            else:
                await asyncio.sleep(1)  # Wait if file is empty
        except Exception as e:
            logger.error(f"Error reading file {input_log_file}: {e}")
            await asyncio.sleep(1)  # If error occurred, wait before retrying

async def read_stdin():
    """
    Asynchronously reads data from stdin.
    """
    while True:
        line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
        line = line.strip()
        if line:
            logger.info(f"[<] {line}")

async def main():
    logger.info("stdin_logger started")
    logger.info(f"Logging to: {log_file}")

    # Parallel task execution
    await asyncio.gather(
        read_stdin(),
        read_input_file()
    )

if __name__ == "__main__":
    asyncio.run(main())