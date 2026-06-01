from datetime import datetime, timezone

import feedparser


def fetch_feed(university_name: str, feed_url: str) -> list[dict]:
    parsed_feed = feedparser.parse(feed_url)

    fetched_at = datetime.now(timezone.utc).isoformat()
    articles = []

    for entry in parsed_feed.entries:
        link = entry.get("link", "")

        if not link:
            continue

        articles.append(
            {
                "university": university_name,
                "title": entry.get("title", "Untitled"),
                "summary": entry.get("summary", ""),
                "link": link,
                "published": entry.get("published", "Unknown date"),
                "fetched_at": fetched_at,
            }
        )

    return articles