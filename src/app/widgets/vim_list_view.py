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

    def action_cursor_down(self) -> None:
        if self.index is None:
            return

        if self.index >= len(self) - 1:
            self.index = 0
        else:
            super().action_cursor_down()

    def action_cursor_up(self) -> None:
        if self.index is None:
            return

        if self.index <= 0:
            self.index = len(self) - 1
        else:
            super().action_cursor_up()
