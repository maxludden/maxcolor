import random
import re
from inspect import currentframe, getframeinfo
from typing import Optional, Tuple

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

# ============================================================================ #
# MaxColor v1.0.3
# ============================================================================ #
__version__ = "1.0.3"
console = MaxConsole()

# ============================================================================ #
#     Initialize Logging


def info_filter(record) -> bool:
    if record['level'].no >= 20:
        return record


log.remove()
# Debug
log_verbose = log.add(
    'logs/verbose.log',
    level='DEBUG',
    format="{time:hh:mm:ss:SSS A} | {file.name: ^13} |  Line {line: ^5} | {level: <8} →  {message}"
)
# Info
info_log = log.add(
    'logs/log.log',
    level='INFO',
    format="{time:hh:mm:ss:SSS A} | {file.name: ^13} |  Line {line: ^5} | {level: <8} →  {message}"
)
# Success
log_rich = log.add(
    lambda msg: console.log(f"{msg}"),
    level='SUCCESS',
    format="{time:hh:mm:ss:SSS A} [#2e2e2e]|[/] [bold #ff00ff]{file.name: ^13}[/] [#2e2e2e]|[/]  [#ddffdd]Line {line: ^5}[/] [#2e2e2e]|[/] [#00ff00]{level: <8}[/] [#22ffee]→ [/] [#00ff00]{message}[/]",
    filter=lambda record: True if record['level'].no >= 20 else False,
    colorize=True,
    backtrace=True,
    diagnose=True
)
# Error
log_error = log.add(
    lambda msg: console.log(f"{msg}"),
    level='ERROR',
    format="[#ffffff on #ff0000]{time:hh:mm:ss:SSS A} | [/#ffffff on #ff0000][bold #ffffff on default]{file.name: ^13}[/bold #ffffff on default]  [#000000 on #ff0000] | Line {line: ^5} | [/#000000 on #ff0000] [bold #ff0000 on default]{message}[/bold #ff0000 on default]",
    filter=lambda record: True if record['level'].no >= 40 else False,
    colorize=True,
    backtrace=True,
    diagnose=True,
    catch=True
)
log.debug("Initialized logging!")

# ============================================================================ #
#     Exceptions


class InvalidHexColor(ColorParseError):
    pass


class InvalidRGBColor(ColorParseError):
    pass


class InvalidColor(Exception):
    pass

INDEXES_COLORS = "[bold][#ff0000]Co[/#ff0000][#ff8800]l[/#ff8800][#ffff00]or[/#ffff00] [#00ff00]Ind[/#00ff00][#00ffff]ex[/#00ffff][#249df1]es[/#249df1][#5f00ff]/Co[/#5f00ff][#af00ff]lo[/#af00ff][#ff00ff]rs[/#ff00ff]"
# ============================================================================ #
#     Compile Regular Expressions
HEX_REGEX = re.compile(r"^\#([0-9a-fA-F]{6})$|^ ([0-9a-fA-F]{6})$", re.VERBOSE)
ANSI_REGEX = re.compile(r"color\(([0-9]{1,3})\)$", re.VERBOSE)
RGB_REGEX = re.compile(r"rgb\(([\d\s,]+)\)$", re.VERBOSE)
COLOR_REGEX = re.compile(
    r"^\#([0-9a-fA-F]{6})$|^ ([0-9a-fA-F]{6})$|color\(([0-9]{1,3})\)$|rgb\(([\d\s,]+)\)$",
    re.VERBOSE,
)

# ============================================================================ #
# Color Lists
# ============================================================================ #

# ============================================================================ #
#     _all_colors()


def _all_colors() -> list[str]:
    """Private function to generate a list of named colors."""
    return [
        "magenta",
        "light_purple",
        "purple",
        "blue",
        "light_blue",
        "cyan",
        "green",
        "yellow",
        "orange",
        "red",
    ]


