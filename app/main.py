from fastapi import FastAPI, HTTPException, Query, BackgroundTasks, logger
from contextlib import asynccontextmanager
from typing import Optional, List

from app.models import ArticleDTO, SearchResponse, IngestResponse
from app.ingestion import fetch_all_news
from app.classifier import NewsClassifier
from app.database import init_db, save_article, search_articles, get_article_by_id

# Initialize Classifier (Global instance to avoid reloading models/connections)
classifier = NewsClassifier()


# --- Lifespan Manager (Startup/Shutdown logic) ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Ensure DB exists
    print("Server starting up. Initializing database...")
    init_db()
    yield
    # Shutdown: (Cleanup if needed)
    print("Server shutting down.")


# Initialize FastAPI app
app = FastAPI(
    title="Nexthink Newsfeed API",
    description="API for aggregating, classifying, and searching IT news.",
    version="1.0.0",
    lifespan=lifespan,
)


# --- Helper Function for Background Task ---
def run_ingestion_task():
    """
    Fetches news, classifies them, and saves to DB.
    We run this in the background so the API doesn't hang while fetching.
    """
    print("Starting background ingestion task...")
    raw_articles = fetch_all_news()
    new_count = 0

    for article in raw_articles:
        # 1. Classify
        # (Pass title + summary for better context)
        text_to_classify = f"{article['title']} {article['summary']}"
        category = classifier.classify(text_to_classify)
        article["category"] = category

        # 2. Save
        saved = save_article(article)
        if saved:
            new_count += 1

    print(f"Ingestion complete. Saved {new_count} new articles.")


# --- Endpoints ---


@app.get("/health")
def health_check():
    """Simple health check endpoint."""
    return {"status": "ok", "database": "connected"}


@app.post("/ingest", response_model=IngestResponse)
def trigger_ingestion(background_tasks: BackgroundTasks):
    """
    Manually triggers the news fetcher.
    Uses BackgroundTasks so the user gets an immediate response.
    """
    background_tasks.add_task(run_ingestion_task)
    return {
        "status": "accepted",
        "message": "Ingestion started in background.",
        "articles_processed": 0,  # This is async, so we return 0 immediately
    }


@app.get("/search", response_model=SearchResponse)
def search_news(
    q: Optional[str] = Query(None, description="Search text in title or summary"),
    category: Optional[str] = Query(None, description="Filter by exact category"),
):
    """
    Search for news articles based on user prompt and/or category.
    """
    results = search_articles(query=q, category=category)
    return {"count": len(results), "results": results}


@app.get("/articles/{article_id}", response_model=ArticleDTO)
def get_article(article_id: int):
    """
    Retrieve a specific article by ID.
    """
    article = get_article_by_id(article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
    return article
