from plyer import notification


def should_notify(article: dict, keywords: list[str]) -> bool:
    if not keywords:
        return True

    text = (
        article.get("title", "") + " " + article.get("summary", "")
    ).lower()

    return any(keyword.lower() in text for keyword in keywords)


def send_article_notification(article: dict) -> None:
    title = article.get("university", "UniNews")
    message = article.get("title", "New article")

    notification.notify(
        title=f"New article from {title}",
        message=message[:200],
        app_name="UniNews",
        timeout=8,
    )