import random
import re
from inspect import currentframe, getframeinfo
from typing import Optional, Tuple, Any
from itertools import cycle
from collections.abc import Generator

from loguru import logger as log
from loguru import _logger
from maxconsole import MaxConsole
from rich import inspect
from rich.align import AlignMethod
from rich.box import ROUNDED, Box
from rich.color import Color, ColorParseError
from rich.columns import Columns
from rich.console import Group, JustifyMethod, RenderableType
from rich.padding import PaddingDimensions
from rich.panel import Panel
from rich.pretty import Pretty
from rich.style import StyleType
from rich.table import Table
from rich.text import Text, TextType
from loguru import logger as log


console = MaxConsole()

log.remove()


def console_filter(record):
    if record["extra"]["sink"] == "rich":
        return record


# log = logger.add('stdout', level="INFO", format="<w>{time:hh:mm:ss:SSS A}</w> <lvl>|</lvl> <c>{file.name: ^13}</c> <lvl>|</lvl>  <g>Line {line: ^5}</g> <lvl>| {level: ^8}</lvl> <r>→</r> <lvl>{message}</lvl>")
console_log = log.bind(sink="rich")

log_rich = console_log.add(
    lambda msg: console.log(
        f"{msg}", markup=True, highlight=True, log_locals=False, emoji=True
    ),
    level="INFO",
    catch=True,
    diagnose=True,
    filter=console_filter,
)
divider_fmt = " <lvl>|</lvl> "
time_fmt = "<w>{time:hh:mm:ss:SSS A}</w>"
filename_fmt = "<c>{file.name: ^13}</c>"
line_fmt = "<g>Line {line: ^5}</g>"
level_fmt = "<lvl>{level: ^8}</lvl>"
arrow = "<r> → </r>"
msg_fmt = "<lvl>{message: <25}</lvl>"
format_strings = [time_fmt, filename_fmt, line_fmt, level_fmt]
data_fmt = divider_fmt.join(format_strings)
FORMAT = f"{data_fmt}{arrow}{msg_fmt}"

log_log = log.add(
    "logs/log.log",
    level="DEBUG",
    format=FORMAT,
    mode="w",
    catch=True,
    diagnose=True,
    backtrace=True,
)


