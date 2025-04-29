from contextlib import contextmanager
from nicegui import ui


@contextmanager
def disable_buttons():
    # Query all buttons on the page
    buttons = ui.query("button")
    buttons.props(add="disabled")
    try:
        yield
    finally:
        buttons.props(remove="disabled")
