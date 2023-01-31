# Itachi Userbot - A telegram userbot.
# Copyright (C) 2021 Itachisann

# This program is free software: you can redistribute it and / or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY
# without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see < https: // www.gnu.org/licenses/>.


import logging
import logging.handlers

CCRI = '\033[48;5;124m'  # CRITICAL
CERR = '\033[38;5;124m'  # ERROR
CWAR = '\033[38;5;202m'  # WARNING
CINF = '\033[38;5;15m'  # INFO
CDEB = '\033[38;5;28m'  # DEBUG
CEND = '\033[0m'  # ANSI END
CORA = '\033[33;1m'  # ORANGE
CBOT = '\033[94;1m'  # BOT (blue?)
CUSR = '\033[38;5;118m'  # USER (white?)


class CustomPercentStyle(logging.PercentStyle):
    """Replace the default_format to our own and override the format method."""
    default_format = "[%(levelname)s / %(asctime)s] %(name)s: %(message)s"

    def format(self, record):
        """Use ANSI escape code for the default format, else ignore it"""
        super().format(record)
        if self._fmt == self.default_format:
            first = "[%(asctime)s / %(levelname)s] "

            if record.name == "root":
                second = f"{CCRI}%(name)s:{CEND} %(message)s"
            elif record.name.startswith('telethon'):
                second = f"{CBOT}%(name)s:{CEND} %(message)s"
            elif record.name.startswith('userbot'):
                second = f"{CORA}%(name)s:{CEND} %(message)s"
            else:
                second = "%(name)s: %(message)s"

            FORMATS = {
                logging.CRITICAL: CCRI + first + CEND + second,
                logging.ERROR: CERR + first + CEND + second,
                logging.WARNING: CWAR + first + CEND + second,
                logging.INFO: CINF + first + CEND + second,
                logging.DEBUG: CDEB + first + CEND + second,
                'DEFAULT': self.default_format
            }
            fmt = FORMATS.get(record.levelno, FORMATS['DEFAULT'])
        else:
            fmt = self._fmt
        return fmt % record.__dict__


class CustomFormatter(logging.Formatter):
    """Update the default Formatter's _STYLES dict to use our custom one"""
    _STYLES = logging._STYLES.update({
        '%': (CustomPercentStyle, logging.BASIC_FORMAT)
    })

    def logFormat(self, record):
        """Format a log record without ANSI escapes for dumping"""
        super().format(record)
        record.__dict__.update(levelAlias=record.levelname[:1])
        fmt = "{asctime} [{levelAlias}] - {name}: {message}".format(
            **record.__dict__
        )
        if record.exc_text:
            fmt += f"\n{record.exc_text}"
        return fmt


class TargetNotSetError(Exception):
    """Raised when dumps is called without a target"""
    pass


class CustomMemoryHandler(logging.handlers.MemoryHandler):
    """Inherits the default MemoryHandler and implements handled buffers"""
    handledbuffer = []

    def setFlushLevel(self, level):
        """Change the current level set for flushing new records"""
        self.flushLevel = logging._checkLevel(level)

    def dump(self):
        """Returns a list of all the handled and pending records"""
        return self.handledbuffer + self.buffer

    def dumps(self, level=None):
        """Returns a list of strings for all the handled and pending records"""
        if self.target is None:
            raise TargetNotSetError(
                'Target handler is not set. Cannot format the records.'
            )
        _format = self.target.format
        if (
            self.target.formatter and
            hasattr(self.target.formatter, 'logFormat')
        ):
            _format = self.target.formatter.logFormat
        return [
            _format(record)
            for record in (self.handledbuffer + self.buffer)
            if record.levelno >= (level if level else self.flushLevel or 0)
        ]

    def emit(self, record):
        """
        Get rid of the first record from handled or main buffer if capicity is
        reached
        """
        if len(self.handledbuffer + self.buffer) >= self.capacity:
            if self.handledbuffer:
                del self.handledbuffer[0]
            else:
                del self.buffer[0]
        super().emit(record)

    def flush(self):
        """
        By default flush doesn't check the log level before calling handle
        """
        offset = -(self.capacity - len(self.buffer))
        self.acquire()
        try:
            if self.target:
                for record in self.buffer:
                    if record.levelno >= self.flushLevel:
                        self.target.handle(record)
                self.handledbuffer = self.handledbuffer[offset:] + self.buffer
                self.buffer.clear()
        finally:
            self.release()

    def flushBuffers(self):
        """Clear the handled and pending buffers list"""
        self.buffer.clear()
        self.handledbuffer.clear()
