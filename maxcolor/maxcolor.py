import random
import re
from enum import Enum
from functools import lru_cache, wraps
from sys import stderr, stdout
from typing import Optional, Tuple

from loguru import logger
from maxconsole import MaxConsole
from rich import inspect
from rich.align import AlignMethod
from rich.box import ROUNDED, Box
from rich.color import Color, ColorParseError
from rich.console import Group, JustifyMethod, RenderableType
from rich.padding import PaddingDimensions
from rich.panel import Panel
from rich.pretty import Pretty
from rich.style import StyleType
from rich.text import Text, TextType
from rich.table import Table
from rich.columns import Columns

from inspect import getframeinfo, currentframe

console = MaxConsole()
logger.remove()
# log = logger.add('stdout', level="INFO", format="<w>{time:hh:mm:ss:SSS A}</w> <lvl>|</lvl> <c>{file.name: ^13}</c> <lvl>|</lvl>  <g>Line {line: ^5}</g> <lvl>| {level: ^8}</lvl> <r>→</r> <lvl>{message}</lvl>")
log = logger.add(
    lambda msg: console.log(
        f"{msg}", markup=True, highlight=True, log_locals=True, emoji=True
    )
)

__version__ = "1.0.3"


class InvalidHexColor(ColorParseError):
    pass


class InvalidRGBColor(ColorParseError):
    pass


class InvalidColor(Exception):
    pass

GRADIENT = '[#FF0000]G[/][#ffa200]r[/][yellow]a[/][#00ff00]d[/][#00ffff]i[/][#0000ff]e[/][#b96aff]n[/][#6400fb]t[/]'
BACK_FRAME = '[bold][#ff0000]Ba[/#ff0000][#ff8800]c[/#ff8800][#ffff00]k[/#ffff00][#00ff00] F[/#00ff00][#00ffff]r[/#00ffff][#0000ff]a[/#0000ff][#249df1]m[/#249df1][#5f00ff]e[/#5f00ff][/bold]'

def _next_line_num():
    back_frame1 = currentframe().f_back
    inspect(back_frame1)
    # console.print(
    #     Panel(
    #         back_frame,
    #         title=BACK_FRAME,
    #         title_align='left',
    #         border_style='bold #ffffff',
    #         expand=False,
    #     )
    # )


class ColorType(Enum):
    """Enum class for the different color types."""

    hex = "hex"
    rgb = "rgb"
    ansi = "ansi"
    named = "named"
    invalid = "invalid"


# Compile regex patters for color parsing
HEX_REGEX = re.compile(r"^\#([0-9a-fA-F]{6})$|^ ([0-9a-fA-F]{6})$", re.VERBOSE)
ANSI_REGEX = re.compile(r"color\(([0-9]{1,3})\)$", re.VERBOSE)
RGB_REGEX = re.compile(r"rgb\(([\d\s,]+)\)$", re.VERBOSE)
COLOR_REGEX = re.compile(
    r"^\#([0-9a-fA-F]{6})$|^ ([0-9a-fA-F]{6})$|color\(([0-9]{1,3})\)$|rgb\(([\d\s,]+)\)$",
    re.VERBOSE,
)


# Static Files
@lru_cache
def get_ansi_colors() -> dict:
    """
    Generate a dictionary with using ANSI color integers as keys and the name of the color as the value."""
    ANSI_COLORS = {
        "0": "black",
        "1": "red",
        "2": "green",
        "3": "yellow",
        "4": "blue",
        "5": "magenta",
        "6": "cyan",
        "7": "white",
        "8": "bright_black",
        "9": "bright_red",
        "10": "bright_green",
        "11": "bright_yellow",
        "12": "bright_blue",
        "13": "bright_magenta",
        "14": "bright_cyan",
        "15": "bright_white",
        "16": "gray0",
        "17": "navy_blue",
        "18": "dark_blue",
        "20": "blue3",
        "21": "blue1",
        "22": "dark_green",
        "25": "deep_sky_blue4",
        "26": "dodger_blue3",
        "27": "dodger_blue2",
        "28": "green4",
        "29": "spring_green4",
        "30": "turquoise4",
        "32": "deep_sky_blue3",
        "33": "dodger_blue1",
        "40": "green3",
        "41": "spring_green3",
        "36": "dark_cyan",
        "37": "light_sea_green",
        "38": "deep_sky_blue2",
        "39": "deep_sky_blue1",
        "47": "spring_green2",
        "43": "cyan3",
        "44": "dark_turquoise",
        "45": "turquoise2",
        "46": "green1",
        "48": "spring_green1",
        "49": "medium_spring_green",
        "50": "cyan2",
        "51": "cyan1",
        "88": "dark_red",
        "125": "deep_pink4",
        "55": "purple4",
        "56": "purple3",
        "57": "blue_violet",
        "94": "orange4",
        "59": "gray37",
        "60": "medium_purple4",
        "62": "slate_blue3",
        "63": "royal_blue1",
        "64": "chartreuse4",
        "71": "dark_sea_green4",
        "66": "pale_turquoise4",
        "67": "steel_blue",
        "68": "steel_blue3",
        "69": "cornflower_blue",
        "76": "chartreuse3",
        "73": "cadet_blue",
        "74": "sky_blue3",
        "81": "steel_blue1",
        "114": "pale_green3",
        "78": "sea_green3",
        "79": "aquamarine3",
        "80": "medium_turquoise",
        "112": "chartreuse2",
        "83": "sea_green2",
        "85": "sea_green1",
        "122": "aquamarine1",
        "87": "dark_slate_gray2",
        "91": "dark_magenta",
        "128": "dark_violet",
        "129": "purple",
        "95": "light_pink4",
        "96": "plum4",
        "98": "medium_purple3",
        "99": "slate_blue1",
        "106": "yellow4",
        "101": "wheat4",
        "102": "gray53",
        "103": "light_slate_gray",
        "104": "medium_purple",
        "105": "light_slate_blue",
        "149": "dark_olive_green3",
        "108": "dark_sea_green",
        "110": "light_sky_blue3",
        "111": "sky_blue2",
        "150": "dark_sea_green3",
        "116": "dark_slate_gray3",
        "117": "sky_blue1",
        "118": "chartreuse1",
        "120": "light_green",
        "156": "pale_green1",
        "123": "dark_slate_gray1",
        "160": "red3",
        "126": "medium_violet_red",
        "164": "magenta3",
        "166": "dark_orange3",
        "167": "indian_red",
        "168": "hot_pink3",
        "133": "medium_orchid3",
        "134": "medium_orchid",
        "140": "medium_purple2",
        "136": "dark_goldenrod",
        "173": "light_salmon3",
        "138": "rosy_brown",
        "139": "gray63",
        "141": "medium_purple1",
        "178": "gold3",
        "143": "dark_khaki",
        "144": "navajo_white3",
        "145": "gray69",
        "146": "light_steel_blue3",
        "147": "light_steel_blue",
        "184": "yellow3",
        "157": "dark_sea_green2",
        "152": "light_cyan3",
        "153": "light_sky_blue1",
        "154": "green_yellow",
        "155": "dark_olive_green2",
        "193": "dark_sea_green1",
        "159": "pale_turquoise1",
        "162": "deep_pink3",
        "200": "magenta2",
        "169": "hot_pink2",
        "170": "orchid",
        "207": "medium_orchid1",
        "172": "orange3",
        "174": "light_pink3",
        "175": "pink3",
        "176": "plum3",
        "177": "violet",
        "179": "light_goldenrod3",
        "180": "tan",
        "181": "misty_rose3",
        "182": "thistle3",
        "183": "plum2",
        "185": "khaki3",
        "222": "light_goldenrod2",
        "187": "light_yellow3",
        "188": "gray84",
        "189": "light_steel_blue1",
        "190": "yellow2",
        "192": "dark_olive_green1",
        "194": "honeydew2",
        "195": "light_cyan1",
        "196": "red1",
        "197": "deep_pink2",
        "199": "deep_pink1",
        "201": "magenta1",
        "202": "orange_red1",
        "204": "indian_red1",
        "206": "hot_pink",
        "208": "dark_orange",
        "209": "salmon1",
        "210": "light_coral",
        "211": "pale_violet_red1",
        "212": "orchid2",
        "213": "orchid1",
        "214": "orange1",
        "215": "sandy_brown",
        "216": "light_salmon1",
        "217": "light_pink1",
        "218": "pink1",
        "219": "plum1",
        "220": "gold1",
        "223": "navajo_white1",
        "224": "misty_rose1",
        "225": "thistle1",
        "226": "yellow1",
        "227": "light_goldenrod1",
        "228": "khaki1",
        "229": "wheat1",
        "230": "cornsilk1",
        "231": "gray100",
        "232": "gray3",
        "233": "gray7",
        "234": "gray11",
        "235": "gray15",
        "236": "gray19",
        "237": "gray23",
        "238": "gray27",
        "239": "gray30",
        "240": "gray35",
        "241": "gray39",
        "242": "gray42",
        "243": "gray46",
        "244": "gray50",
        "245": "gray54",
        "246": "gray58",
        "247": "gray62",
        "248": "gray66",
        "249": "gray70",
        "250": "gray74",
        "251": "gray78",
        "252": "gray82",
        "253": "gray85",
        "254": "gray89",
        "255": "gray93",
    }
    return ANSI_COLORS


