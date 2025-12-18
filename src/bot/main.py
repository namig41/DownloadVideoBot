#!/usr/bin/env python3
"""Запуск бота video_downloader"""
import asyncio
from src.bot.factory import main

if __name__ == "__main__":
    asyncio.run(main())
