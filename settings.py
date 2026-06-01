from pathlib import Path

from PyQt6.QtCore import QStandardPaths


APP_NAME = "UniNews"

BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = BASE_DIR / "data"
FEEDS_FILE = DATA_DIR / "feeds.json"


def get_app_data_dir() -> Path:
    app_data_location = QStandardPaths.writableLocation(
        QStandardPaths.StandardLocation.AppLocalDataLocation
    )

    if app_data_location:
        app_data_dir = Path(app_data_location) / APP_NAME
    else:
        app_data_dir = Path.home() / ".uninews"

    app_data_dir.mkdir(parents=True, exist_ok=True)

    return app_data_dir


APP_DATA_DIR = get_app_data_dir()
DATABASE_PATH = APP_DATA_DIR / "uninews.db"