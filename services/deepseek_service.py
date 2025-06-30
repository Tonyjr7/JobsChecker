import logging
from openai import OpenAI

from utils.settings import settings
from utils.profile_keywords import match

# Setup logging
logger = logging.getLogger(__name__)

# setting up DeepSeek
client = OpenAI(api_key=settings.DEEPSEEK_API_KEY, base_url="https://openrouter.ai/api/v1")

def process_with_deepseek(html: str, profile: str):
    foundational_jobs_keywords = match.profile_match(profile)

    response = client.chat.completions.create(
        model="mistralai/mistral-small-3.2-24b-instruct",
        messages=[
            {
                "role": "system", 
                "content": (
                    "You are a strict job analyzer. You will answer only in a structured format. "
                    "Your goal is to help determine if a job posting is suitable for a specific profile. "
                    f"Consider these foundational job titles that work for this profile: {foundational_jobs_keywords}. If you encounter them a word from them it works."
                    "Avoid deep interpretation — match job titles in a simple, obvious way.\n"
                    "None ofyour business with specific education or experiences in job description"
                    "Always state why you approve\n"
                    "With default keys: position, open, remote, us_based, clearance, travel, approved, reason - these key should never change"
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
                    f"5. See if the job clearly fits the profile of a {profile}. This means job title or description should clearly say it's in {foundational_jobs_keywords} if you encounter a word from there in the job title it works— do not assume fit. Just a simple reason\n\n"
                    f"Respond **only** in the your default format"
                    f"Do not include anything else.\n"
                )
            },
            {
                "role": "user",
                "content": f"HTML content:\n{html}"
            }
        ],
        stream=False
    )

    return response.choices[0].message.content