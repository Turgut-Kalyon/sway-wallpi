from textual.binding import Binding
from textual.widgets import ListView


class VimListView(ListView):
    BINDINGS = [
        Binding("j", "cursor_down", "Down"),
        Binding("k", "cursor_up", "Up"),
        Binding("down", "cursor_down", show=False),
        Binding("up", "cursor_up", show=False),
        Binding("enter", "select_cursor", show=False),
    ]
