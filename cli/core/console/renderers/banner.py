import pathlib
import sys
from dataclasses import dataclass

from cli.core.console.base import console
from pyfiglet import Figlet
from rich.text import Text

HEXADECIMAL_BASE = 16


@dataclass(frozen=True)
class RGBColor:
    """Represent a terminal color as red, green, and blue channels."""

    red: int
    green: int
    blue: int

    @classmethod
    def from_hex(cls, color_hex: str) -> "RGBColor":
        """Parse a hex color string."""
        return cls(
            int(color_hex[1:3], HEXADECIMAL_BASE),
            int(color_hex[3:5], HEXADECIMAL_BASE),
            int(color_hex[5:7], HEXADECIMAL_BASE),
        )

    def interpolate(self, target: "RGBColor", ratio: float) -> "RGBColor":
        """Return the color at the requested position between two colors."""
        return RGBColor(
            self._interpolate_channel(self.red, target.red, ratio),
            self._interpolate_channel(self.green, target.green, ratio),
            self._interpolate_channel(self.blue, target.blue, ratio),
        )

    def as_hex(self) -> str:
        """Format the color as a Rich-compatible hex string."""
        red_hex = format(self.red, "02X")
        green_hex = format(self.green, "02X")
        blue_hex = format(self.blue, "02X")
        color_hex = f"{red_hex}{green_hex}{blue_hex}"
        return f"#{color_hex}"

    def _interpolate_channel(self, start: int, end: int, ratio: float) -> int:
        return int(start + ratio * (end - start))


class BannerRenderer:
    """Render the CLI banner."""

    def render(self, program_name: str) -> list[Text]:
        """Build the banner lines for the current program name."""
        banner_lines = self._render_banner_text(program_name)
        if not banner_lines:
            return []

        colors = self._banner_colors(max(len(line) for line in banner_lines))
        return [self._colorize_line(line, colors) for line in banner_lines]

    def _render_banner_text(self, program_name: str) -> list[Text]:
        prefix = program_name[:3].upper()
        suffix = program_name[3:7]
        normalized_program_name = prefix + suffix
        return [
            Text(line)
            for line in Figlet("georgia11").renderText(normalized_program_name).splitlines()
        ]

    def _banner_colors(self, line_length: int) -> list[str]:
        half_length = line_length // 2
        return self._gradient("#00C9CD", "#472AFF", half_length) + self._gradient(
            "#472AFF", "#392D9C", half_length + 1
        )

    def _colorize_line(self, line: Text, colors: list[str]) -> Text:
        colored_line = Text()
        for index, char in enumerate(line.plain):
            colored_line = Text.assemble(colored_line, Text(char, style=colors[index]))

        return colored_line

    def _gradient(
        self, start_hex: str, end_hex: str, num_samples: int = 16
    ) -> list[str]:  # pragma: no cover
        start_color = RGBColor.from_hex(start_hex)
        end_color = RGBColor.from_hex(end_hex)
        if num_samples <= 1:
            return [start_color.as_hex()]

        last_sample_index = num_samples - 1
        return [
            start_color.interpolate(end_color, sample / last_sample_index).as_hex()
            for sample in range(num_samples)
        ]


def show_banner() -> None:
    """Display a stylized program banner with a color gradient."""
    program_name = pathlib.Path(sys.argv[0]).name
    for line in BannerRenderer().render(program_name):
        console.print(line)
