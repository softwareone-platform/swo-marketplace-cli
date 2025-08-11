import click
from typer.core import TyperGroup


class AliasTyperGroup(TyperGroup):
    """Provides ability to make commands with s and without s at the end.

    Examples:
        mpt-cli account add
        mpt-cli accounts add
    """

    def get_command(self, ctx: click.Context, cmd_name: str) -> click.Command | None:
        """Retrieves a command by name, supporting singular and plural forms.

        Args:
            ctx: The Click context.
            cmd_name: The name of the command to retrieve.

        Returns:
            The command object if found, otherwise abort the execution of the program.

        """
        rv = click.Group.get_command(self, ctx, cmd_name)
        if rv is not None:
            return rv

        matches = [name for name in self.list_commands(ctx) if name == f"{cmd_name}s"]
        if not matches:
            return None
        if len(matches) == 1:
            return click.Group.get_command(self, ctx, matches[0])

        ctx.fail(f"Too many matches: {', '.join(sorted(matches))}")

    def resolve_command(
        self, ctx: click.Context, args: list[str]
    ) -> tuple[str, click.Command, list[str]]:
        """Resolves the command name, command object, and remaining arguments.

        Args:
            ctx: The Click context.
            args: The list of command-line arguments.

        Returns:
            A tuple containing the command name, command object, and remaining arguments.

        """
        _, cmd, args = super().resolve_command(ctx, args)
        return cmd.name, cmd, args  # type: ignore [union-attr, return-value]
