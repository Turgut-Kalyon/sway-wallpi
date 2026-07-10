import os
from pathlib import Path
from PIL import Image as PILImage
from textual import work
from textual.app import App
from textual.containers import Horizontal
from textual.widgets import Footer, Header, ListView, Label
from textual.timer import Timer
from textual_image.widget import Image
from app.widgets.wallpaper_list import gen_ListView, get_wallpapers
from app.link.link_wp import new_link
from app.config.config_loader import PATH_DATA

# TODO write more docstrings
class WallpiApp(App):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._latest_requested_path: Path | None = None
        self._preview_timer: Timer | None = None

    ENABLE_COMMAND_PALETTE = False
    BINDINGS = [("q", "quit", "Quit")]
    CSS_PATH = "./styles/widgets.tcss"

    def compose(self):
        """What widgets is this app composed of?"""

        yield Header(id="header", show_clock=True)
        with Horizontal():
            self.wallpapers = get_wallpapers()
            self.list_view = gen_ListView()
            yield self.list_view
            yield Image(id="preview")
        yield Footer(id="footer")

    def on_mount(self) -> None:
        self.title = "Wallpi"
        self.sub_title = f"{len(self.wallpapers)} wallpapers"
        self.query_one(Header).icon = ""

    def load_preview(self, image_path: Path) -> None:
        self._latest_requested_path = image_path
        if self._preview_timer is not None:
            self._preview_timer.stop()
        self._preview_timer = self.set_timer(
            0.05,
            lambda: self._trigger_preview_load(image_path),
        )

    def _trigger_preview_load(self, image_path: Path) -> None:
        if image_path != self._latest_requested_path:
            return
        preview_widget = self.query_one("#preview", Image)
        cell_width = preview_widget.size.width or 60
        cell_height = preview_widget.size.height or 30

        target_size = (cell_width * 10, cell_height * 20)
        self._load_and_resize(image_path, target_size)

    @work(thread=True)
    def _load_and_resize(self, image_path: Path, target_size: tuple[int, int]) -> None:
        width, height = target_size
        if width <= 0 or height <= 0:
            # Fallback
            width, height = 600, 600

        pil_img = PILImage.open(image_path)
        pil_img.thumbnail((width, height))
        self.call_from_thread(self._set_preview_image, pil_img, image_path)

    def _set_preview_image(self, pil_img, image_path: Path | None = None) -> None:
        if image_path is not None and image_path != self._latest_requested_path:
            return
        self.query_one("#preview", Image).image = pil_img

    def on_list_view_highlighted(self, event: ListView.Highlighted) -> None:
        if event.item is None:
            return
        filename = str(event.item.query_one(Label).content)
        image_path = Path(PATH_DATA["wallpaper_dir"]).expanduser() / filename
        self.load_preview(image_path)

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        index = event.list_view.index
        if index is None:
            return
        src = self.wallpapers[index]
        target = Path(os.path.expanduser(PATH_DATA["target_dir"]))
        new_link(target, src)