class ColorIndex:
    """Generate a list of indexes from which to make a color gradient."""
    title: str|None
    start: int | None
    end: int | None
    indexes: list[int]
    random: bool
    invert: bool
    num_of_index: int
    next_index: int | None

    def __init__(
        self,
        start: Optional[int] = None,
        end: Optional[int] = None,
        invert: Optional[bool] = False,
        num_of_index: int = 3,
        title: Optional[str] = None
    ):
        """Generate a list of indexes from start to end.

        Args:
            start (`Optional[int]`): The integer to begin the color index. Defaults to None.
            end (`Optional[int]`): The integer to end the color index with. Defaults to None.
            invert (`Optional[bool]`): _description_. Defaults to False.
            num_of_index (`Optional[int]`): The number of index in the color indexes. * Note that this value is used if a `start` or `end` value are not provided *. Defaults to 3.
        """
        self.start = start
        self.end = end
        self.num_of_index = num_of_index
        self.invert = invert
        self.title = str(title).title()

        if self.start == None:
            self.random = True
            self.num_of_index = num_of_index

        if self.end == None:
            self.random = True
            self.num_of_index = num_of_index
        
        self.next_index = -1

        if self.start:
            if self.end:
                self.random = False
                log.debug(
                    f"[bold][italic #cf75ff]self[/italic #cf75ff][#ffffff].random: [/#ffffff][#ff00ff]{self.random}[/][/bold]"
                )
            else:
                self.random = True
                log.debug(f'[bold][italic #cf75ff]self[/italic #cf75ff][#ffffff].random: [/#ffffff][#ff00ff]{self.random}[/][/bold]')
                
        else:
            self.random = True
            log.debug(f'[bold][italic #cf75ff]self[/italic #cf75ff][#ffffff].random: [/#ffffff][#ff00ff]{self.random}[/][/bold]')
            

        if self.start == None:
            self.start = self._generate_start()
            log.debug(
                f"[bold][italic #cf75ff]self[/italic #cf75ff][#ffffff].start: [/#ffffff][#ff00ff]{self.start}[/][/bold]"
            )

        if self.end == None:
            self.end = self._generate_end()
            log.debug(
                f"[bold][italic #cf75ff]self[/italic #cf75ff][#ffffff].end: [/#ffffff][#ff00ff]{self.end}[/][/bold]"
            )

        if self.invert:
            self.invert = invert
        else:
            self.invert = False
        log.debug(f'[bold][italic #cf75ff]self[/italic #cf75ff][#ffffff].invert: [/#ffffff][#ff00ff]{self.invert}[/][/bold]')
        

        # Generate Indexes from start and stop values
        self.indexes = self._generate_indexes()

    def __iter__(self):
        return self

    def __next__(self):
        if self.indexes:
            if not self.next:
                self.next = 1
                return self.indexes[0]
            else:
                next = self.next
                self.next += 1
                if next >= len(self.indexes):
                    self.next = 0
                    raise StopIteration
                return self.indexes[next]
        else:
            raise StopIteration

    def __send__(self, index: int):
        if index <= len(self.indexes):
            return self.indexes[index]
            self.next = index + 1

    def __throw__(self, *args):
        raise StopIteration

    def __repr__(self):
        body = ", ".join([str(i) for i in self.indexes])
        return f"{self.__class__.__name__}({self.start}, {self.end})\n\t{body}"

    def __rich__(self):
        if not self.start:
            start_gen = True
        else:
            start_gen = False

        if not self.end:
            end_gen = True
        else:
            end_gen = False

        body = ", ".join([str(i) for i in self.indexes])
        if self.title == None:
            table_title = f"[bold #00ffff]{self.__class__.__name__}[/]"
        else:
            table_title = f"[bold #00ffff]{self.title}[/]"
        table = Table(
            
            title=table_title,
            box=ROUNDED,
            border_style="bold #ffffff",
            row_styles=["italic #ff00ff", "italic #af00ff"],
            expand=False,
        )
        table.add_column("[bold #ffffff]Variable[/]", justify="left", ratio=1)
        table.add_column(
            "[bold #ffffff]Value[/]", justify="center", ratio=3, min_width=70
        )
        table.add_column("[bold #ffffff]Generated[/]", justify="center", ratio=1)
        table.add_row("Start", f"{self.start}", f"{start_gen}")
        table.add_row("End", f"{self.end}", f"{end_gen}")
        table.add_row("Inverted", f"{self.invert}", "[dim]n/a[/dim]")
        table.add_row("Index", f"[bold #cf75ff]{body}[/]", "[bold #00ff00]True[/]")
        return table

    def validate__end(self, __end: int) -> int:
        if self.invert:
            if __end < 0:
                return __end + 9
            else:
                return __end
        else:
            if __end > 9:
                return __end - 9
            else:
                return __end

    def _generate_start(self) -> int:
        """Generate a random starting index. Private function used when a start value is not provided."""
        _start = random.randint(0, 9)
        self.start = _start
        log.debug(f"Generated start: {_start}")
        return _start

    def _generate_end(self) -> int:
        """Generate the value of the end of the random index. Private function used when an end value isn't provided.

        Args:
            start (`Optional[int]`): The index from which to generate the end value. Defaults to generating a random start.
            invert (`Optional[bool]`): Whether to travel up or down the index. Defaults to `False`.
            num_of_index (`Optional[int]`): The number of stops in the color index. Defaults to `3`.

        Returns:
            `int`: The final integer of a color index.
        """
        if self.start not in list(range(0, 10)):
            self.start = self._generate_start()
            log.debug(f"Generated start to generate `end`: {self.start}")

        if self.invert == None:
            log.debug(f"invert not set. Setting `invert`...")
            self.invert = False
            log.debug(
                f"[italic bold #cc75ff]self[/][bold #ffffff].invert:[/] [bold #ff00ff]{self.invert}[/]"
            )

        if self.num_of_index == None:
            log.debug(f"num_of_index not set. Setting `num_of_index`...")
            num_of_index = 3
            log.debug(
                f"[bold #ffffff].num_of_index:[/] [bold #ff00ff]{num_of_index}[/]"
            )

        # Generate End
        if self.invert:
            step = -1
            bump_end = -1
        else:
            step = 1
            bump_end = 1



        __end = self.start + (self.num_of_index * step)
        log.debug(f"[italic bold #cc75ff]__end[/][bold #ffffff] {__end}[/]")

        _end = self.validate__end(__end)
        log.debug(f"[italic bold #cc75ff]_end[/][bold #ffffff] {_end}[/]")

        return _end


    def _generate_indexes(self) -> list[int]:
        """Generate a sequence of integers from which to generate a gradient.

        Args:
            start (`Optional[int]`): The integer from which to start the index. Defaults to `self.start` if not provided.
            end (`Optional[int]`): Then integer from which to end the index. Defaults to `self.end` if not provided.
            invert (`Optional[bool]`): Whether the indexes should proceed negatively or positively to the end value.  Defaults to `self.random` if not provided.

        Returns:
            `list[int]`: The list of color index integers.
        """
        # Input Validation
        if self.start == None:
            start = self._generate_start()
            self.start = start

        if self.num_of_index == None:
            num_of_index = 3

        if self.invert == None:
            if self.invert:
                invert = self.invert
            else:
                invert = False
                self.invert = invert

        if self.end == None:
            if self.end:
                end = self.end
            else:
                end = self._random_end(
                    self.start, invert=invert, num_of_index=num_of_index
                )
                self.end = end

        # Generate Index
        # If index is inverted
        if self.invert:
            if self.start > self.end:
                self.indexes = list(range(self.start, self.end - 1, -1))
                return self.indexes
            else:
                _index1 = list(range(self.start, -1, -1))
                _index2 = list(range(9, self.end - 1, -1))
                self.indexes = _index1 + _index2
                return self.indexes

        # If not inverted (regular ascending) index
        else:
            if self.start < self.end:
                self.indexes = list(range(self.start, self.end + 1))
                return self.indexes
            else:
                _index1 = list(range(self.start, 10))
                _index2 = list(range(0, self.end + 1))
                self.indexes = _index1 + _index2
                return self.indexes


if __name__ == "__main__":
    console = MaxConsole()
    color_index1 = ColorIndex(start=0, end=9, invert=False, title="Color Index 1")
    console.clear()
    console.print("\n\n")
    console.print(color_index1, justify="center")
    color_index2 = ColorIndex(9,6,True,title="Color Index 2")
    console.print(color_index2, justify='center')
    color_index3 = ColorIndex(title="Color Index 3")
    console.print(color_index3, justify="center")
