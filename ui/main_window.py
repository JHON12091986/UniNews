import json

from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtGui import QDesktopServices
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from database import Database
from settings import FEEDS_FILE
from rss_service import fetch_feed
from ui.settings_dialog import SettingsDialog
from app_settings import load_app_settings
from PyQt6.QtCore import QTimer
from notifications import should_notify, send_article_notification

ARTICLE_LINK_ROLE = 1000


class UniNewsWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("UniNews")
        self.resize(1050, 720)

        self.settings_button = QPushButton("Settings")
        self.settings_button.clicked.connect(self.open_settings)

        self.database = Database()
        self.articles = []

        self.app_settings = load_app_settings()
        self.setup_ui()
        self.apply_styles()
        self.load_cached_articles()

        if self.app_settings.get("refresh_on_startup", True):
            self.refresh_news()

        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_news)

        self.apply_theme()
        self.apply_refresh_timer()

        if self.app_settings.get("refresh_on_startup", True):
            self.refresh_news()

    def setup_ui(self):
        self.root = QWidget()
        self.root_layout = QVBoxLayout(self.root)
        self.root_layout.setContentsMargins(28, 24, 28, 24)
        self.root_layout.setSpacing(20)

        self.create_header()
        self.create_article_list()

        self.setCentralWidget(self.root)

    def create_header(self):
        header_card = QFrame()
        header_card.setObjectName("HeaderCard")

        header_layout = QHBoxLayout(header_card)
        header_layout.setContentsMargins(24, 20, 24, 20)
        header_layout.setSpacing(20)

        title_area = QVBoxLayout()
        title_area.setSpacing(4)

        self.title_label = QLabel("UniNews")
        self.title_label.setObjectName("TitleLabel")

        self.subtitle_label = QLabel("University news in one clean place")
        self.subtitle_label.setObjectName("SubtitleLabel")

        title_area.addWidget(self.title_label)
        title_area.addWidget(self.subtitle_label)

        self.refresh_button = QPushButton("Refresh news")
        self.refresh_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.refresh_button.setObjectName("RefreshButton")
        self.refresh_button.clicked.connect(self.refresh_news)

        self.settings_button = QPushButton("Settings")
        self.settings_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.settings_button.clicked.connect(self.open_settings)

        header_layout.addLayout(title_area)
        header_layout.addStretch()
        header_layout.addWidget(self.settings_button)
        header_layout.addWidget(self.refresh_button)

        self.root_layout.addWidget(header_card)

    def create_article_list(self):
        self.article_list = QListWidget()
        self.article_list.setObjectName("ArticleList")
        self.article_list.setSpacing(12)
        self.article_list.setVerticalScrollMode(QListWidget.ScrollMode.ScrollPerPixel)
        self.article_list.itemDoubleClicked.connect(self.open_article)

        self.root_layout.addWidget(self.article_list)

    def apply_styles(self):
        self.setStyleSheet(
            """
            QMainWindow {
                background-color: #F5F7FB;
            }

            #HeaderCard {
                background-color: white;
                border-radius: 18px;
                border: 1px solid #E5EAF3;
            }

            #TitleLabel {
                color: #1E293B;
                font-size: 32px;
                font-weight: 800;
            }

            #SubtitleLabel {
                color: #64748B;
                font-size: 14px;
            }

            #RefreshButton {
                background-color: #385963;
                color: white;
                border: none;
                padding: 11px 20px;
                border-radius: 10px;
                font-size: 14px;
                font-weight: 600;
            }

            #RefreshButton:hover {
                background-color: #2E4A52;
            }

            #RefreshButton:pressed {
                background-color: #22383F;
            }

            #RefreshButton:disabled {
                background-color: #94A3B8;
            }

            #ArticleList {
                background-color: transparent;
                border: none;
                outline: none;
            }

            #ArticleList::item {
                background-color: white;
                color: #1E293B;
                border: 1px solid #E5EAF3;
                border-radius: 16px;
                padding: 18px;
                margin: 2px;
            }

            #ArticleList::item:hover {
                background-color: #F8FAFC;
                border: 1px solid #CBD5E1;
            }

            #ArticleList::item:selected {
                background-color: #EAF2F4;
                border: 1px solid #385963;
                color: #1E293B;
            }

            QScrollBar:vertical {
                background: transparent;
                width: 10px;
                margin: 4px;
            }

            QScrollBar::handle:vertical {
                background: #CBD5E1;
                border-radius: 5px;
            }

            QScrollBar::handle:vertical:hover {
                background: #94A3B8;
            }

            QScrollBar::add-line:vertical,
            QScrollBar::sub-line:vertical {
                height: 0px;
            }
            """
        )

    def load_feeds(self) -> list[dict]:
        try:
            with open(FEEDS_FILE, "r", encoding="utf-8") as file:
                return json.load(file)
        except FileNotFoundError:
            QMessageBox.critical(
                self,
                "Missing feeds file",
                f"Could not find:\n{FEEDS_FILE}",
            )
            return []
        except json.JSONDecodeError as error:
            QMessageBox.critical(
                self,
                "Invalid feeds file",
                f"Your feeds.json file has invalid JSON:\n{error}",
            )
            return []

    def refresh_news(self):
        self.article_list.clear()

        self.refresh_button.setEnabled(False)
        self.refresh_button.setText("Refreshing...")

        feeds = self.load_feeds()

        old_links = {
            article.get("link")
            for article in self.database.get_articles(limit=5000)
        }

        new_articles_for_notification = []

        for feed in feeds:
            university_name = feed.get("name", "Unknown university")
            feed_url = feed.get("url", "")

            if not feed_url:
                continue

            try:
                articles = fetch_feed(university_name, feed_url)

                for article in articles:
                    if article.get("link") not in old_links:
                        new_articles_for_notification.append(article)

                self.database.save_articles(articles)

            except Exception as error:
                print(f"Could not fetch {university_name}: {error}")

        max_cached_articles = self.app_settings.get("max_cached_articles", 500)
        self.database.enforce_article_limit(max_cached_articles)

        self.articles = self.database.get_articles()
        self.render_articles()

        self.handle_notifications(new_articles_for_notification)

        self.refresh_button.setEnabled(True)
        self.refresh_button.setText("Refresh news")

    def load_cached_articles(self):
        self.articles = self.database.get_articles()
        self.render_articles()

    def open_article(self, item: QListWidgetItem):
        url = item.data(ARTICLE_LINK_ROLE)

        if url:
            QDesktopServices.openUrl(QUrl(url))

    def render_articles(self):
        self.article_list.clear()

        if not self.articles:
            empty_item = QListWidgetItem(
                "No articles found.\nCheck your RSS feeds or internet connection."
            )
            empty_item.setFlags(Qt.ItemFlag.NoItemFlags)
            self.article_list.addItem(empty_item)
            return

        for article in self.articles:
            title = article.get("title", "Untitled")
            university = article.get("university", "Unknown university")
            published = article.get("published", "Unknown date")
            summary = article.get("summary", "")

            clean_summary = self.clean_text(summary)

            if len(clean_summary) > 220:
                clean_summary = clean_summary[:220].strip() + "..."

            item_text = (
                f"{title}\n\n"
                f"{university}  •  {published}\n\n"
                f"{clean_summary}"
            )

            item = QListWidgetItem(item_text)
            item.setData(ARTICLE_LINK_ROLE, article.get("link", ""))
            item.setToolTip("Double-click to open article")

            self.article_list.addItem(item)

    def clean_text(self, text: str) -> str:
        clean = text.replace("\n", " ").replace("\r", " ").strip()
        return " ".join(clean.split())

    def open_settings(self):
        dialog = SettingsDialog(self)

        if dialog.exec():
            self.app_settings = load_app_settings()
            self.apply_theme()
            self.apply_refresh_timer()

            max_cached_articles = self.app_settings.get("max_cached_articles", 500)
            self.database.enforce_article_limit(max_cached_articles)

            self.articles = self.database.get_articles()
            self.render_articles()

            self.statusBar().showMessage("Settings saved.")

    def handle_notifications(self, new_articles: list[dict]) -> None:
        if not self.app_settings.get("notifications_enabled", False):
            return

        keywords = self.app_settings.get("notification_keywords", [])

        for article in new_articles:
            if should_notify(article, keywords):
                send_article_notification(article)

    def apply_refresh_timer(self) -> None:
        interval_minutes = self.app_settings.get("refresh_interval_minutes", 0)

        self.refresh_timer.stop()

        if interval_minutes and interval_minutes > 0:
            self.refresh_timer.start(interval_minutes * 60 * 1000)

    def apply_theme(self) -> None:
        theme = self.app_settings.get("theme", "light")

        if theme == "dark":
            self.setStyleSheet(
                """
                QMainWindow {
                    background-color: #0F172A;
                }

                #HeaderCard {
                    background-color: #1E293B;
                    border-radius: 18px;
                    border: 1px solid #334155;
                }

                #TitleLabel {
                    color: #F8FAFC;
                    font-size: 32px;
                    font-weight: 800;
                }

                #SubtitleLabel {
                    color: #CBD5E1;
                    font-size: 14px;
                }

                #RefreshButton {
                    background-color: #385963;
                    color: white;
                    border: none;
                    padding: 11px 20px;
                    border-radius: 10px;
                    font-size: 14px;
                    font-weight: 600;
                }

                #ArticleList {
                    background-color: transparent;
                    border: none;
                    outline: none;
                }

                #ArticleList::item {
                    background-color: #1E293B;
                    color: #F8FAFC;
                    border: 1px solid #334155;
                    border-radius: 16px;
                    padding: 18px;
                    margin: 2px;
                }

                #ArticleList::item:selected {
                    background-color: #334155;
                    border: 1px solid #385963;
                }
                """
            )
        else:
            self.apply_styles()

