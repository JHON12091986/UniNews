from datetime import datetime, timezone

import feedparser


def extract_image_url(entry) -> str:
    if "media_content" in entry and entry.media_content:
        return entry.media_content[0].get("url", "")

    if "media_thumbnail" in entry and entry.media_thumbnail:
        return entry.media_thumbnail[0].get("url", "")

    if "links" in entry:
        for link in entry.links:
            if link.get("type", "").startswith("image/"):
                return link.get("href", "")

    return ""


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
                "image_url": extract_image_url(entry),
            }
        )

    return articles