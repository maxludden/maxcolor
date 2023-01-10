import random
import re
from enum import Enum
from typing import Optional, Tuple, Literal
from functools import lru_cache
from pathlib import Path

from maxconsole import MaxConsole
from rich import print
from rich.align import AlignMethod
from rich.box import ROUNDED, Box
from rich.color import Color, ColorParseError
from rich.console import JustifyMethod, RenderableType, Group
from rich.padding import PaddingDimensions
from rich.panel import Panel
from rich.style import StyleType
from rich.text import Text, TextType
from rich.table import Table
from functools import singledispatch

console = MaxConsole()

def _generate_color_dict() -> dict[dict[str:str|tuple|int]]:
    return {
        "magenta": {
            "name": "magenta",
            "hex": "#ff00ff",
            "rgb": (255, 0, 255),
            "index": 0,
            "next": "light_purple",
            "prev": "red",
            "next_index": 1,
            "prev_index": 9
        },
        "light_purple": {
            "name": "light_purple",
            "hex": "#af00ff",
            "rgb": (175,0,255),
            "index": 1,
            "next": "purple",
            "prev": "light_purple",
            "next_index": 2,
            "prev_index": 0
        },
        "purple": {
            "name": "purple",
            "hex": "#5f00ff",
            "rgb": (95,0,255),
            "index": 2,
            "next": "blue",
            "prev": "purple",
            "next_index": 3,
            "prev_index": 1
        },
        "blue": {
            "name": "blue",
            "hex": "#0000ff",
            "rgb": (0,0,255),
            "index": 3,
            "next": "light_blue",
            "prev": "purple",
            "next_index": 4,
            "prev_index": 2
        },
        "light_blue": {
            "name": "light_blue",
            "hex": "##249df1",
            "rgb": (36, 157, 241),
            "index": 4,
            "next": "cyan",
            "prev": "blue",
            "next_index": 5,
            "prev_index": 3
        },
        "cyan": {
            "name": "cyan",
            "hex": "#00ffff",
            "rgb": (0,255,255),
            "index": 5,
            "next": "green",
            "prev": "light_blue",
            "next_index": 6,
            "prev_index": 4
        },
        "green": {
            "name": "green",
            "hex": "#00ff00",
            "rgb": (0,255,0),
            "index": 6,
            "next": "light_purple",
            "prev": "cyan",
            "next_index": 7,
            "prev_index": 5
        },
        "yellow": {
            "name": "yellow",
            "hex": "#ffff00",
            "rgb": (255,255,0),
            "index": 7,
            "next": "orange",
            "prev": "green",
            "next_index": 8,
            "prev_index": 6
        },
        "orange": {
            "name": "orange",
            "hex": "#ff8800",
            "rgb": (255,128,0),
            "index": 8,
            "next": "red",
            "prev": "yellow",
            "next_index": 9,
            "prev_index": 7
        },
        "red": {
            "name": "red",
            "hex": "#ff0000",
            "rgb": (255, 0, 0),
            "index": 9,
            "next": "magenta",
            "prev": "orange",
            "next_index": 0,
            "prev_index": 8
        }
    }

