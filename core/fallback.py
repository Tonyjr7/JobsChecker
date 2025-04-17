# import logging
# from fastapi import FastAPI, Request
# from pydantic import BaseModel
# from typing import List
# from bs4 import BeautifulSoup
# from playwright.async_api import async_playwright
# import re
# import asyncio
# from fastapi.middleware.cors import CORSMiddleware
# from urllib.parse import urlparse

# # Setup logging
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# app = FastAPI()

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # Replace "*" with your frontend origin in production
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # U.S. States list
# US_STATES = [
#     "alabama", "alaska", "arizona", "arkansas", "california", "colorado", "connecticut", "delaware", "florida",
#     "georgia", "hawaii", "idaho", "illinois", "indiana", "iowa", "kansas", "kentucky", "louisiana", "maine",
#     "maryland", "massachusetts", "michigan", "minnesota", "mississippi", "missouri", "montana", "nebraska", 
#     "nevada", "new hampshire", "new jersey", "new mexico", "new york", "north carolina", "north dakota", 
#     "ohio", "oklahoma", "oregon", "pennsylvania", "rhode island", "south carolina", "south dakota", "tennessee", 
#     "texas", "utah", "vermont", "virginia", "washington", "west virginia", "wisconsin", "wyoming"
# ]

# app_states_keywords = US_STATES + ["united states", "us", "united states of america"]

# class LinkRequest(BaseModel):
#     links: List[str]

# ROLE_KEYWORDS = {
#     "web": ["frontend", "backend", "fullstack", "web developer", "software engineer", "software", "python", "java", "engineer", "developer"],
#     "devops": ["architect", "cloud", "cloud infrastructure", "devops", "site reliability", "sre", "platform engineer", "cloud engineer", "infrastructure engineer", "systems engineer", "ci/cd", "kubernetes", "docker", "terraform", "aws", "azure", "gcp", "cloud infrastructure", "build and release", "automation engineer", "deployment engineer", "solutions"],
#     "ml": ["data scientist", "machine learning", "ml engineer", "ai engineer"]
# }

# def get_keywords(profile):
#     return ROLE_KEYWORDS.get(profile.lower(), [])

# async def scrape_job(url: str, profile: str = "web"):
#     logger.info(f"Starting to scrape job from URL: {url} for profile: {profile}")
#     try:
#         async with async_playwright() as p:
#             browser = await p.chromium.launch(headless=True)
#             page = await browser.new_page()
#             await page.goto(url, timeout=80000)
#             html = await page.content()
#             await browser.close()

#         soup = BeautifulSoup(html, "html.parser")
#         text = soup.get_text(separator=" ", strip=True).lower()

#         domain = urlparse(url).netloc

#         def get_title_and_location():
#             # Greenhouse
#             if "greenhouse.io" in domain:
#                 title = soup.select_one("h1.app-title") or soup.select_one("h1")
#                 location = soup.select_one("div.location") or soup.select_one("span.location")
#             # Lever
#             elif "lever.co" in domain:
#                 title = soup.select_one("h2.posting-headline") or soup.select_one("h1")
#                 location = soup.select_one("div.posting-categories > div") or soup.select_one("span.location")
#             # Ashby
#             elif "ashbyhq.com" in domain:
#                 title = soup.select_one("h1")  # Usually structured
#                 location = soup.find(string=re.compile("Location")).find_next("span") if soup.find(string=re.compile("Location")) else None
#             # Workable
#             elif "workable.com" in domain:
#                 title = soup.select_one("h1") or soup.select_one("div.job-header h2")
#                 location = soup.select_one("div.job-location") or soup.select_one("span.job-location")
#             else:
#                 # Fallback for general pages
#                 title = soup.find('h1') or soup.find('h2') or soup.find('title') or soup.find('meta', {'name': 'title'})
#                 location = soup.find("meta", {"name": "location"}) or soup.find("span", {"class": "location"})

#             return (title.get_text(strip=True) if title else "Unknown",
#                     location.get_text(strip=True) if location else "Unknown")

#         title, location = get_title_and_location()

#         location_match = any(keyword in text for keyword in app_states_keywords) or any(state in location.lower() for state in US_STATES)
#         if location_match:
#             location = "United States"

#         clearance_match = re.search(r"\b(secret clearance|security clearance|ts/sci|top secret|dod|public trust|requires clearance|requires.*?clearance|must have.*?clearance)\b", text)
#         travel_match = re.search(r"travel.*?(\d{1,3})\s?%", text)
#         closed_match = re.search(r"\b(job closed|no longer available|expired)", text)

#         travel_pct = int(travel_match.group(1)) if travel_match else 0
#         allowed_titles = get_keywords(profile)
#         title_match = any(k in title.lower() for k in allowed_titles)

#         rule_flags = {
#             "title_match": title_match,
#             "remote_us": location_match,
#             "no_clearance": not bool(clearance_match),
#             "travel_ok": travel_pct <= 25,
#             "job_open": not bool(closed_match),
#         }

#         logger.info(f"Scraping completed for URL: {url}. Title: {title}. Matching rules: {rule_flags}")

#         return {
#             "url": url,
#             "title": title if title != "Unknown" else "Title not found",
#             "location": location if location != "Unknown" else "Location not found",
#             "clearance": bool(clearance_match),
#             "travel": f"{travel_pct}%",
#             "rules": rule_flags,
#             "approve": all(rule_flags.values())
#         }

#     except Exception as e:
#         logger.error(f"Error occurred while scraping {url}: {str(e)}")
#         return {"url": url, "error": str(e)}


# @app.post("/check-jobs")
# async def check_jobs(data: LinkRequest, request: Request):
#     profile = request.query_params.get("profile", "web")
#     logger.info(f"Checking jobs for profile: {profile}")
#     tasks = [scrape_job(url, profile=profile) for url in data.links]
#     results = await asyncio.gather(*tasks)
#     logger.info(f"Job check completed. Results: {results}")
#     return {"results": results}
