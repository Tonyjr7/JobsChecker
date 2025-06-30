import json
import asyncio
import logging
from services.groq_service import process_with_groq
from services.gemini_service import process_with_gemini
from helper_function.scrape_page import scrape

logger = logging.getLogger(__name__)

def handle_job(url: str, profile: str, ai: str):
        try:
            html_content = scrape.scrape_page(url)
            # llm_response = process_with_groq(html_content, profile)
            if ai == "groq":
                llm_response = process_with_groq(html_content, profile)
                parsed_response = json.loads(llm_response)
                results.append({
                    "url": url,
                    "response": parsed_response
                })
                await asyncio.sleep(10)
            elif ai == "gemini":
                llm_response = process_with_gemini(html_content, profile)
                gemini_result = llm_response
                results.append({
                    "url": url,
                    "response": gemini_result
                })
                await asyncio.sleep(30)
            else:
                raise HTTPException(status_code=400, detail="Please specify a valid AI: 'groq' or 'gemini'")

        except Exception as e:
            logger.error(f"Error processing URL {url}: {str(e)}")
            results.append({
                "url": url,
                "error": f"Failed to process the job listing: {str(e)}"
            })