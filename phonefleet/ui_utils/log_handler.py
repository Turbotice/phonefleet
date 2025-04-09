import logging
from nicegui import ui


class LogElementHandler(logging.Handler):
    """A logging handler that emits messages to a log element."""

    def __init__(self, element: ui.log, level: int = logging.NOTSET) -> None:
        self.element = element
        super().__init__(level)
        self.formatter = logging.Formatter(
            fmt="[%(asctime)s] %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    def emit(self, record: logging.LogRecord) -> None:
        try:
            msg = self.format(record)
            self.element.push(msg)
        except Exception:
            self.handleError(record)


logger = logging.getLogger()


def log_view():
    log = ui.log(max_lines=None).classes(
        "bg-slate-900 text-green-400 text-bold text-wrap"
    )
    handler = LogElementHandler(log)
    logger.addHandler(handler)
    ui.context.client.on_disconnect(lambda: logger.removeHandler(handler))
