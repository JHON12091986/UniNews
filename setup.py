from setuptools import setup


setup(
    name="uninews",
    version="0.1.0",
    py_modules=[
        "app_settings",
        "database",
        "main",
        "notifications",
        "rss_service",
        "scraper_service",
        "settings",
    ],
    packages=[
        "ui",
        "scrapers",
    ],
    include_package_data=True,
    install_requires=[
        "PyQt6",
        "feedparser",
        "requests",
        "beautifulsoup4",
        "plyer",
    ],
    entry_points={
        "console_scripts": [
            "uninews=main:main",
        ],
    },
)