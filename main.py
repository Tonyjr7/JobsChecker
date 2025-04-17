# app/main.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import logging
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from services.groq_service import process_with_groq
from helper_function.parse_ai_response import parse_response
from helper_function.scrape_page import scrape

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class LinkRequest(BaseModel):
    links: List[str]


@app.post("/check-jobs")
async def check_jobs(data: LinkRequest, profile: str = ""):
    results = []

    for url in data.links:
        try:
            html_content = scrape.scrape_page(url)
            print(profile)
            llm_response = process_with_groq(html_content, profile)
            print(llm_response)
            groq_result = parse_response.parse_groq_response(llm_response)

            results.append({
                "url": url,
                **groq_result
            })

        except Exception as e:
            logger.error(f"Error processing URL {url}: {str(e)}")
            results.append({
                "url": url,
                "error": f"Failed to process the job listing: {str(e)}"
            })

        await asyncio.sleep(8)  # Add a 2-second delay between requests

    return {"results": results}
