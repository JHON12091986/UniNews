from notifications import should_notify, send_article_notification

article = {
    "university": "Wageningen University",
    "title": "New Scholarship Deadline Announced",
    "summary": "Applications close on June 15."
}

keywords = ["scholarship", "deadline"]

print("Should notify:", should_notify(article, keywords))

send_article_notification(article)

print("Notification sent.")