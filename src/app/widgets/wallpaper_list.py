from app.core.config.config_loader import PATH_DATA
from app.widgets.vim_list_view import VimListView
from textual.widgets import ListItem, Label
import os
from pathlib import Path

WALLPAPER_DIR = Path(os.path.expanduser(PATH_DATA["wallpaper_dir"]))
EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def get_wallpapers():
    return sorted(p for p in WALLPAPER_DIR.iterdir() if p.suffix.lower() in EXTENSIONS)


def gen_ListView():
    wallpapers = get_wallpapers()
    return VimListView(
        *[ListItem(Label(path.name)) for path in wallpapers], id="file-list"
    )