@lru_cache
def get_colors_ansi() -> dict:
    """Generate a dictionary with using W3 colors as keys and their ansi integers values."""
    COLORS_ANSI = {
        "black": 0,
        "red": 1,
        "green": 2,
        "yellow": 3,
        "blue": 4,
        "magenta": 5,
        "cyan": 6,
        "white": 7,
        "bright_black": 8,
        "bright_red": 9,
        "bright_green": 10,
        "bright_yellow": 11,
        "bright_blue": 12,
        "bright_magenta": 13,
        "bright_cyan": 14,
        "bright_white": 15,
        "grey0": 16,
        "navy_blue": 17,
        "dark_blue": 18,
        "blue3": 20,
        "blue1": 21,
        "dark_green": 22,
        "deep_sky_blue4": 25,
        "dodger_blue3": 26,
        "dodger_blue2": 27,
        "green4": 28,
        "spring_green4": 29,
        "turquoise4": 30,
        "deep_sky_blue3": 32,
        "dodger_blue1": 33,
        "green3": 40,
        "spring_green3": 41,
        "dark_cyan": 36,
        "light_sea_green": 37,
        "deep_sky_blue2": 38,
        "deep_sky_blue1": 39,
        "spring_green2": 47,
        "cyan3": 43,
        "dark_turquoise": 44,
        "turquoise2": 45,
        "green1": 46,
        "spring_green1": 48,
        "medium_spring_green": 49,
        "cyan2": 50,
        "cyan1": 51,
        "dark_red": 88,
        "deep_pink4": 125,
        "purple4": 55,
        "purple3": 56,
        "blue_violet": 57,
        "orange4": 94,
        "grey37": 59,
        "gray37": 59,
        "medium_purple4": 60,
        "slate_blue3": 62,
        "royal_blue1": 63,
        "chartreuse4": 64,
        "dark_sea_green4": 71,
        "pale_turquoise4": 66,
        "steel_blue": 67,
        "steel_blue3": 68,
        "cornflower_blue": 69,
        "chartreuse3": 76,
        "cadet_blue": 73,
        "sky_blue3": 74,
        "steel_blue1": 81,
        "pale_green3": 114,
        "sea_green3": 78,
        "aquamarine3": 79,
        "medium_turquoise": 80,
        "chartreuse2": 112,
        "sea_green2": 83,
        "sea_green1": 85,
        "aquamarine1": 122,
        "dark_slate_gray2": 87,
        "dark_magenta": 91,
        "dark_violet": 128,
        "purple": 129,
        "light_pink4": 95,
        "plum4": 96,
        "medium_purple3": 98,
        "slate_blue1": 99,
        "yellow4": 106,
        "wheat4": 101,
        "grey53": 102,
        "gray53": 102,
        "light_slate_grey": 103,
        "light_slate_gray": 103,
        "medium_purple": 104,
        "light_slate_blue": 105,
        "dark_olive_green3": 149,
        "dark_sea_green": 108,
        "light_sky_blue3": 110,
        "sky_blue2": 111,
        "dark_sea_green3": 150,
        "dark_slate_gray3": 116,
        "sky_blue1": 117,
        "chartreuse1": 118,
        "light_green": 120,
        "pale_green1": 156,
        "dark_slate_gray1": 123,
        "red3": 160,
        "medium_violet_red": 126,
        "magenta3": 164,
        "dark_orange3": 166,
        "indian_red": 167,
        "hot_pink3": 168,
        "medium_orchid3": 133,
        "medium_orchid": 134,
        "medium_purple2": 140,
        "dark_goldenrod": 136,
        "light_salmon3": 173,
        "rosy_brown": 138,
        "grey63": 139,
        "gray63": 139,
        "medium_purple1": 141,
        "gold3": 178,
        "dark_khaki": 143,
        "navajo_white3": 144,
        "grey69": 145,
        "gray69": 145,
        "light_steel_blue3": 146,
        "light_steel_blue": 147,
        "yellow3": 184,
        "dark_sea_green2": 157,
        "light_cyan3": 152,
        "light_sky_blue1": 153,
        "green_yellow": 154,
        "dark_olive_green2": 155,
        "dark_sea_green1": 193,
        "pale_turquoise1": 159,
        "deep_pink3": 162,
        "magenta2": 200,
        "hot_pink2": 169,
        "orchid": 170,
        "medium_orchid1": 207,
        "orange3": 172,
        "light_pink3": 174,
        "pink3": 175,
        "plum3": 176,
        "violet": 177,
        "light_goldenrod3": 179,
        "tan": 180,
        "misty_rose3": 181,
        "thistle3": 182,
        "plum2": 183,
        "khaki3": 185,
        "light_goldenrod2": 222,
        "light_yellow3": 187,
        "grey84": 188,
        "gray84": 188,
        "light_steel_blue1": 189,
        "yellow2": 190,
        "dark_olive_green1": 192,
        "honeydew2": 194,
        "light_cyan1": 195,
        "red1": 196,
        "deep_pink2": 197,
        "deep_pink1": 199,
        "magenta1": 201,
        "orange_red1": 202,
        "indian_red1": 204,
        "hot_pink": 206,
        "dark_orange": 208,
        "salmon1": 209,
        "light_coral": 210,
        "pale_violet_red1": 211,
        "orchid2": 212,
        "orchid1": 213,
        "orange1": 214,
        "sandy_brown": 215,
        "light_salmon1": 216,
        "light_pink1": 217,
        "pink1": 218,
        "plum1": 219,
        "gold1": 220,
        "navajo_white1": 223,
        "misty_rose1": 224,
        "thistle1": 225,
        "yellow1": 226,
        "light_goldenrod1": 227,
        "khaki1": 228,
        "wheat1": 229,
        "cornsilk1": 230,
        "grey100": 231,
        "gray100": 231,
        "grey3": 232,
        "gray3": 232,
        "grey7": 233,
        "gray7": 233,
        "grey11": 234,
        "gray11": 234,
        "grey15": 235,
        "gray15": 235,
        "grey19": 236,
        "gray19": 236,
        "grey23": 237,
        "gray23": 237,
        "grey27": 238,
        "gray27": 238,
        "grey30": 239,
        "gray30": 239,
        "grey35": 240,
        "gray35": 240,
        "grey39": 241,
        "gray39": 241,
        "grey42": 242,
        "gray42": 242,
        "grey46": 243,
        "gray46": 243,
        "grey50": 244,
        "gray50": 244,
        "grey54": 245,
        "gray54": 245,
        "grey58": 246,
        "gray58": 246,
        "grey62": 247,
        "gray62": 247,
        "grey66": 248,
        "gray66": 248,
        "grey70": 249,
        "gray70": 249,
        "grey74": 250,
        "gray74": 250,
        "grey78": 251,
        "gray78": 251,
        "grey82": 252,
        "gray82": 252,
        "grey85": 253,
        "gray85": 253,
        "grey89": 254,
        "gray89": 254,
        "grey93": 255,
        "gray93": 255,
    }
    return COLORS_ANSI