class NamedColor(Color):
    """A color that is defined by a name."""
    name: str
    hex: str
    rgb: Tuple[int, int, int]
    index: int
    next: str
    prev: str
    next_index: int
    prev_index: int
    named_colors = {
        "magenta": {
            "name": "magenta",
            "hex": "#ff00ff",
            "rgb": (255, 0, 255),
            "index": 0,
            "next": "light_purple",
            "prev": "red",
            "next_index": 1,
            "prev_index": 9
        },
        "light_purple": {
            "name": "light_purple",
            "hex": "#af00ff",
            "rgb": (175,0,255),
            "index": 1,
            "next": "purple",
            "prev": "light_purple",
            "next_index": 2,
            "prev_index": 0
        },
        "purple": {
            "name": "purple",
            "hex": "#5f00ff",
            "rgb": (95,0,255),
            "index": 2,
            "next": "blue",
            "prev": "purple",
            "next_index": 3,
            "prev_index": 1
        },
        "blue": {
            "name": "blue",
            "hex": "#0000ff",
            "rgb": (0,0,255),
            "index": 3,
            "next": "light_blue",
            "prev": "purple",
            "next_index": 4,
            "prev_index": 2
        },
        "light_blue": {
            "name": "light_blue",
            "hex": "##249df1",
            "rgb": (36, 157, 241),
            "index": 4,
            "next": "cyan",
            "prev": "blue",
            "next_index": 5,
            "prev_index": 3
        },
        "cyan": {
            "name": "cyan",
            "hex": "#00ffff",
            "rgb": (0,255,255),
            "index": 5,
            "next": "green",
            "prev": "light_blue",
            "next_index": 6,
            "prev_index": 4
        },
        "green": {
            "name": "green",
            "hex": "#00ff00",
            "rgb": (0,255,0),
            "index": 6,
            "next": "light_purple",
            "prev": "cyan",
            "next_index": 7,
            "prev_index": 5
        },
        "yellow": {
            "name": "yellow",
            "hex": "#ffff00",
            "rgb": (255,255,0),
            "index": 7,
            "next": "orange",
            "prev": "green",
            "next_index": 8,
            "prev_index": 6
        },
        "orange": {
            "name": "orange",
            "hex": "#ff8800",
            "rgb": (255,128,0),
            "index": 8,
            "next": "red",
            "prev": "yellow",
            "next_index": 9,
            "prev_index": 7
        },
        "red": {
            "name": "red",
            "hex": "#ff0000",
            "rgb": (255, 0, 0),
            "index": 9,
            "next": "magenta",
            "prev": "orange",
            "next_index": 0,
            "prev_index": 8
        }
    }

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    @singledispatch()
    def named_color(self, arg):
        raise NotImplementedError(f"Base implementation of single dispatch function.")

    @named_color.register(str)
    def _(self, arg: str) -> NamedColor:

        # If initialized with named_color
        if args in self.named_colors.keys():
            name = arg,
            self.name = name
            self.hex = self.named_colors[name]['hex']
            self.rgb = self.named_colors[name]['rgb']
            self.index = self.named_colors[name]['index']
            self.next = self.named_colors[name]['next']
            self.prev = self.named_colors[name]['prev']
            self.next_index = self.named_colors[name]['next_index']
            self.prev_index = self.named_colors[name]['prev_index']

        # if initialized with HEX Color
        elif '#' in args:
            HEX_REGEX = re.compile(r"^\#([0-9a-fA-F]{6})$|^ ([0-9a-fA-F]{6})$", re.VERBOSE)
            match = re.match(HEX_REGEX, args)
            if match:
                group = match.group(1)
                if '#' in group:
                    hex = group
                else:
                    hex = f"#{group}"
        else:
            raise KeyError(f"Unable to parse color: {args}")
            
        
    @__init__.register
    def _(self, args: int):

        # If initialized with index
        if args in range (0, 10):
            for index, color in enumerate(self.named_colors):
                if args == index: # Verify against counter
                    # Validate against internal index value 
                    if self.named_colors[color]['index'] == args:
                        color = self.named_colors[color]
                        self.name = color['name']
                        self.hex = color['hex']
                        self.rgb = color['rgb']
                        self.index = color['index']
                        self.next = color['next']
                        self.prev = color['prev']
                        self.next_index = color['next_index']
                        self.prev_index = color['prev_index']
        else:
            raise ValueError(f"Unable to initialize NamedColor with an index that doesn't exist. Args type: Integer\n\tArgs: {args}")

    def __repr__(self) -> str:
        table = Table(show_header=True, header_style="bold #00c8ff", show_lines=True, style="bold #0091ff")),
        table.add_column("NamedColor", style='italic #e2e2e2')
        table.add_column("Parameter", style="bold #4363ff")
        table.add_row(f'Class', f'NamedColor')
        table.add_row(f'Name', f'{self.name}')
        table.add_row(f'RGB', f'{self.rgb}')
        table.add_row(f'Hex', f'{self.hex}')
        return table

    
    def __str__(self) -> str:
        return self.name

    def __rich__(self) -> RenderableType:
        """Render the color."""
        return Panel(
            Text(self.name, style=self.style),
            title=self.name,
            title_align=AlignMethod.CENTER,
            box=ROUNDED,
            padding=PaddingDimensions(1, 2),
            style=self.style
        )

    def _validate_named_color(self) -> bool:
        """Validate the color name."""
        if self.name in NamedColors.__members__:
            return True
        else:
            return False

    def _generate_hex(self) -> str:
        """Get the hex value of the color."""
        match self.name:
            case 'magenta':
                self.hex = '#ff00ff'
                return self.hex
            case 'light_purple':
                self.hex = '#af00ff'
                return self.hex
            case 'purple':
                self.hex = '#5f00ff'
                return self.hex
            case 'blue':
                self.hex = '#0000ff'
                return self.hex
            case 'light_blue':
                self.hex = '#249df1'
                return self.hex
            case 'cyan':
                self.hex = '#00ffff'
                return self.hex
            case 'green':
                self.hex = '#00ff00'
                return self.hex
            case 'yellow':
                self.hex =  '#ffff00'
                return self.hex
            case 'orange':
                self.hex = '#ff8000'
                return self.hex
            case 'red':
                self.hex = '#ff0000'
                return self.hex
            case _:
                raise ColorParseError(f'Invalid color name: {self.name}')


    def _generate_rgb(self) -> Tuple[int, int, int]:
        """Get the RGB value of the color."""
        match self.name:
            case 'magenta':
                self.rgb = (255, 0, 255)
                return self.rgb
            case 'light_purple':
                self.rgb = (175, 0, 255)
                return self.rgb
            case 'purple':
                self.rgb = (95, 0, 255)
                return self.rgb
            case 'blue':
                self.rgb = (0, 0, 255)
                return self.rgb
            case 'light_blue':
                self.rgb = (36, 157, 241)
                return self.rgb
            case 'cyan':
                self.rgb = (0, 255, 255)
                return self.rgb
            case 'green':
                self.rgb = (0, 255, 0)
                return self.rgb
            case 'yellow':
                self.rgb = (255, 255, 0)
                return self.rgb
            case 'orange':
                self.rgb = (255, 128, 0)
                return self.rgb
            case 'red':
                self.rgb = (255, 0, 0)
                return self.rgb
            case _:
                raise ColorParseError(f'Invalid color name: {self.name}')

    def _generate_style(self) -> StyleType:
        """Generate the style of the color."""
        self.style = f'{self.hex}'
        return self.style

    def _generate_color(self) -> None:
        """Generate the color."""
        self._generate_hex()
        self._generate_rgb()
        self._generate_style()

    def as_rgb(self) -> Tuple[int, int, int]:
        """Get the RGB value of the color."""
        if self.rgb is None:
            self._generate_color()
        
        return self.rgb
        

    def __rich_console__(
        self,
        console: "Console",
        options: "ConsoleOptions",
    ) -> RenderableType:
        """Render the color as a panel with the name of the color."""
        return Panel(
            Text(self.name, style=self.style),
            title=self.name,
            title_align=AlignMethod.CENTER,
            box=ROUNDED,
            padding=PaddingDimensions(1, 2),
            width=20,
            height=5,
        )

