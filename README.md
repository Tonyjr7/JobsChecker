This repository contains a FastAPI application designed to check job postings from given URLs and determine their suitability for specific profiles using various AI models. It scrapes job page content, sends it to a chosen AI service (Groq, Gemini, or DeepSeek), and processes the AI's response to provide structured job suitability results.

### Features

  * **Job Scraping**: Fetches HTML content from job listing URLs.
  * **AI-Powered Analysis**: Integrates with Groq, Gemini, and DeepSeek AI models to analyze job descriptions based on predefined criteria and user profiles.
  * **Profile Matching**: Utilizes keywords to match job titles/descriptions against specified professional profiles (e.g., DevOps, Web Developer, Data Scientist).
  * **Structured Output**: Provides job suitability results in a consistent JSON format, including details like position, remote status, US-based requirement, security clearance, travel, approval status, and a reason for approval/disapproval.
  * **Configurable API Keys**: Securely loads API keys for different AI services from environment variables.
  * **CORS Enabled**: Configured to handle Cross-Origin Resource Sharing, allowing requests from any origin.

### Installation

To set up and run the JobsChecker application, follow these steps:

#### Prerequisites

  * Python 3.8+
  * `pip` (Python package installer)

#### Clone the Repository

```bash
git clone https://github.com/Tonyjr7/JobsChecker.git
cd JobsChecker
```

#### Install Dependencies

Install all required Python packages using `pip`:

```bash
pip install -r requirements.txt
```

#### Configuration

Create a `.env` file in the root directory of the project to store your API keys. This file is ignored by Git for security reasons.

```
GROQ_API_KEY="your_groq_api_key"
GEMINI_API_KEY="your_gemini_api_key"
DEEPSEEK_API_KEY="your_deepseek_api_key"
```

Replace the placeholder values with your actual API keys.

### Usage

#### Running the Application

You can run the FastAPI application using Uvicorn:

```bash
uvicorn main:app --reload
```

The `--reload` flag is optional and useful for development, as it reloads the server automatically on code changes.

#### API Endpoints

The application exposes the following endpoints:

1.  **Home Page**

      * **GET `/`**
      * Returns a welcome message.
      * Example: `http://localhost:8000/`

2.  **Check Jobs**

      * **POST `/check-jobs`**
      * Analyzes a list of job links based on a specified profile and AI model.
      * **Request Body**:
        ```json
        {
          "links": ["url1", "url2", ...]
        }
        ```
      * **Query Parameters**:
          * `profile` (string, optional): The job profile to check against (e.g., "web", "devops", "data", "software engineer", "data scientist"). Defaults to "web" if not specified or unrecognized.
          * `ai` (string, required): The AI model to use for analysis. Must be one of "groq", "gemini", or "deepseek".
      * **Example Request (using `curl`)**:
        ```bash
        curl -X POST "http://localhost:8000/check-jobs?profile=devops&ai=groq" \
             -H "Content-Type: application/json" \
             -d '{"links": ["https://example.com/job1", "https://example.com/job2"]}'
        ```
      * **Example Response**:
        ```json
        {
          "results": [
            {
              "url": "https://example.com/job1",
              "response": {
                "position": "DevOps Engineer",
                "open": true,
                "remote": true,
                "us_based": true,
                "clearance": false,
                "travel": false,
                "approved": true,
                "reason": "Job title matches 'devops engineer'."
              }
            },
            {
              "url": "https://example.com/job2",
              "error": "Failed to process the job listing: An error occurred."
            }
          ]
        }
        ```

### Project Structure

```
JobsChecker/
├── background_tasks/
│   └── job_handler.py         # (Potentially) For background job processing
├── core/
│   └── fallback.py            # Commented-out alternative scraping logic
├── helper_function/
│   ├── parse_ai_response.py   # (Note: Appears unused in current main.py flow, AI responses are directly JSON parsed)
│   └── scrape_page.py         # HTML content scraping utility
├── services/
│   ├── deepseek_service.py    # Integration with DeepSeek AI
│   ├── gemini_service.py      # Integration with Gemini AI
│   └── groq_service.py        # Integration with Groq AI
├── utils/
│   ├── profile_keywords.py    # Defines keywords for job profiles
│   └── settings.py            # Loads application settings and API keys
├── .gitignore                 # Specifies files to be ignored by Git
├── main.py                    # Main FastAPI application entry point and API routes
└── requirements.txt           # List of Python dependencies
```

