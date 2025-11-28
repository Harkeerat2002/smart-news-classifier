# Nexthink Newsfeed API

This is a real-time news aggregation system that fetches IT-related news from the RSS feeds of 3 sources. This uses an LLM (OpenAI) to classify them into specific categories, and then a search API is provided through FastAPI to query the stored articles.

## Features

- **Automated Ingestion:** Fetches news from _Reddit (r/technology)_, _Ars Technica_, and _Tom's Hardware_.
- **AI Classification:** Uses **GPT-3.5-turbo** to categorize articles into the following 6 categories:
  - Cybersecurity
  - Software Development
  - Hardware
  - Networking
  - Cloud Computing
  - General IT News
- **Resilient Architecture:** Includes a "Mock Mode" fallback. If no OpenAI API key is provided, the system automatically switches to a keyword-based classifier, ensuring the application never crashes during review.
- **Duplicate Protection:** Prevents the same article from being saved twice using URL uniqueness.
- **REST API:** Fully documented API built with FastAPI.

## Demo


https://github.com/user-attachments/assets/cef97259-1113-4fc8-93de-02eb275b4025



## Setup Instructions

### Running

1. **Clone the Repository:**
   ```bash
    git clone https://github.com/Harkeerat2002/smart-news-classifier
    cd smart-news-classifier
   ```
2. **Create a Virtual Environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Set OpenAI API Key:**
   If you have an OpenAI API key, set it as an environment variable to enable AI classification. Duplicate .env.example to .env and add your key.:
   ```bash
   export OPENAI_API_KEY="your_openai_api_key_here"
   ```
5. **Run the Application:**
   ```bash
   uvicorn app.main:app --reload
   ```
6. The API will start at http://127.0.0.1:8000/docs.

### Testing

1. **Run Tests:**
   ```bash
   pytest
   ```


## Documentation
1. `app/main.py` (The API Controller)

    **Purpose:** This triggers the main application flow. It initializes the FastAPI server, defines URL routes, and orchestrates the flow of data between the other modules.

    - `lifespan(app)`: Manages the server startup/shutdown lifecycle. It automatically initializes the database tables when the server boots up.
    - `trigger_ingestion(background_tasks)`: Endpoint (POST /ingest). It initiates the news fetching process in a background thread, allowing the API to return an immediate "Accepted" response to the user without waiting for the slow fetching process.
    - `run_ingestion_task()`: The worker function that coordinates the ETL pipeline: Fetch -> Classify -> Save.
    - `search_news(q, category)`: Endpoint (GET /search). Connects the user's query parameters to the database search logic.

2. `app/ingestion.py` (The Data Fetcher)

    **Purpose:** Handles the connection to external world. It abstracts away the complexity of parsing different RSS XML formats into a standardized dictionary.

    - `fetch_all_news()`: Iterates through the configured source list. It handles network errors and feedparser exceptions (like "bozo" bits for bad XML) to ensure one bad feed doesn't crash the whole pipeline. Source List:
        - Reddit r/technology RSS
        - Ars Technica RSS
        - Tom's Hardware RSS
    - `parse_date(entry)`: A utility function to normalize date formats, as Reddit and news sites often use different timestamp standards.

3. `app/classifier.py` (The Intelligence Layer)

    **Purpose:** Determines the category of a news article. This module implements the "Strategy Pattern" to switch between Real AI and Mock Logic.

    - `__init__`: Checks for the existence of OPENAI_API_KEY. If found, it initializes the OpenAI client. If not, it logs a warning and enables "Mock Mode".

    - `classify(text)`:

        - **Strategy A (Real)**: Sends a system prompt to GPT-3.5-turbo instructing it to categorize the text into one of 6 strict categories.

        - **Strategy B (Mock)**: Uses deterministic keyword matching (e.g., "malware" -> "Cybersecurity"). This ensures the application is testable and runnable by reviewers without requiring an API key.

4. `app/database.py` (The Persistence Layer)

    **Purpose:** A wrapper around the SQLite database. It handles all SQL execution, ensuring no SQL code leaks into the API layer.

    - `init_db()`: Idempotent function that creates the articles table only if it doesn't exist.

    - `save_article(article)`: Inserts a new record. Crucially, it catches sqlite3.IntegrityError to detect and ignore duplicate URLs, enforcing data uniqueness.

    - `search_articles(query, category)`: Dynamically builds a SQL query string based on provided filters. It uses SQL LIKE operators for text matching.

5. `app/models.py` (The Data Schemas)
    
    **Purpose:** Defines the data contracts (DTOs) using Pydantic. This ensures strict data validation for inputs and outputs.

    - `ArticleDTO`: Defines exactly what an article looks like in the JSON response (hides internal DB fields if necessary).
    - `SearchResponse`: Standardizes the API response format to include metadata (like count) alongside results.

## Future Improvements
- **Logging**: Current logging is done via print statements, which makes it difficult to debug in production. Better logging techniques can be implemented. 
- **Better Resilience**: Implement either more keywords or a small local ML model for the mock classifier to improve accuracy when OpenAI is not available.
- **Dockerization**: Containerize the application for easier deployment.