class NamedColor2(Enum):
    magenta = "magenta"
    light_purple = "light_purple",
    purple = "purple",
    blue = "blue",
    light_blue = "light_blue",
    cyan = "cyan",
    green = "green",
    yellow = "yellow",
    orange = "orange",
    red = "red"

    def get_index(self) -> int:
        match self:
            case "magenta":
                return 0
            case "light_purple":
                return 1
            case "purple":
                return 2
            case "blue":
                return 3
            case "light_blue":
                return 4
            case "cyan":
                return 5
            case "green":
                return 6
            case "yellow":
                return 7
            case "orange":
                return 8
            case "red":
                return 9
            case _:
                raise ColorParseError(f"Unable to retrieve index: {self} is not a named color.")
    
    def name(self) -> str:
        return super().name

    @classmethod
    def from_index(cls, index: int) -> str:
        match index:
            case 0:
                return NamedColor.magenta
            case 1:
                return NamedColor.light_purple
            case 2:
                return NamedColor.purple
            case 3:
                return NamedColor.blue
            case 4:
                return NamedColor.light_blue
            case 5:
                return NamedColor.cyan
            case 6:
                return NamedColor.green
            case 7:
                return NamedColor.yellow
            case 8:
                return NamedColor.orange
            case 9:
                return NamedColor.red


class HexColor(Enum):
    magenta = "#ff00ff"
    light_purple = "#af00ff"
    purple = "#5f00ff"
    blue = "#0000ff"
    light_blue = "#249df1"
    cyan = "#00ffff"
    green = "#00ff00"
    yellow = "#ffff00"
    orange = "#ff8800"
    red = "#ff0000"

class RgbTuple(Enum):
    magenta = (255, 0, 255)
    light_purple = (175, 0, 255)
    purple = (95, 0, 255)
    blue = (0, 0, 255)
    light_blue =  (36, 157, 241)
    cyan = (0, 255, 0)
    green = (0, 255, 0)
    yellow = (255, 255, 0)
    orange = (255, 128, 0)
    red = (255, 0, 0)

class RangeType(Enum):
    named = NamedColor
    hex = HexColor
    rgb = RgbTuple

class MaxColor(Color):
    name: NamedColor.name

    def Parse(self)

class ColorRange:
    start: NamedColor|HexColor|RgbTuple
    end:  NamedColor|HexColor|RgbTuple
    indexes = range(0, 9)
    start_index: int
    end_index: int

    def __init__(self, start: NamedColor|HexColor|RgbTuple, end:  NamedColor|HexColor|RgbTuple):
        self.start = start
        self.end = end
        if isinstance(start, NamedColor):
            start_index = NamedColor.get_index(start)
            case 

class chapter_gen:
    """
    Generator for chapter numbers.
    """

    def __init__(self, start: int = 1, end: int = 3462):
        self.start = start
        self.end = end
        self.chapter_number = start

    def __iter__(self):
        return self

    def __next__(self):
        if self.chapter_number >= 3462:
            raise StopIteration
        elif self.chapter_number == 3094:
            # Skipping chapter 3095
            # 3094 + 1 + 1 = 3096
            self.chapter_number += 2
            return self.chapter_number
        elif self.chapter_number == 3116:
            # Skipping chapter 3117
            # 3116 + 1 + 1 = 3118
            self.chapter_number += 2
            return self.chapter_number
        else:
            self.chapter_number += 1
            return self.chapter_number

    def __len__(self):
        return self.end - self.start + 1