# Generate the ANSI dictionaries
ANSI_COLORS = get_ansi_colors()
ANSI_NUMBERS = ANSI_COLORS.keys()
COLORS_ANSI = get_colors_ansi()
W3_COLORS = COLORS_ANSI.keys()


def hex_to_rgb(hex: str) -> Tuple:
    """
    Convert a hex color to rgb.
    Args:
        hex (str): The hex color.
    Returns:
        rgb (tuple): The rgb color.
    """
    if HEX_REGEX.match(hex):
        rgb = []
        for i in (0, 2, 4):
            decimal = int(hex[i : i + 2], 16)
            rgb.append(decimal)
        return tuple(rgb)
    else:
        raise InvalidHexColor(f"Invalid hex color: {hex}")


def rgb_to_hex(rgb: Tuple[int, int, int]) -> str:
    """Convert an rgb color to hex."""
    r, g, b = rgb

    return ("{:X}{:X}{:X}").format(r, g, b)


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


def random_color_index(color_stops: int = 3, random_invert: bool = False, invert: bool = False, test: bool = False) -> list[int]:
    """Generate a random color range from the named colors.

    Args:
        color_stops (`int`): Then number of colors in the random gradient.

    Returns:
        `list[tuple]`: The list of rgb tuples from which to make the gradient.
    """
    # Initialize list of colors.
    all_colors = _all_colors()

    color_indexes = []

    # Randomly select starting color of the gradient
    start = random.choice(all_colors) # color
    start_index = all_colors.index(start) # color index
    # yield start_index
    indexes = [start_index]

    # Whether to randomly invert gradient
    if random_invert:
        invert = random.choice([True, False])
    else:
        invert = invert
    if test:
        table = Table(title="Index Start", show_lines=True, show_edge=True, border_style='bold #ff00ff', width=40)
        table.add_column("[bold #00ffff]Key[/]", justify='left', ratio=1)
        table.add_column("[bold #00ffff]Value[/]", justify='center', ratio=1)
        table.add_row("Start", f"{start}")
        table.add_row("Start_Index", f"{start_index}")
        table.add_row("Invert Gradient", f"{invert}")

        console.clear()
        console.print('\n\n')
        console.print(table, justify='center')
        console.print('\n\n')
    
    for x in range(1,color_stops+1):
        if invert:
            _next_index = start_index - x
            next_index = __validate_next_index(_next_index)
            # yield next_index
            indexes.append(next_index)
        else:
            _next_index = start_index + x
            next_index = __validate_next_index(_next_index)
            # yield next_index
            indexes.append(next_index)
        if test:
            console.print(f"Color Range: {color_indexes}", justify='center')

    return indexes



