import asyncio
from dotenv import load_dotenv
import os
from ingestion.pipeline import run_pipeline

load_dotenv()

async def main():
    books = await run_pipeline()
    for book in books:
        print(f"{book.title} - {book.authors}")

asyncio.run(main())