import pathlib
import sys

from pyfiglet import Figlet
from rich.console import Console
from rich.text import Text

HEXADECIMAL_BASE = 16


def _gradient(start_hex: str, end_hex: str, num_samples: int = 16) -> list[str]:  # pragma: no cover
    start_rgb = _hex_to_rgb(start_hex)
    end_rgb = _hex_to_rgb(end_hex)
    gradient_colors = [start_hex]
    gradient_colors.extend(
        _gradient_color(start_rgb, end_rgb, sample, num_samples) for sample in range(1, num_samples)
    )
    return gradient_colors


def show_banner() -> None:
    """Display a stylized program banner with a color gradient."""
    banner_lines = [Text(line) for line in _banner_text().splitlines()]
    max_line_length = max(len(line) for line in banner_lines)
    half_length = max_line_length // 2
    colors = _gradient("#00C9CD", "#472AFF", half_length) + _gradient(
        "#472AFF", "#392D9C", half_length + 1
    )

    for line in banner_lines:
        _print_banner_line(line, colors)


def _banner_text() -> str:
    program_name = pathlib.Path(sys.argv[0]).name
    banner_name = f"{program_name[:3].upper()}{program_name[3:7]}"
    return Figlet("georgia11").renderText(banner_name)


def _gradient_color(
    start_rgb: tuple[int, int, int],
    end_rgb: tuple[int, int, int],
    sample: int,
    num_samples: int,
) -> str:
    ratio = float(sample) / (num_samples - 1)
    red = _interpolate(start_rgb[0], end_rgb[0], ratio)
    green = _interpolate(start_rgb[1], end_rgb[1], ratio)
    blue = _interpolate(start_rgb[2], end_rgb[2], ratio)
    return f"#{red:02X}{green:02X}{blue:02X}"


def _hex_to_rgb(color_hex: str) -> tuple[int, int, int]:
    return (
        int(color_hex[1:3], HEXADECIMAL_BASE),
        int(color_hex[3:5], HEXADECIMAL_BASE),
        int(color_hex[5:7], HEXADECIMAL_BASE),
    )


def _print_banner_line(line: Text, colors: list[str]) -> None:
    colored_line = Text()
    for index, char in enumerate(line.plain):
        colored_line = Text.assemble(colored_line, Text(char, style=colors[index]))
    console.print(colored_line)


def _interpolate(start_value: int, end_value: int, ratio: float) -> int:
    return int(start_value + ratio * (end_value - start_value))


console = Console(highlight=False)
