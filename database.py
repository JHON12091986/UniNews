import sqlite3
from pathlib import Path
from typing import Optional

from settings import DATABASE_PATH


class Database:
    def __init__(self, database_path: Path = DATABASE_PATH):
        self.database_path = database_path
        self.connection = sqlite3.connect(self.database_path)
        self.connection.row_factory = sqlite3.Row
        self.create_tables()

    def create_tables(self) -> None:
        query = """
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            university TEXT NOT NULL,
            title TEXT NOT NULL,
            summary TEXT,
            link TEXT NOT NULL UNIQUE,
            published TEXT,
            fetched_at TEXT NOT NULL
        );
        """

        self.connection.execute(query)
        self.connection.commit()

    def save_article(self, article: dict) -> None:
        query = """
        INSERT OR IGNORE INTO articles (
            university,
            title,
            summary,
            link,
            published,
            fetched_at
        )
        VALUES (?, ?, ?, ?, ?, ?);
        """

        self.connection.execute(
            query,
            (
                article.get("university", "Unknown university"),
                article.get("title", "Untitled"),
                article.get("summary", ""),
                article.get("link", ""),
                article.get("published", "Unknown date"),
                article.get("fetched_at", ""),
            ),
        )

        self.connection.commit()

    def save_articles(self, articles: list[dict]) -> None:
        for article in articles:
            self.save_article(article)

    def get_articles(
        self,
        university: Optional[str] = None,
        search_text: Optional[str] = None,
        limit: int = 200,
    ) -> list[dict]:
        query = """
        SELECT
            id,
            university,
            title,
            summary,
            link,
            published,
            fetched_at
        FROM articles
        WHERE 1 = 1
        """

        params = []

        if university and university != "All Universities":
            query += " AND university = ?"
            params.append(university)

        if search_text:
            query += """
            AND (
                title LIKE ?
                OR summary LIKE ?
                OR university LIKE ?
            )
            """

            search_pattern = f"%{search_text}%"
            params.extend([search_pattern, search_pattern, search_pattern])

        query += """
        ORDER BY id DESC
        LIMIT ?
        """

        params.append(limit)

        cursor = self.connection.execute(query, params)
        rows = cursor.fetchall()

        return [dict(row) for row in rows]

    def delete_all_articles(self) -> None:
        self.connection.execute("DELETE FROM articles;")
        self.connection.commit()

    def close(self) -> None:
        self.connection.close()

    def enforce_article_limit(self, max_articles: int) -> None:
        query = """
                DELETE \
                FROM articles
                WHERE id NOT IN (SELECT id \
                                 FROM articles \
                                 ORDER BY id DESC
                    LIMIT ?
                    ); \
                """

        self.connection.execute(query, (max_articles,))
        self.connection.commit()