# ============================================================================ #
#     _hex_colors()
def _hex_colors() -> list[str]:
    """Private function to generate a list of the HEX translations of the named colors."""
    return [
        "#ff00ff",
        "#af00ff",
        "#5f00ff",
        "#0000ff",
        "#249df1",
        "#00ffff",
        "#00ff00",
        "#ffff00",
        "#ff8800",
        "#ff0000",
    ]


# ============================================================================ #
#     _rgb_tuples()
def _rgb_tuples() -> list[tuple]:
    """Private function to generate a list of the RGB translations of the named colors."""
    return [
        (255, 0, 255),  # magenta
        (175, 0, 255),  # light_purple
        (95, 0, 255),  # purple
        (0, 0, 255),  # blue
        (36, 157, 241),  # light_blue
        (0, 255, 0),  # cyan
        (0, 255, 0),  # green
        (255, 255, 0),  # yellow
        (255, 128, 0),  # orange
        (255, 0, 0),  # red
    ]

# ============================================================================ #
# Index Validation
# ============================================================================ #


# ============================================================================ #
#     Start Index

def __validate_color_start_index(start_index: int, test: bool = False) -> int | None:
    """Validate the index from which to start the color gradient.

    Args:
        start_index (`int``): The color index to validate.
        test (`bool`, optional): Whether to display the validation. Defaults to False.

    Raises:
        ColorParseError: `start_index` must be less than 10.
        ColorParseError: `start_index` must be greater than or equal to zero.

    Returns:
        int|None: The validated start_index
    """
    all_colors = _all_colors()
    all_indexes = len(all_colors)
    if start_index > all_indexes:
        raise ColorParseError(
            f"Starting Index Invalid: {start_index}\n\n\tMust be less that {all_indexes}")
    elif start_index < 0:
        raise ColorParseError(
            f"Starting Index Invalid: {start_index}\n\n\tMust be grater than zero.")
    else:
        if test:
            console.print(
                f"Validated `start_index`: {start_index}"
            )
        return start_index


# ============================================================================ #
#     End Index
def __validate_color_end_index(end_index: int, test: bool = False) -> int | None:
    """Validate the index from which to end the color gradient.

    Args:
        end_index (`int``): The color index to validate.
        test (`bool`, optional): Whether to display the validation. Defaults to False.

    Raises:
        ColorParseError: `end_index` must be less than 10.
        ColorParseError: `end_index` must be greater than or equal to zero.

    Returns:
        int|None: The validated end_index.
    """
    all_indexes = len(_all_colors())
    if end_index > all_indexes:
        raise ColorParseError(
            f"Ending Index Invalid: {end_index}\n\n\tMust be less that {all_indexes}")
    elif end_index < 0:
        raise ColorParseError(
            f"Ending Index Invalid: {end_index}\n\n\tMust be grater than zero.")
    else:
        if test:
            console.print(
                f"Validated `start_index`: {end_index}"
            )
        return end_index