def random_color_range(range_type: str = 'rgb', color_stops: int = 3, random_invert: bool = True, invert: bool = False, test: bool = False) -> list[str|tuple]:
    """Generate a random color range from named colors, hex colors, or rgb tuples.

    Args:
        range_type (`str`): The type of color code you would like a random color range made from. Valid strings are `color`, `hex`, and `rgb`.
        color_stops (`int`): Then number of colors in the random gradient. Defaults to `3`.
        random_invert (`bool`): Whether or not the gradient is inverted randomly. Defaults to True.
        invert (`bool`): The direction the random gradient travels. `random_invert` must be `False` for this arg to have any function.
        test(`bool`): Whether or not this function is being run as a test.

    Returns:
        `list[str|tuple]`: The list of colors, hex colors, or rgb tuples from which to make the gradient.
    """
    color_indexes = random_color_index(color_stops=color_stops, random_invert=random_invert, invert=invert, test=test)
    if test:
        console.print(f"Color Indexes: {color_indexes}")
    
    gradient_colors = []
    # colors = []
    match range_type:
        case 'color':
            colors = _all_colors()
            for index in color_indexes:
                gradient_colors.append(colors[index])

            if test:
                console.print(f"Color Range Type: {range_type}")
                console.print(f"Colors: {', '.join(colors)}")
    
            return colors


        case 'hex':
            colors = _hex_colors()
            for index in color_indexes:
                gradient_colors.append(colors[index])

            if test:
                console.print(f"Color Range Type: {range_type}")
                console.print(f"Colors: {', '.join(colors)}")
    
            return colors


        case 'rgb':
            colors = _rgb_tuples()
            for index in color_indexes:
                gradient_colors.append(colors[index])

            if test:
                console.print(f"Color Range Type: {range_type}")
                console.print(f"Colors: {', '.join(colors)}")
    
            return colors
    


def __validate_range_input(start: str, end: str, test: bool = False) -> str:
    """Validate the start and end color of the gradient.

    Args:
        start(`str`): The color with which to begin the gradient.
        end (`end`): The color with which to end the gradient.

    Returns:
        `bool`: Returns `True` if valid.
    """
    all_colors = _all_colors()
    hex_colors = _hex_colors()
    rgb_tuples = _rgb_tuples()

    # Validate args
    mode1, mode2 = None, None
    for x, _ in enumerate([start, end], start=1):
        if x in all_colors:
            if x == 1:
                mode1 = "color"
            else:
                mode2 = "color"
        elif x in hex_colors:
            if x == 1:
                mode1 = "hex"
            else:
                mode2 = "hex"
        elif x in rgb_tuples:
            if x == 1:
                mode1 = "rgb"
            else:
                mode2 = "rgb"

        elif x == None:
            raise ColorParseError(
                f"Unable to make a gradient when not provided with a start and end color. \n\tStart: {start}\n\tEnd: {end}"
            )
        else:
            raise ColorParseError(
                f"Unable to parse start color of gradient for color_range. Value: {x}"
            )

    if mode1 != mode2:
        raise ColorParseError(
            f"Unable to correctly set mode. Mode1: {mode1}\tMode2: {mode2}\n\tStart: {start}\n\tEnd: {end}"
        )
    else:
        if test:
            console.print(f"Mode Determined: {mode1}")
        
        return mode1

def __validate_color_start_index(start_index: int, test: bool = False) -> int|None:
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
        raise ColorParseError(f"Starting Index Invalid: {start_index}\n\n\tMust be less that {all_indexes}")
    elif start_index < 0:
        raise ColorParseError(f"Starting Index Invalid: {start_index}\n\n\tMust be grater than zero.")
    else:
        if test:
            console.print(
                f"Validated `start_index`: {start_index}"
            )
        return start_index
    
def __validate_color_end_index(end_index: int, test: bool = False) -> int|None:
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
        raise ColorParseError(f"Ending Index Invalid: {end_index}\n\n\tMust be less that {all_indexes}")
    elif end_index < 0:
        raise ColorParseError(f"Ending Index Invalid: {end_index}\n\n\tMust be grater than zero.")
    else:
        if test:
            console.print(
                f"Validated `start_index`: {end_index}"
            )
        return end_index

def __validate_next_index(next_index: int, test:bool = False) -> int|None:
    """Validate the next color index.

    Args:
        next_index ('int'): The next color index for the color range.
        test (`bool`, optional): Whether to print the validation to the console. Defaults to False.

    Returns:
        int|None: The valid next index.

    Raises:
        ValueError: If the next_index is greater than len(colors) or less than zero.
    """
    all_indexes = len(_all_colors())
    if next_index > all_indexes:
        next_index = next_index - all_indexes
        if test:
            console.print(
                f'Next Index: {next_index} Validated'
            )
    elif next_index < 0:
        next_index = next_index + all_indexes
        if test:
            console.print(
                f'Next Index: {next_index} Validated'
            )
    elif next_index in range(0,10):
        if test:
            console.print(
                f'Next Index: {next_index} Validated'
            )
        return next_index
    else:
        raise ValueError(f"Invalid Next Index: {next_index}. Next Index must fall in between zero and nine.")


def color_range_generator(colors: list[str|tuple], start_index: int, end_index: int, invert: bool = False, test: bool = False) -> list[int]:
    """Generate the sequence of color from the `start_index`, to the `end_index` traversing the spectrum in the indicated direction.
    
    Args:
        colors (`list[str|tuple]`): The spectrum of colors that the input colors are a part of (Named_colors, HEX_colors, or RGB Tuples).
        start_index (`int`): The index to begin the gradient with.
        end_index (`int`): Then index to end the gradient with.
        invert (`bool`): Which direction on the spectrum to travel in. Defaults to `False` (positively).

    Returns:
        `list[int]`: The list of color indexes from which to generate a gradient.
    """
    # Validation
    start_index = __validate_color_start_index(start_index, test)
    end_index = __validate_color_end_index(end_index, test)
    
    # Start
    yield colors[start_index]
    
    # Determine Stop iteration conditions
    if invert:
        stop_index = end_index + 1
        if stop_index > len(colors):
            stop_index -= len(colors)
        
        step = -1
    else:
        stop_index = end_index - 1
        if stop_index < 0:
            stop_index += len(colors)
    
        step = 1

    next_index = start_index
    num_of_steps = 0
    while next_index != stop_index:
        num_of_steps += 1 # Color Stop Count
        distance = num_of_steps * step # range inverted/not
        _next_index = start_index + distance # Possible next index
        next_index = __validate_next_index(_next_index, test) # Validated next index
        if test:
            console.print(
                Panel(
                    f"Validated next_index: {next_index}\n\n\tNext color: {colors[next_index]}",
                    title='[bold #00ffff]Color Range Generator[/]',
                    title_align='left',
                    subtitle=f"[italic #0000ff]maxcolor.py[/][bold #249df1] | [/][dim]Line 875",
                    expand=False
                ),
                justify='center',
            )
        yield colors[next_index]
        




