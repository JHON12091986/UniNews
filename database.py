import sqlite3
from pathlib import Path
from typing import Optional

import settings


class Database:
    def __init__(self, database_path: Path | None = None):
        if database_path is None:
            database_path = settings.DATABASE_PATH

        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)

        self.connection = sqlite3.connect(self.database_path)
        self.connection.row_factory = sqlite3.Row

        self.create_tables()

    def create_tables(self) -> None:
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS articles
            (
                id
                INTEGER
                PRIMARY
                KEY
                AUTOINCREMENT,
                university
                TEXT
                NOT
                NULL,
                title
                TEXT
                NOT
                NULL,
                summary
                TEXT,
                link
                TEXT
                NOT
                NULL
                UNIQUE,
                published
                TEXT,
                fetched_at
                TEXT
                NOT
                NULL,
                image_url
                TEXT
            );
            """
        )
        self.connection.commit()

        try:
            self.connection.execute("ALTER TABLE articles ADD COLUMN image_url TEXT;")
            self.connection.commit()
        except sqlite3.OperationalError:
            pass

        try:
            self.connection.execute("ALTER TABLE articles ADD COLUMN source TEXT;")
            self.connection.commit()
        except sqlite3.OperationalError:
            pass

    def save_article(self, article: dict) -> None:
        query = """
                INSERT \
                OR IGNORE INTO articles (
            university,
            source,
            title,
            summary,
            link,
            published,
            fetched_at,
            image_url
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?); \
                """

        self.connection.execute(
            query,
            (
                article.get("university", "Unknown university"),
                article.get("source", article.get("university", "Unknown source")),
                article.get("title", "Untitled"),
                article.get("summary", ""),
                article.get("link", ""),
                article.get("published", "Unknown date"),
                article.get("fetched_at", ""),
                article.get("image_url", ""),
            ),
        )

        self.connection.commit()

    def save_articles(self, articles: list[dict]) -> None:
        for article in articles:
            self.save_article(article)

    def get_articles(
            self,
            university=None,
            source=None,
            search_text=None,
            limit: int = 500,
    ) -> list[dict]:
        query = """
                SELECT
                    id,
                    university,
                    source,
                    title,
                    summary,
                    link,
                    published,
                    fetched_at,
                    image_url
                FROM articles
                WHERE 1 = 1 \
                """

        params = []

        if university and university != "All":
            query += " AND university = ?"
            params.append(university)

        if source and source != "All":
            query += " AND source = ?"
            params.append(source)

        if university and university != "All":
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

    def load_cached_articles(self):
        try:
            self.articles = self.database.get_articles()
        except Exception as error:
            print(f"Could not load cached articles: {error}")
            self.articles = []
            self.selected_university = "All"
            self.search_text = ""

        self.render_articles()

    def get_universities(self) -> list[str]:
        query = """
                SELECT DISTINCT university
                FROM articles
                ORDER BY university ASC; 
                """

        cursor = self.connection.execute(query)
        rows = cursor.fetchall()

        return [row["university"] for row in rows]

    def get_sources_for_university(self, university: str) -> list[str]:
        cursor = self.connection.execute(
            """
            SELECT DISTINCT source
            FROM articles
            WHERE university = ?
            ORDER BY source ASC;
            """,
            (university,),
        )

        return [row["source"] for row in cursor.fetchall() if row["source"]]