### How it Works (High-Level)

1.  **Request Reception**: The `main.py` file receives POST requests with a list of job URLs and specified `profile` and `ai` parameters.
2.  **Page Scraping**: For each URL, `helper_function/scrape_page.py` uses `requests` and `BeautifulSoup` to fetch and extract the plain text content from the job posting page.
3.  **AI Analysis**:
      * Based on the `ai` parameter, the application calls the corresponding service (`groq_service.py`, `gemini_service.py`, or `deepseek_service.py`).
      * Each AI service constructs a detailed prompt including system instructions, user instructions, and the scraped HTML content. The system instructions guide the AI to act as a "strict job analyzer" and to output results in a specific JSON format with predefined keys (position, open, remote, us\_based, clearance, travel, approved, reason).
      * The `profile_keywords.py` module is used to retrieve relevant job keywords for the given `profile`, which are then included in the AI prompt to guide the suitability check.
      * After receiving the AI's response, a post-processing step ensures that if any of the foundational job keywords appear in the AI's output, the `approved` status is forced to `true`.
4.  **Response Aggregation**: The AI's JSON response is parsed, and the results for each URL are compiled into a final JSON response.

### AI Model Integration

The application supports three AI models for job analysis:

  * **Groq**: Integrated via `services/groq_service.py`, using the `requests` library to interact with the Groq API.
  * **Gemini**: Integrated via `services/gemini_service.py`, using the `google.generativeai` library to interact with the Gemini API.
  * **DeepSeek**: Integrated via `services/deepseek_service.py`, using the `openai` library to interact with the OpenRouter API (which likely routes to DeepSeek internally).

All AI services are configured to use API keys loaded from environment variables via `utils/settings.py`.

### Job Suitability Logic

The AI models are instructed to determine job suitability based on several criteria, which are reflected in their JSON output:

  * **`position`**: The job title.
  * **`open`**: Whether the job is currently open and accepting applications.
  * **`remote`**: Whether the job is remote.
  * **`us_based`**: Whether the job is based in the US. If location is not mentioned, it's assumed acceptable.
  * **`clearance`**: Whether security clearance or background checks are required.
  * **`travel`**: An estimate of whether travel is required more than 25%.
  * **`approved`**: Whether the job is suitable for the specified profile. This is primarily determined by matching job titles or descriptions with foundational keywords for the profile. The AI's reason for approval/disapproval is also captured.
  * **`reason`**: A precise and very short explanation for the approval status.

The `helper_function/parse_ai_response.py` contains logic to parse a text-based AI response and determine a final `approve` status based on all these criteria (remote, US-based, no clearance, open, suitable). However, in `main.py`, the AI responses from Groq and DeepSeek are directly loaded as JSON, implying the AI models themselves are expected to return well-structured JSON. The `parse_groq_response` function might be a remnant or intended for a scenario where the AI does not return strict JSON initially.

### Dependencies

The project relies on a number of Python libraries, as listed in `requirements.txt`. Key dependencies include:

  * `fastapi`: For building the web API.
  * `uvicorn`: For serving the FastAPI application.
  * `requests`, `google-generativeai`, `openai`: For interacting with external AI services.
  * `beautifulsoup4`: For parsing HTML content.
  * `python-decouple`, `pydantic-settings`: For environment variable management.
  * `asyncio`: For asynchronous operations.
  * `pydantic`: For data validation.

### Further Development Notes

  * **`background_tasks/job_handler.py`**: This file appears to be an alternative implementation for handling job processing, possibly intended for background tasks, but it is not directly integrated into the `main.py` FastAPI routes.
  * **`core/fallback.py`**: This file is entirely commented out and seems to contain an older or alternative job scraping and analysis logic that did not rely on external AI services, using `playwright` and regex for direct content analysis.
