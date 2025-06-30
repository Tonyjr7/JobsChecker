# app/services/gemini_service.py

import logging
import google.generativeai as genai
from utils.settings import settings
from utils.profile_keywords import match

# Setup logging
logger = logging.getLogger(__name__)

# Configure Gemini API key
genai.configure(api_key=settings.GEMINI_API_KEY)

def process_with_gemini(html: str, profile: str):
    foundational_jobs_keywords = match.profile_match(profile)

    prompt = (
        "You are a strict job analyzer. You will answer only in a structured format. "
        "Your goal is to help determine if a job posting is suitable for a specific profile. "
        f"Consider these foundational job titles that work for this profile: {foundational_jobs_keywords}. "
        "If you encounter a word from them it works. Avoid deep interpretation — match job titles in a simple, obvious way. "
        "None of your business with specific education or experiences in job description. Always state why you approve.\n\n"
        "Always state why you approve\n"
        "Your reponse should be in **very strict well structured JSON format**, this should be consistent"
        "With default keys: position, open, remote, us_based, clearance, travel, approved, reason - these key should never change\n"
        f"Instructions:\n"
        f"1. Check if the job is currently open and accepting applications.\n"
        f"2. Check if it's remote or based in the US. If location is not mentioned, assume it is acceptable.\n"
        f"3. Identify if it requires security clearance or background checks.\n"
        f"4. Estimate if travel is required more than 25%.\n"
        f"5. See if the job clearly fits the profile of a {profile}. This means job title or description should clearly say it's in {foundational_jobs_keywords} — do not assume fit.\n\n"
        f"Respond **only** in the your default format\n"
        f"Do not include anything else.\n\n"
        f"HTML content:\n{html}"
    )

    try:
        model = genai.GenerativeModel("gemini-1.5-pro-latest")
        response = model.generate_content(prompt)

        if response and response.text:
            result_text = response.text.strip()

            for word in foundational_jobs_keywords:
                if word.lower() in result_text.lower():
                    result_text = result_text.replace("Suitable: false", "Suitable: true")

            logger.info("Gemini processing completed successfully.")
            return result_text
        else:
            logger.error("Empty response from Gemini model.")
            return {"error": "No content returned from Gemini model."}

    except Exception as e:
        logger.error(f"Error occurred while processing with Gemini: {str(e)}")
        return {"error": f"Exception occurred: {str(e)}"}
