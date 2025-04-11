import typer
from rich.console import Console
import json
import os

app = typer.Typer()
console = Console()

SETTINGS_FILE = "settings.json"

# Default theme config
def default_settings():
    return {
        "theme": "default",
        "color_scheme": {
            "success": "green",
            "error": "red",
            "prompt": "cyan",
            "info": "yellow"
        }
    }

def load_settings():
    if not os.path.exists(SETTINGS_FILE):
        save_settings(default_settings())
    with open(SETTINGS_FILE, "r") as f:
        return json.load(f)

def save_settings(settings):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=2)

def themed_print(message: str, type_: str = "info"):
    settings = load_settings()
    color = settings["color_scheme"].get(type_, "white")
    console.print(f"[{color}]{message}[/{color}]")

@app.command()
def change_theme():
    """Change the CLI theme color scheme."""
    settings = load_settings()
    console.print("Choose a theme:")
    console.print("1. Default\n2. Ocean\n3. Sunset")
    choice = typer.prompt("Enter choice (1/2/3)", default="1")

    themes = {
        "1": default_settings()["color_scheme"],
        "2": {
            "success": "blue",
            "error": "bright_red",
            "prompt": "bright_cyan",
            "info": "bright_blue"
        },
        "3": {
            "success": "magenta",
            "error": "bright_yellow",
            "prompt": "bright_magenta",
            "info": "bright_red"
        }
    }

    if choice in themes:
        settings["color_scheme"] = themes[choice]
        save_settings(settings)
        themed_print("Theme updated successfully!", "success")
    else:
        themed_print("Invalid choice.", "error")

@app.command()
def view_settings():
    """View current configuration settings."""
    settings = load_settings()
    themed_print("Current Settings:", "info")
    for key, value in settings["color_scheme"].items():
        console.print(f"- {key.capitalize()}: [{value}]{value}[/{value}]")

@app.command()
def test_error_handling():
    """Simulate common errors to demonstrate error messages."""
    try:
        themed_print("Trying to divide by zero...", "info")
        x = 1 / 0
    except ZeroDivisionError:
        themed_print("Cannot divide by zero!", "error")

    try:
        themed_print("Trying to open missing file...", "info")
        with open("missing_file.txt", "r") as f:
            data = f.read()
    except FileNotFoundError:
        themed_print("File not found.", "error")

if __name__ == "__main__":
    app()
