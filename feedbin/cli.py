import typer

from feedbin.commands import add, list, mark_unread

app = typer.Typer(no_args_is_help=True)

app.command(name="add", no_args_is_help=True)(add.main)
app.command(name="list")(list.main)
app.command(name="mark-unread", no_args_is_help=True)(mark_unread.main)
