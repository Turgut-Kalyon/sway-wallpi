"""Wallpi - Terminal-based wallpaper browser with live preview.

This module defines the main application `WallpiApp`, which displays a
list of available wallpapers, renders a live image preview in the
terminal, and symlinks selected wallpapers into a target directory.
"""

import os
from pathlib import Path
from textual import work
from textual.app import App
from textual.containers import Horizontal
from textual.widgets import Footer, Header, ListView, Label
from textual.timer import Timer
from textual_image.widget import Image
from app.widgets.wallpaper_list import gen_ListView, get_wallpapers
from app.core.link.link_wp import new_link
from app.core.config.config_loader import PATH_DATA


class WallpiApp(App):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._latest_requested_path: Path | None = None
        self._preview_timer: Timer | None = None

    ENABLE_COMMAND_PALETTE = False
    BINDINGS = [("q", "quit", "Quit")]
    CSS_PATH = "./styles/widgets.tcss"

    def compose(self):
        """Builds the app's widget layout.

        Creates the header, a horizontal layout containing the
        wallpaper list and the image preview, and the footer.

        Yields:
            Widget: The individual widgets that make up the app
            (Header, ListView, Image, Footer).
        """
        yield Header(id="header", show_clock=True)
        with Horizontal():
            self.wallpapers = get_wallpapers()
            self.list_view = gen_ListView()
            yield self.list_view
            yield Image(id="preview")
        yield Footer(id="footer")

    def on_mount(self) -> None:
        """Called after the app is mounted; sets initial UI values.

        Sets the title, subtitle (number of wallpapers found), and
        removes the default icon from the header.
        """
        self.title = "Wallpi"
        self.sub_title = f"{len(self.wallpapers)} wallpapers"
        self.query_one(Header).icon = ""

    def load_preview(self, image_path: Path) -> None:
        """Schedules a (debounced) load of a new image preview.

        Stops any currently running preview timer to avoid loading
        unnecessary images when quickly scrolling through the list
        (debouncing). After a short delay, `_trigger_preview_load` is
        called.

        Args:
            image_path: Path to the image file to load as a preview.
        """
        self._latest_requested_path = image_path
        if self._preview_timer is not None:
            self._preview_timer.stop()
        self._preview_timer = self.set_timer(
            0.05,
            lambda: self._trigger_preview_load(image_path),
        )

    def _trigger_preview_load(self, image_path: Path) -> None:
        """Starts the actual loading/resizing of a preview image.

        Aborts if a newer path has been requested in the meantime
        (prevents stale previews when navigating quickly). Computes
        the target size based on the current size of the preview
        widget.

        Args:
            image_path: Path to the image file to load.
        """
        if image_path != self._latest_requested_path:
            return
        preview_widget = self.query_one("#preview", Image)
        cell_width = preview_widget.size.width or 60
        cell_height = preview_widget.size.height or 30
        target_size = (cell_width * 10, cell_height * 20)
        self._load_and_resize(image_path, target_size)

    @work(thread=True)
    def _load_and_resize(self, image_path: Path, target_size: tuple[int, int]) -> None:
        """Loads an image on a background thread and resizes it.

        Runs as a Textual worker on a separate thread so that opening
        and resizing large images doesn't block the UI. Uses Pillow to
        proportionally shrink the image to fit within `target_size`
        (thumbnail), then hands the result back to the main thread.

        Args:
            image_path: Path to the image file to load.
            target_size: Desired maximum (width, height) in pixels.
                Falls back to 600x600 if either value is <= 0.
        """
        width, height = target_size
        if width <= 0 or height <= 0:
            # Fallback
            width, height = 600, 600
        from PIL import Image as PILImage

        pil_img = PILImage.open(image_path)
        pil_img.thumbnail((width, height))
        self.call_from_thread(self._set_preview_image, pil_img, image_path)

    def _set_preview_image(self, pil_img, image_path: Path | None = None) -> None:
        """Sets the loaded image on the preview widget (main thread).

        Called from `_load_and_resize` on the main thread. Ignores the
        result if a different path has since been requested, to avoid
        race conditions when the selection changes quickly.

        Args:
            pil_img: The already loaded and resized PIL image.
            image_path: Path this image was loaded for. Used to check
                against `_latest_requested_path`.
        """
        if image_path is not None and image_path != self._latest_requested_path:
            return
        self.query_one("#preview", Image).image = pil_img

    def on_list_view_highlighted(self, event: ListView.Highlighted) -> None:
        """Handles highlighting (hover/cursor) of a list entry.

        Determines the filename of the highlighted entry, builds the
        full wallpaper path from it, and triggers loading of the
        preview.

        Args:
            event: The `ListView.Highlighted` event containing the highlighted item.
        """
        if event.item is None:
            return
        filename = str(event.item.query_one(Label).content)
        image_path = Path(PATH_DATA["wallpaper_dir"]).expanduser() / filename
        self.load_preview(image_path)

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        """Handles selection (Enter) of a list entry.

        Determines the corresponding wallpaper from the list index and
        creates a symlink in the configured target directory.

        Args:
            event: The `ListView.Selected` event containing the selected index.
        """
        index = event.list_view.index
        if index is None:
            return
        src = self.wallpapers[index]
        target = Path(os.path.expanduser(PATH_DATA["target_dir"]))
        new_link(target, src)
