import pathlib
import sys

from pyfiglet import Figlet
from rich.console import Console
from rich.text import Text

HEXADECIMAL_BASE = 16


def _gradient(start_hex: str, end_hex: str, num_samples: int = 16) -> list[str]:  # pragma: no cover
    start_rgb = tuple(
        int(start_hex[index : index + 2], HEXADECIMAL_BASE) for index in range(1, 6, 2)
    )
    end_rgb = tuple(int(end_hex[index : index + 2], HEXADECIMAL_BASE) for index in range(1, 6, 2))
    gradient_colors = [start_hex]
    for sample in range(1, num_samples):
        red = int(start_rgb[0] + (float(sample) / (num_samples - 1)) * (end_rgb[0] - start_rgb[0]))
        green = int(
            start_rgb[1] + (float(sample) / (num_samples - 1)) * (end_rgb[1] - start_rgb[1])
        )
        blue = int(start_rgb[2] + (float(sample) / (num_samples - 1)) * (end_rgb[2] - start_rgb[2]))
        gradient_colors.append(f"#{red:02X}{green:02X}{blue:02X}")

    return gradient_colors


def show_banner() -> None:
    """Display a stylized program banner with a color gradient."""
    program_name = pathlib.Path(sys.argv[0]).name
    program_name = "".join((program_name[0:3].upper(), program_name[3:7]))
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