# ============================================================================ #
#    Validate Next Index
def __validate_next_index(_next_index: int, test: bool = False) -> int | None:
    """Validate the next color index.

    Args:
        _next_index ('int'): The next color index for the color range.
        test (`bool`, optional): Whether to print the validation to the console. Defaults to False.

    Returns:
        int|None: The valid next index.

    Raises:
        ValueError: If the next_index is greater than len(colors) or less than zero.
    """
    all_indexes = len(_all_colors())
    if _next_index > 9:
        next_index = _next_index - all_indexes
        if test:
            console.log(
                f'\n\t[#ffffff]The[/#ffffff][italic bold #ff00ff] `_next_index`[/italic bold #ff00ff][#ffffff],[/#ffffff][bold #00ffff] {_next_index}[/bold #00ffff][#ffffff], has [/#ffffff][#ffffff on #ff0000]exceeded[/#ffffff on #ff0000][#ffffff] the available indexes.[\#ffffff]\n\t[italic #00ffff]Adjusting [/#00ffff][bold #ffffff]`next_index`[/#ffffff][#00ffff]... now:[/#00ffff] [bold #00ff00]{next_index}[/#00ff00]',
                log_locals=True,
                markup=True,
                highlight=True
            )
            return next_index
    elif _next_index < 0:
        next_index = _next_index + all_indexes
        if test:
            console.log(
                f"\n\t[#ffffff]The[/#ffffff][italic bold #ff00ff] `_next_index`[/italic bold #ff00ff][#ffffff], [/#ffffff][bold #00ffff] {_next_index},/bold #00ffff][#ffffff], doesn't [/#ffffff][#ffffff on #ff0000]exist...[/#ffffff on #ff0000][#ffffff] the available indexes.[\#ffffff]\n\t[italic #00ffff]Adjusting [/#00ffff][bold #ffffff]`next_index`[/#ffffff][#00ffff]... now:[/#00ffff] [bold #00ff00]{next_index}[/#00ff00]' doesn't exist.\n\tAdjusting `next_index`... now: {next_index}",
                log_locals=True,
                markup=True,
                highlight=True
            )
            return next_index
    elif _next_index in range(0, 10):
        if test:
            console.log(
                f'[italic bold #ff00ff]`_next_index`[/italic bold #ff00ff][#ffffff]:[/#ffffff] [italic bold #ff00ff]{_next_index}[/italic bold #ff00ff] [bold #00ff00]⎷[/bold #00ff00][#ddffdd]Validated[/#ddffdd]',
                log_locals=True,
                markup=True,
                highlight=True
            )
        return _next_index
    else:
        raise ValueError(
            f"Invalid Next Index: {_next_index}. Next Index must fall in between zero and nine.")


# ============================================================================ #
# def generate_random_color_range()
# ============================================================================ #
def _generate_random_color_range(
    color_stops: int = 3, 
    random_invert: bool = True, 
    invert: bool = False, 
    test: bool = False) -> list[tuple]:
    """Generate a random sequence of colors from which to make a gradient.

    Args:
        color_stops (`int`): Number of colors in the generated sequence. Defaults to three.
        random_invert (`bool`): Whether to random go up or down the spectrum. Defaults to True.
        invert (`bool`): Whether to tavel up or down the spectrum. Only effects the outcome if `random_invert` is `False`. Defaults to False.
        test (`bool`): Whether to log to the console for test purposes. Defaults to False.

    Returns:
        `list[tuple]`: a list of tuples that carry the gradient's rgb components in sequence.
    """
    all_colors = _all_colors()
    rgb_tuples = _rgb_tuples()

    colors = []
    color_range = []
    color_range_indexes = []

    # Start Index
    start = random.choice(all_colors)
    if test:
        console.print(f"start: {start}")

    start_index = all_colors.index(start)
    color_range_indexes.append(start_index)
    if test:
        console.print(f"Start Index: {start_index}")

    if random_invert:
        invert = random.choice([True, False])
    else:
        invert = invert
    if test:
        console.log(f"Random Invert: {random_invert}")
        console.log(f"Invert: {invert}")

    # Determine which direction to traverse the spectrum
    if invert:
        step = -1
    else:
        step = 1

    # (de)Increment the index every color stop
    if test:
        console.log("Begin looping through the spectrum to get the next indexes.")

    for x in range(1, color_stops + 1):
        _next_index = start_index + (x * step) 
        if _next_index > 9:
            _next_index -= 10
        if _next_index < 0:
            _next_index += 10
        if test:
            console.log(f"\n\n\tIndex #{x}. `_next_index`: {_next_index}")

        next_index = __validate_next_index(_next_index)
        if test:
            console.log(f"\n\n\tIndex #{x}. `next_index`: {next_index}")

        color_range_indexes.append(next_index)
        if test:
            console.log(
                f"\n\n\tColor Range Indexes: {', '.join([str(index) for index in color_range_indexes])}")

    # ============================================================================ #
    #     Generate `color_range``
    panels = []
    hex_colors = _hex_colors()
    for x, index in enumerate(color_range_indexes, start=1):
        color_range.append(rgb_tuples[index])
        new_panel = Panel(
            f"{rgb_tuples[index]}",
            title = f"[bold #00ffff]Index {x}[/]",
            border_style=f'bold {hex_colors[index]}',
            style=f'#000000 on {hex_colors[index]}',
            width = 30,
            padding=(1,4)
        )
        panels.append(new_panel)

    if test:
        title = INDEXES_COLORS
        console.print(
            Panel(
                Columns(
                    panels,
                    equal=True,
                    align='center'
                ),
                title=title,
                expand=False,
            ),
            justify="center"
        )

    return color_range

