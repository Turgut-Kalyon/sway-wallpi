import os
from pathlib import Path
from textual.app import App
from textual.widgets import Footer, Header, ListView
from app.widgets.wallpaper_list import gen_ListView, get_wallpapers
from app.link.link_wp import new_link
from app.config.config_loader import PATH_DATA


class WallpiApp(App):
    ENABLE_COMMAND_PALETTE = False
    BINDINGS = [
        ("q", "quit", "Quit"),
        ("t", "toggle_dark_mode", "Toggle dark mode"),
    ]
    CSS = """
    Screen {
        layout: vertical;
    }

    ListView {
        height: 1fr;
    }
    """

    def compose(self):
        """What widgets is this app composed of?"""
        self.wallpapers = get_wallpapers()
        yield Header(show_clock=True)
        self.list_view = gen_ListView()
        yield self.list_view

        yield Footer()

    def action_toggle_dark_mode(self):
        self.theme = "textual-light" if self.theme == "textual-dark" else "textual-dark"

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        index = event.list_view.index
        if index is None:
            return
        src = self.wallpapers[index]
        target = Path(os.path.expanduser(PATH_DATA["target_dir"]))
        new_link(target, src)