def generate_color_range(start: str, end: str, invert: bool = False, test: bool = False) -> list[tuple]:
    """Generate a dist of strings or tuples from the start color to the end color.

    Args:
        start(`str`): The color with which to start the color gradient.
        end(`str`): The color with which to end the color gradient.

    Returns:
        `dict[str:list[str|tuple]]`: A dict of the translations of the gradient to be made.
    """
    # Generate color lists
    all_colors = _all_colors()
    hex_colors = _hex_colors()
    rgb_tuples = _rgb_tuples()

    # Allocate and initialize ranges
    color_range_indexes = []
    color_range = []

    # Mode
    colors = []
    mode = __validate_range_input(start,end,True)
    match mode:
        case "color":
            colors = all_colors
            if test:
                console.print(f"Generating gradient from {mode} colors: {', '.join(colors)}")
        case "hex":
            colors = hex_colors
            if test:
                console.print(f"Generating gradient from {mode} colors: {', '.join(colors)}")
        case "rgb":
            colors = rgb_tuples
            if test:
                console.print(f"Generating gradient from {mode} colors: {', '.join(colors)}")
        case _:
            raise ColorParseError(
                f"Unable to determine mode: {mode}\n\tStart: {start}\n\tEnd: {end}"
            )

    # start index
    start_index = __validate_color_start_index(colors.index(start), True)
    color_range_indexes.append(start_index)
    color_range.append(colors[start_index])

    # end index
    end_index = colors.index(end)

    if invert:
        end = end_index + 1
        operator = '-'
        condition = "x < 0"

    # range inverted
    if invert:
        z = 0
        while x != end_index + 1:  # type: ignore
            z += 1
            next_index = start_index - z
            if x < 0:  # type: ignore
                next_index += 10
            color_range_indexes.append(next_index)
            color_range.append(colors[next_index])
            if test:
                console.print(
                    f"\n\n{z} random index: {', '.join(color_range_indexes)}\n{z} inverted colors: {', '.join(color_range)}"
                )

    # range
    else:
        z = 0
        while x != end_index - 1:  # type: ignore
            z += 1
            next_index = start_index + z
            if x > len(colors):  # type: ignore
                next_index -= len(colors)
            color_range_indexes.append(next_index)
            color_range.append(colors[next_index])
            if test:
                console.print(
                    f"\n\n{z} index: {', '.join(color_range_indexes)}\n{z} colors: {', '.join(color_range)}"
                )
    if test:
        console.print(f"Finished Generating Color Range!\n\n\tInvert: {invert}\n\tColor Range: {', '.join(color_range)}"
    )
    
    return color_range

def _pretty_rgb(rgb: Tuple[int,int,int])-> Text:
    """Generate a colored, formatted rich.Text object from a tuple of integers.
    
    Args:
        rgb (`tuple[int,int,int]`): A tuple representing an rgb color.

    Returns:
        `Text`: A rich.Text formatted and colored string.
    """

    red, green, blue = tuple(rgb)
    red_string = f"[#ffffff on #ff0000]{red:>3}"
    green_string = f"[#000000 on #00ff00]{green:>3}"
    blue_string = f"[#ffffff on #0000ff]{blue:>3}"
    left_parenthesis = f"[#ffffff]([/]"
    comma = f"[#fffffd], [/]"
    right__parenthesis = f"[#ffffff])[/]"
    text = f"{left_parenthesis}{red_string}{comma}{green_string}{comma}{blue_string}{right__parenthesis}"
    # console.print(text, markup=True)
    return text



def gradient(
    message: str | Text,
    random: bool = True,
    color_stops: int = 3,
    justify_text: JustifyMethod = "left",
    start: Optional[str | tuple] = None,
    end: Optional[str | tuple] = None,
    invert: bool = False,
    test: bool = False) -> Text:
    """Generate a gradient text.

    Args:
        message (str): The message to be gradiented.
        random (`bool`): Whether the gradient is random colors. Defaults to `True`.
        color_stops (Optional[]): The number of gradients to use. Defaults to 3.
        justify_text (`Optional[JustifyMethod]`) The alignment of the text. Can be 'left', 'center',or 'right'. Defaults to 'left'.
        start (`Optional[str|tuple]`): If arg named_gradient is set to `True` start becomes a required value to start the gradient off. Valid values are {', '.join(_all_colors)}, {', '.join(_hex_colors)}, {', '.join(_rgb_tuples)}
        end (`Optional[str|tuple]`): If arg named_gradient is set to `True` end becomes a required value to end the gradient with. Valid values are {', '.join(_all_colors)}, {', '.join(_hex_colors)}, {', '.join(_rgb_tuples)}
        invert (`Optional[bool]`): Which direction to traverse the spectrum. Default to False.
        test (`test`): Whether the function is being run to test it or not. Defaults to `False`.

    Returns:
        Text: The gradiented text.
    """
    all_colors = _all_colors()
    rgb_tuples = _rgb_tuples()

    # Message metadata
    size = len(message)
    gradient_size = size // (len(all_colors) - 1)
    if test:
        table = Table(show_lines=True, show_edge=True,header_style='bold italic #00ffff')
        table.add_column("Key", justify='left')
        table.add_column("Value", justify= 'center')
        table.add_row()
    gradient_text = Text()
    text = Text(message, justify=justify_text)

    # Generate Color Range
    if not random:
        if test:
            console.print(f"Generating Gradient...")
        
        color_dict = generate_color_range(start, end, invert)
        console.print(
            Panel(
                Pretty(
                    color_dict
                ),
                title=GRADIENT,
                title_align='left',
                subtitle='Named Gradient',
                subtitle_align='right',
                width=80
            ),
            justify='center'
        )
        color_range = list(color_dict["rgb"])
        color_range_indexes = color_dict["indexes"]
    else:
        console.print(f"Generating Random Gradient")
        color_dict = random_color_range(color_stops)
        rgb_strings = Text()
        for rgb in color_dict['rgb']:
            rgb_text = _pretty_rgb(tuple(rgb))
            rgb_strings.assemble(rgb_strings, rgb_text)
        indexes = Text()
        for index in color_dict['indexes']:
            sub_string = f"{index:^3}"
            indexes = Text.assemble(indexes, sub_string)
        # log_group = Columns(
        #     Panel(
        #         ",\n".join(color_dict["colors"]),
        #         title=f"[bold][#ff0000]C[/][#ff9100]o[/][#fffb00]l[/][#00ff00]o[/][#00ffff]r[/][#0000ff]s[/][/bold]",
        #         expand=False,
        #         subtitle=f"[italic][#ff0000]L[/][#ff9100]in[/][#fffb00]e[/][#00ff00] 8[/][#00ffff]#5[/][#0000ff]45[/][/italic]",
        #         border_style="bold bright_white"
        #     ),
        #     Panel(
        #         rgb_strings,
        #         title=f"[bold][#ff0000]R[/][#ff9100]G[/][#fffb00]B[/][#00ff00] Co[/][#00ffff]lo[/][#0000ff]rs[/][/bold]",
        #         expand=False,
        #         subtitle=f"[italic][#ff0000]L[/][#ff9100]in[/][#fffb00]e[/][#00ff00] 8[/][#00ffff]5[/][#0000ff]1[/][/italic]"
        #     ),
        #     Panel(
        #         indexes,
        #         title=f"[bold][#ff0000]I[/][#ff9100]n[/][#fffb00]d[/][#00ff00]e[/][#00ffff]x[/][#0000ff]es[/][/bold]",
        #         expand=False,
        #         subtitle=f"[bold][#ff0000]L[/][#ff9100]in[/][#fffb00]e[/][#00ff00] 8[/][#00ffff]5[/][#0000ff]7[/][/bold]"
        #     )
        # )
        # console.print(
        #     Panel(
        #         log_group,
        #         title=GRADIENT,
        #         title_align='left',
        #         subtitle='Random Gradient',
        #         subtitle_align='right',
        #         width=80
        #     ),
        #     justify='center'
        # )
        color_range = list(color_dict["rgb"])
        color_range_indexes = color_dict["indexes"]

    # Generate substrings
    for index, rgb in enumerate(color_range):

        # Get substring
        begin = index * gradient_size
        finish = begin + gradient_size
        sub_string = text[begin:finish]

        if index < len(color_range):
            # Color1
            color1_range_index = color_range.index(
                rgb
            )  # determines the position in the color_range
            color1 = tuple(rgb)  # Retrieves that color from the color_range
            if color1 != None:  # Ensures retrieved color is not `None`
                (
                    r1,
                    b1,
                    g1,
                ) = color1  # Parses the red, blue, and green components from the rgb tuple
            else:
                raise ColorParseError(
                    f"Unable to parse color1: {color1}\n\tcolor_range_idex: {index}\n\tColor Range: {', '.join(color_range)}"
                )

            # Color2
            try:
                color2_range_index = (color1_range_index + 1)  # Determines the next color's index in the color_range
                color2 = tuple(color_range[color2_range_index])
            except IndexError as ie:
                rgb_range_index = rgb_tuples.index(color1)
                if invert:
                    color2 = tuple(rgb_tuples[rgb_range_index-1])
                else:
                    color2 = tuple(rgb_tuples[rgb_range_index+1])
                    
            if color2 != None:  # Ensures retrieved color is not `None`
                (
                    r2,
                    b2,
                    g2,
                ) = color2  # Parses the red, blue, and green components from the next rgb tuple
            else:
                raise ColorParseError(
                    f"Unable to parse color2: {color2}\n\tcolor_range_idex: {index}\n\tColor Range: {', '.join(color_range)}"
                )

            # Color Delta
            dr = r2 - r1
            dg = g2 - g1
            db = b2 - b1

        # Blend Color1 & Color2 and apple style to substring
        for index in range(gradient_size):
            blend = index / gradient_size
            color = f"#{int(r1 + dr * blend):02X}{int(g1 + dg * blend):02X}{int(b1 + db * blend):02X}"  # type: ignore
            sub_string.stylize(color, index, index + 1)

        # Concatenate the styled substring
        gradient_text = Text.assemble(gradient_text, sub_string, justify=justify_text)

    return gradient_text