def __validate_start(start: str|tuple) -> int:
    """Validate the color from which to start the gradient.

    Args:
        start (`str | tuple`): The starting color
    
    Returns:
        `ing`: the index of the starting color if it's valid.
    """
    all_colors = _all_colors()
    hex_colors = _hex_colors()
    rgb_tuples = _rgb_tuples()
    if start in all_colors:
        return all_colors.index(start)
    elif start in hex_colors:
        return hex_colors.index(start)
    elif start in rgb_tuples:
        return rgb_tuples.index(start)
    else:
        raise ValueError(f"{start} is not a valid named_color, hex, or rgb tuple.")


def __validate_end(end: str|tuple) -> int:
    """Validate the color from which to start the gradient.

    Args:
        start (`str | tuple`): The starting color
    
    Returns:
        `ing`: the index of the starting color if it's valid.
    """
    all_colors = _all_colors()
    hex_colors = _hex_colors()
    rgb_tuples = _rgb_tuples()
    if end in all_colors:
        return all_colors.index(end)
    elif end in hex_colors:
        return hex_colors.index(end)
    elif end in rgb_tuples:
        return rgb_tuples.index(end)
    else:
        raise ValueError(f"{end} is not a valid named_color, hex, or rgb tuple.")


def generate_color_range(start: str|tuple, end: str|tuple, invert: bool = False, test: bool = False):
    """Generate a sequence of colors from which to make a gradient.

    Args:
        start (`str|tuple`): The color from which to start the gradient
        end (`str|tuple`): The color to end the gradient with.
        invert (`bool`): Whether to tavel up or down the spectrum. Defaults to False (traveling in the positive direction)
        test (`bool`): Whether to log to the console for test purposes. Defaults to False.

    Returns:
        `list[tuple]`: a list of tuples that carry the gradient's rgb components in sequence.
    """
    # Validate start and retrieve its index
    start_index = __validate_start(start)

    # Validate end and retrieve it's index
    end_index = __validate_end(end)

    # Allocate and initialize list of indexes
    color_range_indexes = [start_index]
    

    if invert:
        step = -1 # Reduce the next index at each step
        stop_index = end_index - 1 # Adjust the index at which to stop
    else:
        step = 1 # Increase the next_index at each step
        stop_index = end_index + 1 # Adjust the index at which to stop

    index = 0
    steps = 0
    _next_index = -1

    if test:
        console.log(f"Looping through color sequence to generate the color range indexes")
    
    while index != stop_index:
        steps += 1
        __next_index = start_index + (steps * step)

        if __next_index > 9:
            _next_index -= __next_index - 10
        else:
            _next_index  = __next_index - 10

        if _next_index < 0:
            next_index = _next_index + 10
        if next_index not in range(0,10):
            raise IndexError(f'`__next_index`: {__next_index} is not a valid Index. Valid indexes fall between zero and nine.')
        elif next_index in range(0, 10):
            color_range_indexes.append(next_index)
            if test:
                console.log(f"Adding the next index: {next_index}")
        else:
            raise ValueError(f"__next_index: {__next_index} is not with the range of indexes 0-9.")


if __name__ == "__main__":
    start_idex = random.choice(range(0,10))
    start = _all_colors()[start_idex]
    end_idex = random.choice(range(0,10))
    end = _all_colors()[end_idex]
    generate_color_range(start,end,False, True)