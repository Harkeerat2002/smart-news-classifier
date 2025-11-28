import sqlite3
from typing import List, Dict, Optional

DB_NAME = "news.db"


def get_db_connection():
    """Establishes a connection to the SQLite database."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # Access columns by name (row['title'])
    return conn


def init_db():
    """
    Creates the necessary tables if they don't exist.
    Structure of the Table:
    - id: Auto-incremented primary key
    - title: Title of the article
    - summary: Short summary of the article
    - url: URL of the article (Unique)
    - source: Source of the article
    - category: Classified category
    - published_at: Publication date
    - created_at: Timestamp when added to DB
    """
    conn = get_db_connection()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                summary TEXT,
                url TEXT UNIQUE,
                source TEXT,
                category TEXT,
                published_at TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )
        conn.commit()
    except Exception as e:
        conn.close()
        raise e


def save_article(article: Dict) -> bool:
    """
    Saves an article to the DB. Returns True if saved, False if it was a duplicate.
    """
    conn = get_db_connection()
    try:
        conn.execute(
            """
            INSERT INTO articles (title, summary, url, source, category, published_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                article["title"],
                article["summary"],
                article["url"],
                article["source"],
                article["category"],
                article["published_at"],
            ),
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        # This error happens if the URL already exists (duplicate news)
        return False
    except Exception as e:
        conn.close()
        raise e


def search_articles(
    query: Optional[str] = None, category: Optional[str] = None
) -> List[Dict]:
    """
    Searches for articles based on a text query and/or category.
    Requirements: Search by user prompt and category.
    """
    conn = get_db_connection()
    cursor = conn.cursor()

    # Base SQL query
    sql = "SELECT * FROM articles WHERE 1=1"
    params = []

    # Add text search condition (checks title OR summary)
    if query:
        sql += " AND (title LIKE ? OR summary LIKE ?)"
        wildcard_query = f"%{query}%"
        params.extend([wildcard_query, wildcard_query])

    # Add category filter condition
    if category:
        sql += " AND category = ?"
        params.append(category)

    # Order by newest first
    sql += " ORDER BY published_at DESC LIMIT 50"

    cursor.execute(sql, params)
    rows = cursor.fetchall()
    conn.close()

    # Convert rows to a list of dicts for the API
    return [dict(row) for row in rows]


def get_article_by_id(article_id: int) -> Optional[Dict]:
    """Retrieves a specific article by its ID."""
    conn = get_db_connection()
    row = conn.execute("SELECT * FROM articles WHERE id = ?", (article_id,)).fetchone()
    conn.close()
    if row:
        return dict(row)
    return None


# --- Test Block ---
if __name__ == "__main__":
    # 1. Initialize DB
    init_db()

    # 2. Mock Data
    mock_article = {
        "title": "Test Article: Python is great",
        "summary": "A short summary about Python.",
        "url": "http://example.com/python-news",
        "source": "Test Source",
        "category": "Software & Development",
        "published_at": "2023-10-27T10:00:00",
    }

    # 3. Save
    if save_article(mock_article):
        print("Article saved!")
    else:
        print("Article already exists (Duplicate skipped).")

    # 4. Search
    results = search_articles(query="Python", category="Software & Development")
    print(f"\nFound {len(results)} articles matching 'Python':")
    for r in results:
        print(f"- {r['title']} (ID: {r['id']})")
