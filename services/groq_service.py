# app/services/groq_service.py

import requests
import logging
import re
from utils.settings import settings
from utils.profile_keywords import match

# Setup logging
logger = logging.getLogger(__name__)

# Your Groq API key
GROQ_API_KEY = settings.GROQ_API_KEY

def process_with_groq(html: str, profile: str):
    foundational_jobs_keywords = match.profile_match(profile)
    
    # Setting up the conversation history with role and instructions
    conversation_history = [
        {
            "role": "system",
            "content": (
                "You are a strict job analyzer. You will answer only in a structured format. "
                "Your goal is to help determine if a job posting is suitable for a specific profile. "
                f"Consider these foundational job titles that work for this profile: {foundational_jobs_keywords}. If you encounter them a word from them it works."
                "Avoid deep interpretation — match job titles in a simple, obvious way.\n"
                "None ofyour business with specific education or experiences in job description"
                "Always state why you approve"
            )
        },
        {
            "role": "user",
            "content": (
                f"Instructions:\n"
                f"1. Check if the job is currently open and accepting applications.\n"
                f"2. Check if it's remote or based in the US. If location is not mentioned, assume it is acceptable.\n"
                f"3. Identify if it requires security clearance or background checks.\n"
                f"4. Estimate if travel is required more than 25%.\n"
                f"5. See if the job clearly fits the profile of a {profile}. This means job title or description should clearly say it's in {foundational_jobs_keywords} if you encounter a word from there in the job title it works— do not assume fit.\n\n"
                f"Respond **only** in the following format:\n"
                f"Job Title: [Insert Title], Open: [true/false], Remote: [true/false], US-Based: [true/false], Clearance: [true/false], Travel: [true/false], Suitable: [true/false], Reason: [short reason if not suitable - this is important]\n\n"
                f"Do not include anything else."
            )
        },
        {
            "role": "user",
            "content": f"HTML content:\n{html}"
        }
    ]

    # # Combine system prompt with user prompt
    # final_system_prompt = "Avoid deep interpretation — match job titles in a simple, obvious way."
    # messages = [{"role": "system", "content": final_system_prompt}] + conversation_history

    # Setup the request payload
    payload = {
        "model": "llama3-8b-8192",  # Or any other model
        "messages": conversation_history,
        "temperature": 0.7
    }

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    try:
        # Send the request to Groq's API
        response = requests.post("https://api.groq.com/openai/v1/chat/completions", json=payload, headers=headers)

        if response.status_code == 200:
            groq_result = response.json()["choices"][0]["message"]["content"].strip()
            logger.info("Groq processing completed successfully.")

            # If foundational job title words exist in job title, force the AI to mark it as suitable
            for word in foundational_jobs_keywords:
                if word in groq_result.lower():
                    groq_result = groq_result.replace("Suitable: false", "Suitable: true")

            return groq_result
        else:
            logger.error(f"Groq API request failed with status code {response.status_code}")
            return {"error": f"Failed to communicate with Groq API. Status code: {response.status_code}"}
    
    except Exception as e:
        logger.error(f"Error occurred while processing with Groq: {str(e)}")
        return {"error": f"Exception occurred: {str(e)}"}