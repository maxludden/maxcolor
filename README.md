---
Title: README.md
Path: README.md
Author: Max Ludden
Date: 2022-10-31 7:28 AM EST
CSS: static/style.css
...

# maxcoler 0.6.0

Updated dependencies to work with the other helper packages: maxconsole and max progress.

# maxcolor 0.5.0

## Purpose

This is a collection of helper scripts to work with rich renderables.

<br />

## Features from Textualize/Rich:

<br />

- Provides a helper function to allow for rich to easily print gradient text.
- Provides a helper function to allow for rich to easily print a gradient text to a panel.

<br />

## Installation

<br />

#### Install from Pip

```Python
pip install maxcolor
```

<br />

#### Install from Pipx

```Python
pipx install maxcolor
```

<br />

#### Install from Pipx

```Python
python add maxcolor
```

<br />
<hr />
<br />

## Usage

<br />

The following are available to import from `maxcolor`:

### Color Regular Expressions

```Python
from maxcolor import HEX_REGEX, ANSI_REGEX, RGB_REGEX, COLOR_REGEX

hex_result = re.match(HEX_REGEX, "#FF0000")
ansi_result = re.match(ANSI_REGEX, "124")
rgb_result = re.match(RGB_REGEX, "255, 0, 0")
color_result = re.match(COLOR_REGEX, "#FF0000 123 255, 0, 0")
```

### Color Conversion Functions
```python
from maxcolor import hex_to_rgb, rgb_to_hex

rgb_color = hex_to_rgb("#FF0000") # (255, 0, 0)  # RGB tuple

hex_color = rgb_to_hex(255, 0, 0) # "#FF0000"  # Hex string
```

### Gradient Color Functions
```Python
from maxcolor import gradient, rainbow, gradient_panel

console = get_console(get_theme())

console.print(
    gradient("Hello World!")
)
```

![gradient.png](static/gradient.png)

The gradient function will allow you to print multicolor gradients colored text. THe gradient function takes a string, an optional number of colors (defaults to 4), and an optional justification (defaults to "left").

The rainbow function is simply a the gradient function with the maximum number of colors, 10. And since it spans the entire color spectrum, it's a great way to print a rain.
```Python
console.print(
    gradient(
        "Sunt sit est labore elit ut laboris est. Aute cupidatat sit officia deserunt sint adipisicing et minim aliqua enim. Tempor eiusmod dolore excepteur dolore id aliquip enim incididunt ex. Non ipsum eu cillum proident ex. Officia deserunt consequat adipisicing est eiusmod nisi tempor aliquip proident ut in sunt nisi ullamco."
    )
)
console.print(
    rainbow(
        "Sunt sit est labore elit ut laboris est. Aute cupidatat sit officia deserunt sint adipisicing et minim aliqua enim. Tempor eiusmod dolore excepteur dolore id aliquip enim incididunt ex. Non ipsum eu cillum proident ex. Officia deserunt consequat adipisicing est eiusmod nisi tempor aliquip proident ut in sunt nisi ullamco.\n\n"
    )
)
```

#### Gradient (top text)

<br />

![gradient_rainbow](static/gradient_rainbow.png)

#### Rainbow (bottom text)

<hr />
<br />

## Gradient Panel
Somtimes you need something more formal than a gradient, though. For that, you can use the gradient_panel function. This function takes a string, an optional number of colors (defaults to 4), and an optional justification (defaults to "left"). It will return a panel with the gradient text, and optionally, gradient title.

```python
text = "\tEnim tempor veniam proident. Reprehenderit deserunt do duis laboris laborum consectetur fugiat deserunt officia officia eu consequat. Aute sint occaecat adipisicing eu aute. Eu est laborum enim deserunt fugiat nostrud officia do ad cupidatat enim amet cillum amet. Consectetur occaecat ex quis irure cupidatat amet occaecat ad sit adipisicing pariatur est velit mollit voluptate. Eiusmod deserunt nisi voluptate irure. Sunt irure consectetur veniam dolore elit officia et in labore esse esse cupidatat labore. Fugiat enim irure ipsum eiusmod consequat irure commodo cillum.\n\n\tReprehenderit ea quis aliqua qui labore enim consequat ea nostrud voluptate amet reprehenderit consequat sunt. Ad est occaecat mollit qui sit enim do esse aute sint nulla sint laborum. Voluptate veniam ut Lorem eiusmod id veniam amet ipsum labore incididunt. Ex in consequat voluptate mollit nisi incididunt pariatur ipsum ut eiusmod ut cupidatat elit. Eu irure est ad nulla exercitation. Esse elit tempor reprehenderit ipsum eu officia sint.\n\n\tCupidatat officia incididunt cupidatat minim fugiat sit exercitation ullamco occaecat est officia ut occaecat labore. Id consectetur cupidatat amet aute. Pariatur nostrud enim reprehenderit aliqua. Elit deserunt excepteur aute aliquip."

console.print(
    gradient_panel(
        text,
        title="Hello World",
        title_align = 'center',
        subtitle = "The Cake is a Lie".
        subtitle_align = 'right'
        num_of_gradients = 4,
        justify = "left"
        width = None
    )
)
```
![gradient_panel](static/gradient_panel.png)