import click
from typer.core import TyperGroup


class AliasTyperGroup(TyperGroup):
    """
    Provides ability to make commands with s and without s at the end same
    swocli account add
    swocli accounts add

    are same commands
    """

    def get_command(self, ctx, cmd_name):
        rv = click.Group.get_command(self, ctx, cmd_name)
        if rv is not None:
            return rv

        matches = [name for name in self.list_commands(ctx) if name == f"{cmd_name}s"]
        if not matches:
            return None
        elif len(matches) == 1:
            return click.Group.get_command(self, ctx, matches[0])

        ctx.fail(f"Too many matches: {', '.join(sorted(matches))}")  # pragma: no cover

    def resolve_command(self, ctx, args):
        _, cmd, args = super().resolve_command(ctx, args)
        return cmd.name, cmd, args
