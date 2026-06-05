# UniNews

UniNews is a small desktop application that brings together news and announcements from universities into a single place.

The project started as a simple way to avoid visiting multiple university websites every day just to check for updates. Instead of opening several tabs, RSS feeds, and department pages, UniNews collects everything into one application and presents it in a clean interface.

The application is written in Python using PyQt6 and currently supports both RSS feeds and custom website scrapers. News articles are stored locally so that previously fetched content remains available even when a source is temporarily unavailable.

## Features

- Read news from multiple universities in one place
- Support for RSS feeds
- Support for custom HTML scrapers
- Local article caching using SQLite
- Search articles by keyword
- Filter articles by university
- Filter articles by specific source or department
- Light and dark themes
- Desktop notifications for new articles
- Configurable refresh intervals
- Local settings storage

## Project Structure

```text
UniNews/
├── scrapers/
├── ui/
├── data/
├── local_data/
├── app_settings.py
├── database.py
├── main.py
├── notifications.py
├── rss_service.py
├── scraper_service.py
├── settings.py
└── requirements.txt
```

## Installation

Clone the repository:

```bash
git clone https://github.com/open-source-uom/UniNews.git
cd UniNews
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it:

### Windows

```powershell
.venv\Scripts\activate
```

### Linux

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Running the Application

```bash
python main.py
```

## Adding a New RSS Feed

Open `data/feeds.json` and add a new entry:

```json
{
  "name": "MIT News",
  "type": "rss",
  "url": "https://news.mit.edu/rss/feed"
}
```

## Adding a New Scraper

Create a new file inside the `scrapers` folder.

Example:

```python
from scrapers.base_scraper import BaseScraper

class ExampleScraper(BaseScraper):

    def scrape(self):
        return []
```

Register it in `scraper_service.py`:

```python
SCRAPER_REGISTRY = {
    "example": ExampleScraper,
}
```

Then add it to `feeds.json`:

```json
{
  "name": "Example University",
  "type": "scraper",
  "scraper": "example"
}
```

## Data Storage

UniNews stores its local data inside:

```text
local_data/
```

This includes:

- Cached articles
- Application settings
- SQLite database

Deleting the database file will force the application to rebuild its cache the next time it runs.

## Development

Lint the code:

```bash
ruff check .
```

Automatically fix common issues:

```bash
ruff check . --fix
```

## Roadmap

Planned improvements include:

- More university sources
- Better image handling
- Pagination
- Source management from the UI
- Export and backup options
- Packaging for Linux distributions
- Automatic update checks

## Contributing

Contributions are welcome.

The easiest way to contribute is by adding support for additional universities through RSS feeds or custom scrapers.

Before opening a pull request:

1. Make sure the application runs correctly.
2. Run the linter.
3. Keep changes focused and easy to review.

## License

<<<<<<< HEAD
This project is released under the MIT License.
=======
This project is released under the GNU General Public License v3.0.
>>>>>>> d4366a7acaeea3b24f79877cde7e2b7fea51bfa7
