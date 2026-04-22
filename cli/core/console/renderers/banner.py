import pathlib
import sys

from cli.core.console.base import console
from pyfiglet import Figlet
from rich.text import Text

HEXADECIMAL_BASE = 16


class BannerRenderer:
    """Render the CLI banner."""

    def render(self, program_name: str) -> list[Text]:
        """Build the banner lines for the current program name."""
        normalized_program_name = "".join((program_name[:3].upper(), program_name[3:7]))
        figlet = Figlet("georgia11")
        banner_text = figlet.renderText(normalized_program_name)

        banner_lines = [Text(line) for line in banner_text.splitlines()]
        if not banner_lines:
            return []
        max_line_length = max(len(line) for line in banner_lines)
        half_length = max_line_length // 2

        colors = self._gradient("#00C9CD", "#472AFF", half_length) + self._gradient(
            "#472AFF", "#392D9C", half_length + 1
        )

        rendered_lines: list[Text] = []
        for line in banner_lines:
            colored_line = Text()
            for index, char in enumerate(line.plain):
                colored_line = Text.assemble(colored_line, Text(char, style=colors[index]))
            rendered_lines.append(colored_line)

        return rendered_lines

    def _gradient(
        self, start_hex: str, end_hex: str, num_samples: int = 16
    ) -> list[str]:  # pragma: no cover
        start_rgb = tuple(
            int(start_hex[index : index + 2], HEXADECIMAL_BASE) for index in range(1, 6, 2)
        )
        end_rgb = tuple(
            int(end_hex[index : index + 2], HEXADECIMAL_BASE) for index in range(1, 6, 2)
        )
        gradient_colors = [start_hex]
        for sample in range(1, num_samples):
            red = int(
                start_rgb[0] + (float(sample) / (num_samples - 1)) * (end_rgb[0] - start_rgb[0])
            )
            green = int(
                start_rgb[1] + (float(sample) / (num_samples - 1)) * (end_rgb[1] - start_rgb[1])
            )
            blue = int(
                start_rgb[2] + (float(sample) / (num_samples - 1)) * (end_rgb[2] - start_rgb[2])
            )
            rgb_color = bytes((red, green, blue)).hex().upper()
            gradient_colors.append(f"#{rgb_color}")

        return gradient_colors


def show_banner() -> None:
    """Display a stylized program banner with a color gradient."""
    program_name = pathlib.Path(sys.argv[0]).name
    for line in BannerRenderer().render(program_name):
        console.print(line)
