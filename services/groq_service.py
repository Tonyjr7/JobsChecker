# app/services/groq_service.py

import requests
import logging
import re
from utils.settings import settings

# Setup logging
logger = logging.getLogger(__name__)

# Your Groq API key
GROQ_API_KEY = settings.GROQ_API_KEY

devops = """solution architect devops engineer site reliablity engineer platform engineer infrastructure engineer cloud engineer automation engineer systems engineer ci/cd engineer operations engineer solutions architect automation engineer"""
web = """software engineer web developer frontend developer backend developer full stack developer software developer senior software engineer software engineer web application developer javascript developer python developer java developer react developer angular developer vue developer node.js developer ruby on rails developer php developer"""
data = """data scientist machine learning engineer ml engineer ai engineer data engineer research scientist applied scientist data analyst senior data scientist machine learning researcher deep learning engineer nlp engineer computer vision engineer ai researcher data science engineer mlops engineer ai/ml engineer quantitative analyst statistical analyst predictive modeler business intelligence engineer"""

# Profile to job titles mapping
PROFILE_JOBS = {
    "devops": devops,
    "web": web,
    "data": data,
    "software engineer": web,
    "web developer": web,
    "data scientist": data,
    "machine learning engineer": data
}

def process_with_groq(html: str, profile: str):
    # Get relevant job titles for the profile
    profile_lower = profile.lower()
    relevant_jobs = None
    for key in PROFILE_JOBS:
        if key in profile_lower:
            relevant_jobs = PROFILE_JOBS[key]
            break
    
    if not relevant_jobs:
        relevant_jobs = web  # default to web if no match found

    # Split foundational jobs into words for matching
    foundational_jobs_keywords = set(relevant_jobs.lower().split(","))
    
    # Setting up the conversation history with role and instructions
    conversation_history = [
        {
            "role": "system",
            "content": (
                "You are a strict job analyzer. You will answer only in a structured format. "
                "Your goal is to help determine if a job posting is suitable for a specific profile. "
                f"Consider these foundational job titles that work for this profile: {relevant_jobs}. If you encounter them a word from them it works."
                "Avoid deep interpretation — match job titles in a simple, obvious way.\n"
                "None ofyour business with specific education or experiences in job description"
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
                f"5. See if the job clearly fits the profile of a {profile}. This means job title or description should clearly say it's in {relevant_jobs} if you encounter a word from there in the job title it works— do not assume fit.\n\n"
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

    # Combine system prompt with user prompt
    final_system_prompt = "Avoid deep interpretation — match job titles in a simple, obvious way."
    messages = [{"role": "system", "content": final_system_prompt}] + conversation_history

    # Setup the request payload
    payload = {
        "model": "llama3-8b-8192",  # Or any other model
        "messages": messages,
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

# def parse_groq_response(text: str) -> dict:
#     """
#     Parses the Groq LLM response string into structured fields.
#     """
#     try:
#         data = {
#             "title": re.search(r"Job Title:\s*(.*?),\s*Open:", text).group(1).strip(),
#             "location": "Remote" if "Remote: True" in text else "On-site",
#             "clearance": "No" if "Clearance" not in text else "Yes",
#             "travel": "Minimal" if "Travel" not in text else "Unknown",
#             "approve": "Yes" if "Suitable: True" in text else "No",
#             "explanation": re.search(r"Reason:\s*(.*)", text).group(1).strip()
#         }
#         return data
#     except Exception as e:
#         return {
#             "title": "Unknown",
#             "location": "Unknown",
#             "clearance": "Unknown",
#             "travel": "Unknown",
#             "approve": "No",
#             "explanation": f"Failed to parse response: {str(e)}"
#         }


# print(process_with_groq("""Sinch
# Senior Backend Engineer, Mailgun Send - Sinch
# RemoteTechnology, Technology_R&D EmailFull time

# Atlanta, Georgia, United States
# Denver, Colorado, United States
# Chicago, Illinois, United States
# San Antonio, Texas, United States
# Overview
# Application
# Description
# The Sending Pipeline team at Sinch Email is responsible for a sophisticated and robust email delivery platform that delivers ~2.3 billion emails daily to people all around the globe. This team is responsible for all email ingestion, email storage, email processing, and email delivery. This includes product features centered around domain management, mailing lists, inbound email routing, email templates, email tracking, email bounces/complaints, etc. There are no dull moments on this team, as the services we own are what made Mailgun what it is today.

# With scalability and throughput at the forefront of priorities, the team is heavily focused on building, improving, and maintaining our microservices, supporting technologies, and architecture that as of today have handled up to 100,000 requests per second. We are constantly seeking innovative ways to ensure our customers are having the best experience with our product as possible.

# The ideal candidate thrives on uncovering and understanding the root causes of reliability and performance issues in robust production systems. They are passionate about documenting shortcomings and driving long-term improvements, whether that means rethinking architecture, building internal libraries, or designing new services to enhance system resilience and supportability. They enjoy building tools, such as HTTP APIs to CLIs and UIs, that empower engineers and support teams to operate systems confidently and at scale. This role is great for someone who loves doing more than just basic REST APIs, and who also loves exploring new technologies, evaluating their fit for our ecosystem, and crafting thoughtful plans to integrate them in ways that improve the reliability of both current and future systems.

# Responsibilities
# Be a part of the entire SDL: planning and analysis stage, design and prototyping stage, development, testing, integration and deployment, operations and maintenance. This spans new product work, tweaks to existing code, refactoring, performance enhancements, etc.
# Own and direct work during incidents. Investigate and diagnose difficult issues. Record the root cause and give recommendations on how to improve systems to avoid issues in the future.
# Be responsible for the reliability roadmap: Adopt a comprehensive and long-term perspective of the system. Drive and shape organizational practices that enhance operational efficiency and reliability. Handle the cycle of continuous improvement centered on availability and dependability.
# Stay up-to-date with industry trends and emerging technologies. Design and Implement a rollout plan for these new technologies. For example, planning and deploying Service-Mesh, Open Telemetry, Traffic Shaping, etc…
# Write documentation, map out flowcharts, and build diagrams for use in educating junior developers and onboarding.
# Aid our customers and help internal support reps by tackling incoming bugs, answering difficult questions, and offering assistance when needed.
# Requirements
# 7+years of experience paired with an in-depth understanding of Golang, Python, or any similar language
# Experience building and running highly scalable distributed systems
# Experience with modern-day cloud technologies and deployment strategies, such as AWS, GCP, Nomad, Docker, Domain Driven Micro Service architecture, CI/CD, and canary deployments.
# In-depth familiarity with monitoring production code within robust distributed systems
# Proven knowledge of NoSQL databases such as MongoDB or Cassandra
# Proven record of mentoring mid-level software engineers in order to build a strong team that is aligned with values
# Analytical mind with a passion for problem-solving in a sophisticated system
# Excellent communication paired with the ability to empower and lead through initiatives
# We're looking for someone who takes ownership of their work, follows through on commitments, and values accountability.
# Preferred
# Experience with Golang
# Understanding of observability principles and experience with OpenTelemetry
# Our Hiring Process 
# We are committed to ensuring a recruitment process that is fair, objective, consistent, and inclusive. Our approach includes structured, competency-based interviews designed to evaluate your skills, experience, and qualifications relevant to the role. At times, we may include a data-driven assessment to enhance our hiring success and identify candidates likely to excel.  

# We believe in a two-way process and encourage you to ask questions throughout the journey.  If this role isn't what you're looking for, please explore the other opportunities listed on our career page: . No matter who you are, we hope you find an exciting path forward - hopefully with us! 

# Benefits
# STAY HEALTHY: We offer comprehensive market competitive medical, dental, and vision plans. A variety of supplemental plans are also provided to meet your individual needs including access to telehealth for all participants. 
# CARE FOR YOURSELF: Take advantage of our free virtual counseling resources through our global Employee Assistance Program. Your mental health is as important as your physical health. 
# SECURE YOUR FUTURE: Plan for your future with our Roth and Pre-tax 401(k) options including an employer match for all participants. 
# TAKE A BREAK: Enjoy a generous paid time off program. We value balance and understand that performance at work requires time to rest at home and/or rejuvenate on vacation. 
# PUT FAMILY FIRST: We know that families can be built in a variety of ways; therefore, we offer paid parental leave and family planning support. 
# WORK WHEREVER: Our flexible remote work offerings allow you to work wherever you are the most productive and successful. It is what you do, not where you work, that matters. 
# MAKE AN IMPACT: Support betterment in your community and beyond by taking paid time off to support a volunteer program of your choice. 
 

# We're proud to be an equal opportunity employer, and all qualified applicants will be considered to join our team regardless of race, color, religion, creed, gender, national origin, age, disability, veteran status, marital status, pregnancy, sex, gender expression or identity, sexual orientation, citizenship, or any other legally protected class. 

# The annual starting salary for this position is $152,768.00 - $180,960.00. Factors which may affect starting pay within this range may include geography/market, skills, education, experience, and other qualifications. This role will be accepting applications until 4/07/25 at a minimum. Please note that the application timeline may be flexible to accommodate a comprehensive candidate evaluation.

# Sinch collects and processes personal data in accordance with applicable data protection laws.If you are a European Job Applicant see the privacy notice for further details.
# Sinch does not discriminate on the basis of race, sex, color, religion, age, national origin, marital status, disability, veteran status, genetic information, sexual orientation, gender identity or any other reason prohibited by law in provision of employment opportunities and benefits.
# View website
# View all jobs
# Help
# Accessibility
# Powered byWorkable""", "Software Engineer & Web Development"))