if __name__ == "__main__":
    console.print(
        gradient(
            "Ad tempor dolore laborum aute. Excepteur do aliquip ex qui sit qui. Incididunt ea sit id excepteur duis dolore. Ipsum velit occaecat ut sint commodo ea ex. Culpa duis officia tempor ipsum reprehenderit veniam duis ullamco est non adipisicing mollit consequat excepteur. Anim cillum deserunt aliquip eiusmod tempor dolore voluptate aute in aliqua nisi proident. Sit culpa id ea in. Ad tempor dolore laborum aute. Excepteur do aliquip ex qui sit qui. Incididunt ea sit id excepteur duis dolore. Ipsum velit occaecat ut sint commodo ea ex. Culpa duis officia tempor ipsum reprehenderit veniam duis ullamco est non adipisicing mollit consequat excepteur. Anim cillum deserunt aliquip eiusmod tempor dolore voluptate aute in aliqua nisi proident. Sit culpa id ea in. Ad tempor dolore laborum aute. Excepteur do aliquip ex qui sit qui. Incididunt ea sit id excepteur duis dolore. Ipsum velit occaecat ut sint commodo ea ex. Culpa duis officia tempor ipsum reprehenderit veniam duis ullamco est non adipisicing mollit consequat excepteur. Anim cillum deserunt aliquip eiusmod tempor dolore voluptate aute in aliqua nisi proident. Sit culpa id ea in.\nn\Ad sint sit laborum laborum ipsum dolor mollit occaecat elit sit id nostrud nostrud. Esse sit incididunt officia amet. Veniam adipisicing ipsum laboris nisi laborum amet. Eiusmod elit enim qui in ea aute commodo officia ea id duis do. Culpa laborum do sint ut occaecat esse voluptate. Id elit proident consequat magna et. Velit nisi commodo non ut dolor dolore aliqua. Ipsum voluptate aliquip ipsum."
        )
    )


# def gradient_backup(
#     gradient_size: int,
#     all_colors: list[str] = _all_colors(),
#     hex_colors: list[str] = _hex_colors(),
#     rgb_tuples: list[tuple] = _rgb_tuples(),
# ):
#     # Generate substrings
#     for index, color_name in enumerate(all_colors, start=0):
#         color_index = all_colors.index(color_name)
#         hex = hex_colors[color_index]
#         rgb = rgb_tuples[color_index]

#         # Get substring
#         begin = index * gradient_size
#         end = begin + gradient_size
#         sub_string = text[begin:end]
#         if index < len(all_colors):
#             color1_tuple = tuple(rgb_tuples[color_index - 1])
#             # color1_tuple = color1.triplet
#             if color1_tuple != None:
#                 r1, b1, g1 = color1_tuple
#             else:
#                 raise ColorParseError(
#                     f"Unable to parse color1: {color1}\t\tcolor_tuple: {color1_tuple}"
#                 )
#             color2_tuple = tuple(rgb_tuples[color_index])
#             if color2_tuple != None:
#                 r2, b2, g2 = color2_tuple
#             else:
#                 raise ColorParseError(
#                     f"Unable to parse color2: {color2}\t\tcolor_tuple: {color2_tuple}"
#                 )
#             dr = r2 - r1
#             dg = g2 - g1
#             db = b2 - b1
#         for index in range(gradient_size):
#             blend = index / gradient_size
#             color = f"#{int(r1 + dr * blend):02X}{int(g1 + dg * blend):02X}{int(b1 + db * blend):02X}"  # type: ignore
#             sub_string.stylize(color, index, index + 1)
#         gradient_text = Text.assemble(gradient_text, sub_string, justify=justify_text)

