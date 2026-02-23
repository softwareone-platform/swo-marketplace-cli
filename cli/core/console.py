import pathlib
import sys

from pyfiglet import Figlet
from rich.console import Console
from rich.text import Text

HEXADECIMAL_BASE = 16
HEX_COLOR_START_INDEX = 1
HEX_COLOR_STOP_INDEX = 6
HEX_COLOR_STEP = 2


def _hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    rgb_values = [
        _to_hex_component(hex_color, index)
        for index in range(HEX_COLOR_START_INDEX, HEX_COLOR_STOP_INDEX, HEX_COLOR_STEP)
    ]
    return rgb_values[0], rgb_values[1], rgb_values[2]


def _to_hex_component(hex_color: str, index: int) -> int:
    return int(hex_color[index : index + 2], HEXADECIMAL_BASE)


def _blend_channel(start_value: int, end_value: int, sample_ratio: float) -> int:
    return int(start_value + sample_ratio * (end_value - start_value))


def _gradient(start_hex: str, end_hex: str, num_samples: int = 16) -> list[str]:  # pragma: no cover
    start_rgb = _hex_to_rgb(start_hex)
    end_rgb = _hex_to_rgb(end_hex)
    gradient_colors = [start_hex]
    sample_ratio_denominator = num_samples - 1
    for sample in range(1, num_samples):
        sample_ratio = float(sample) / sample_ratio_denominator
        red = _blend_channel(start_rgb[0], end_rgb[0], sample_ratio)
        green = _blend_channel(start_rgb[1], end_rgb[1], sample_ratio)
        blue = _blend_channel(start_rgb[2], end_rgb[2], sample_ratio)
        gradient_colors.append(f"#{red:02X}{green:02X}{blue:02X}")

    return gradient_colors


def show_banner() -> None:
    """Display a stylized program banner with a color gradient."""
    program_name = pathlib.Path(sys.argv[0]).name
    prefix = program_name[0:3].upper()
    suffix = program_name[3:7]
    program_name = f"{prefix}{suffix}"
    figlet = Figlet("georgia11")

    banner_text = figlet.renderText(program_name)

    banner_lines = [Text(line) for line in banner_text.splitlines()]
    max_line_length = max(len(line) for line in banner_lines)
    half_length = max_line_length // 2

    colors = _gradient("#00C9CD", "#472AFF", half_length) + _gradient(
        "#472AFF", "#392D9C", half_length + 1
    )

    for line in banner_lines:
        colored_line = Text()
        for index in range(len(line)):
            char = line[index : index + 1]
            char.stylize(colors[index])
            colored_line = Text.assemble(colored_line, char)
        console.print(colored_line)


console = Console(highlight=False)