#     return gradient_text


# ────────────────────── Gradient Color Functions────────────────────────
def not_gradient(
    message: str | Text,
    num_of_gradients: int = 3,
    justify: Optional[JustifyMethod] = "left",
) -> Text:
    """Generate a gradient text.
    Args:
        message (str): The message to be gradiented.
        num_of_gradients (int, optional): The number of gradients to use. Defaults to 3.
        justify (Optional[JustifyMethod], optional): The justification of the text. Defaults to "left".
    Returns:
        Text: The gradiented text.
    """
    all_colors = [
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
    if num_of_gradients > len(all_colors):
        raise ValueError(
            f"Number of gradients must be less than or equal to {len(all_colors)}."
        )
    # Set Justification Method for Tet
    text = Text(message, justify=justify)  # type: ignore
    # Get the length of the message
    size = len(message)

    # , Select starting color
    color = random.choice(all_colors)
    chosen_index = all_colors.index(color)  # Get index of chosen color
    color_indexes = [chosen_index]  # Add chosen index to list of indexes
    # console.log(f"Chosen Index: {chosen_index}")  # Log chosen index

    # , Get the indexes of the other colors
    for i in range(1, num_of_gradients + 1):
        next_index = chosen_index + i
        if next_index > len(all_colors):
            next_index = next_index - len(all_colors)
        color_indexes.append(next_index)  # type: ignore
    # console.log(f"Color Indexes: {color_indexes}")

    # , Get the colors for the gradient
    color_range = []  # type: ignore
    for x, i in enumerate(color_indexes):
        next_color = all_colors[i - 1]
        color_range.append(next_color)

    # Determine the size of the gradient
    gradient_size = size // (num_of_gradients - 1)
    gradient_text = Text()

    # , Determine the substring for each gradient
    for index in range(0, num_of_gradients):
        begin = index * gradient_size
        end = begin + gradient_size
        sub_string = text[begin:end]

        if index < num_of_gradients:
            color1 = Color.parse(color_range[index])
            color1_triplet = color1.triplet
            r1 = color1_triplet[0]  # type: ignore
            g1 = color1_triplet[1]  # type: ignore
            b1 = color1_triplet[2]  # type: ignore
            color2 = Color.parse(color_range[index + 1])
            color2_triplet = color2.triplet
            r2 = color2_triplet[0]  # type: ignore
            g2 = color2_triplet[1]  # type: ignore
            b2 = color2_triplet[2]  # type: ignore
            dr = r2 - r1
            dg = g2 - g1
            db = b2 - b1

        # Apply the gradient to each character
        for index in range(gradient_size):
            blend = index / gradient_size
            color = f"#{int(r1 + dr * blend):02X}{int(g1 + dg * blend):02X}{int(b1 + db * blend):02X}"  # type: ignore
            sub_string.stylize(color, index, index + 1)

        gradient_text = Text.assemble(gradient_text, sub_string, justify=justify)

    return gradient_text


def rainbow(message: str, justify: JustifyMethod = "left") -> Text:
    """Generate a rainbow text.
    Args:
        message (str): The message to be rainbowed.
        justify (JustifyMethod, optional): The justification method. Defaults to "left".
    Returns:
        Text: The rainbowed text.
    """
    return gradient(message, num_of_gradients=10, justify=justify)


def gradient_panel(
    message: RenderableType,
    box: Box = ROUNDED,
    title: Optional[TextType] = None,
    title_align: AlignMethod = "center",
    gradient_title: bool = True,
    subtitle: Optional[TextType] = None,
    subtitle_align: AlignMethod = "right",
    expand: bool = True,
    border_style: StyleType = "bold #ffffff",
    width: Optional[int] = None,
    height: Optional[int] = None,
    padding: PaddingDimensions = (0, 1),
    num_of_gradients: int = 3,
    justify_text: JustifyMethod = "left",
) -> Panel:
    """
    Generate a gradient panel.
    Args:
        message (RenderableType): The message to be gradiented.
        box (Box, optional): The box style. Defaults to ROUNDED.
        title (Optional[TextType], optional): The title of the panel. Defaults to None.
        title_align (AlignMethod, optional): The alignment of the title. Defaults to "center".
        subtitle (Optional[TextType], optional): The subtitle of the panel. Defaults to None.
        subtitle_align (AlignMethod, optional): The alignment of the subtitle. Defaults to "right".
        expand (bool, optional): Whether to expand the panel. Defaults to True.
        border_style (StyleType, optional): The border style. Defaults to "bold #ffffff".
        width (Optional[int], optional): The width of the panel. Defaults to None.
        height (Optional[int], optional): The height of the panel. Defaults to None.
        padding (PaddingDimensions, optional): The padding of the panel. Defaults to (0, 1).
        num_of_gradients (int, optional): The number of gradients to use. Defaults to 3.
        justify_text (JustifyMethod, optional): The justification method. Defaults to "left".
    Returns:
        Panel: The gradiented panel.
    """
    all_colors = [
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
    if num_of_gradients > len(all_colors):
        raise ValueError(
            f"Number of gradients must be less than or equal to {len(all_colors)}."
        )
    # Set Justification Method for Tet
    text = Text(message, justify=justify_text)  # type: ignore
    # Get the length of the message
    size = len(text)

    # , Select starting color
    color = random.choice(all_colors)
    chosen_index = all_colors.index(color)  # Get index of chosen color
    color_indexes = [chosen_index]  # Add chosen index to list of indexes
    # console.log(f"Chosen Index: {chosen_index}")  # Log chosen index

    # , Get the indexes of the other colors
    for i in range(1, num_of_gradients + 1):
        next_index = chosen_index + i
        if next_index > len(all_colors):
            next_index = next_index - len(all_colors)
        color_indexes.append(next_index)  # type: ignore
    # console.log(f"Color Indexes: {color_indexes}")

    # , Get the colors for the gradient
    color_range = []  # type: ignore
    for x, i in enumerate(color_indexes):
        next_color = all_colors[i - 1]
        color_range.append(next_color)

    # Determine the size of the gradient
    gradient_size = size // (num_of_gradients - 1)
    gradient_text = Text()

    # , Determine the substring for each gradient
    for index in range(0, num_of_gradients):
        begin = index * gradient_size
        end = begin + gradient_size
        sub_string = text[begin:end]

        if index < num_of_gradients:
            color1 = Color.parse(color_range[index])
            color1_triplet = color1.triplet
            r1 = color1_triplet[0]  # type: ignore
            g1 = color1_triplet[1]  # type: ignore
            b1 = color1_triplet[2]  # type: ignore
            color2 = Color.parse(color_range[index + 1])
            color2_triplet = color2.triplet
            r2 = color2_triplet[0]  # type: ignore
            g2 = color2_triplet[1]  # type: ignore
            b2 = color2_triplet[2]  # type: ignore
            dr = r2 - r1
            dg = g2 - g1
            db = b2 - b1

        # Apply the gradient to each character
        for index in range(gradient_size):
            blend = index / gradient_size
            color = f"#{int(r1 + dr * blend):02X}{int(g1 + dg * blend):02X}{int(b1 + db * blend):02X}"  # type: ignore
            sub_string.stylize(color, index, index + 1)

        gradient_text = Text.assemble(gradient_text, sub_string, tab_size=4, justify=justify_text)  # type: ignore

    if gradient_title:
        panel_title = gradient(f"{title}")

        gradient_panel = Panel(
            gradient_text,
            box=box,
            title=panel_title,
            title_align=title_align,
            subtitle=subtitle,
            subtitle_align=subtitle_align,
            expand=expand,
            border_style=border_style,
            width=width,
            height=height,
            padding=padding,
        )
        return gradient_panel
    else:
        gradient_panel = Panel(
            gradient_text,
            box=box,
            title=f"[bold bright_white]{title}[/bold bright_white]",
            title_align=title_align,
            subtitle=subtitle,
            subtitle_align=subtitle_align,
            expand=expand,
            border_style=border_style,
            width=width,
            height=height,
            padding=padding,
        )
        return gradient_panel


def gradient_panel_demo():
    text = "\tEnim tempor veniam proident. Reprehenderit deserunt do duis laboris laborum consectetur fugiat deserunt officia officia eu consequat. Aute sint occaecat adipisicing eu aute. Eu est laborum enim deserunt fugiat nostrud officia do ad cupidatat enim amet cillum amet. Consectetur occaecat ex quis irure cupidatat amet occaecat ad sit adipisicing pariatur est velit mollit voluptate. Eiusmod deserunt nisi voluptate irure. Sunt irure consectetur veniam dolore elit officia et in labore esse esse cupidatat labore. Fugiat enim irure ipsum eiusmod consequat irure commodo cillum.\n\n\tReprehenderit ea quis aliqua qui labore enim consequat ea nostrud voluptate amet reprehenderit consequat sunt. Ad est occaecat mollit qui sit enim do esse aute sint nulla sint laborum. Voluptate veniam ut Lorem eiusmod id veniam amet ipsum labore incididunt. Ex in consequat voluptate mollit nisi incididunt pariatur ipsum ut eiusmod ut cupidatat elit. Eu irure est ad nulla exercitation. Esse elit tempor reprehenderit ipsum eu officia sint.\n\n\tCupidatat officia incididunt cupidatat minim fugiat sit exercitation ullamco occaecat est officia ut occaecat labore. Id consectetur cupidatat amet aute. Pariatur nostrud enim reprehenderit aliqua. Elit deserunt excepteur aute aliquip."
    console.print("\n\n")
    wide_panel = gradient_panel(
        text,
        title="Hello World",
        subtitle="The Cake is a Lie",
        num_of_gradients=5,
        justify_text="left",
        gradient_title=True,
    )
    left_panel = gradient_panel(
        text,
        title="Left Adjusted Title",
        gradient_title=True,
        width=80,
        expand=True,
        subtitle="[white]Optional Subtitle (one the left)[/]",
        subtitle_align="left",
    )
    console.print("\n\n")
    console.print(left_panel, justify="left")
    right_panel = gradient_panel(
        text,
        title="Wide Right Adjusted Title",
        title_align="right",
        gradient_title=True,
        width=120,
        expand=True,
        justify_text="right",
    )
    console.print("\n\n")
    console.print(right_panel, justify="right")
    center_panel = gradient_panel(
        text,
        title="[bold bright_white]Thin Centered Adjusted Title[/]",
        gradient_title=False,
        width=50,
        expand=True,
        justify_text="center",
        subtitle="[italic bright_white]The cake is a lie.[/]",
        subtitle_align="right",
    )
    console.print("\n\n")
    console.print(center_panel, justify="center")

    # text1 = "While the text is definitely gradient, the title doesn't have to be "
    # gradient_word = gradient("Gradient")
    # text2 = ". [bold bright_red]Nor does the other text have to be full [/][bold orange1]C[]/[bold bright_yellow]O[/][bold bright_green]L[/][bold bright_blue]O[/][bold purple1]R[/]. "
    # text3 = "So do whatever you feel, or just have gradient text in a panel. Just realize people might doubt your sexuality. But their insecure in theirs, already... so says more about them."
    # text = Text.assemble(text1, gradient_word,text2, text3)
    # full_panel = gradient_panel(
    #     text,
    #     title="Bold Bright_WHITE Title"
    # )


def demo():
    console.print("\n\n")
    console.print(gradient("Hello World", 4, "center"), justify="center")

    console.print("\n\n")

    console.print(
        gradient(
            "Sunt sit est labore elit ut laboris est. Aute cupidatat sit officia deserunt sint adipisicing et minim aliqua enim. Tempor eiusmod dolore excepteur dolore id aliquip enim incididunt ex. Non ipsum eu cillum proident ex. Officia deserunt consequat adipisicing est eiusmod nisi tempor aliquip proident ut in sunt nisi ullamco.\n\n"
        )
    )

    console.print(
        rainbow(
            "Sunt sit est labore elit ut laboris est. Aute cupidatat sit officia deserunt sint adipisicing et minim aliqua enim. Tempor eiusmod dolore excepteur dolore id aliquip enim incididunt ex. Non ipsum eu cillum proident ex. Officia deserunt consequat adipisicing est eiusmod nisi tempor aliquip proident ut in sunt nisi ullamco.\n\n"
        ),
        justify="left",
    )
    gradient(
        "Non aliquip ea proident aute duis exercitation esse commodo ut. Ad ad eiusmod aute ex culpa ex amet eiusmod aute dolore minim. Occaecat ullamco culpa adipisicing qui exercitation proident enim cupidatat anim fugiat consectetur magna. Officia ad sint proident tempor pariatur. Sint pariatur est commodo. Ex culpa in ut consequat ut elit sint."
    )
