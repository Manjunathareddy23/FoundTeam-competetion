# milestone1.py
import typer
from rich.console import Console
from rich.table import Table
from rich.prompt import Confirm
from datetime import datetime
import json
import os
from typing import List

app = typer.Typer()
console = Console()

DATA_FILE = "tasks.json"

class Task:
    def __init__(self, title, description, priority, due_date, tags, status="Pending"):
        self.title = title
        self.description = description
        self.priority = priority
        self.due_date = due_date
        self.tags = tags
        self.status = status

    def to_dict(self):
        return {
            "title": self.title,
            "description": self.description,
            "priority": self.priority,
            "due_date": self.due_date,
            "tags": self.tags,
            "status": self.status
        }

    @staticmethod
    def from_dict(data):
        return Task(
            title=data["title"],
            description=data["description"],
            priority=data["priority"],
            due_date=data["due_date"],
            tags=data["tags"],
            status=data.get("status", "Pending")
        )

def load_tasks() -> List[Task]:
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return [Task.from_dict(t) for t in json.load(f)]
    return []

def save_tasks(tasks: List[Task]):
    with open(DATA_FILE, "w") as f:
        json.dump([t.to_dict() for t in tasks], f, indent=2)

@app.command()
def add():
    title = typer.prompt("Title")
    description = typer.prompt("Description", default="")
    priority = typer.prompt("Priority (low/medium/high)", default="medium")
    due_date = typer.prompt("Due date (YYYY-MM-DD)", default="")
    tags_input = typer.prompt("Tags (comma-separated)", default="")

    if due_date:
        try:
            datetime.strptime(due_date, "%Y-%m-%d")
        except ValueError:
            console.print("[red]Invalid date format! Use YYYY-MM-DD[/red]")
            raise typer.Exit()

    tags = [tag.strip() for tag in tags_input.split(",") if tag.strip()]

    task = Task(title, description, priority.lower(), due_date, tags)
    tasks = load_tasks()
    tasks.append(task)
    save_tasks(tasks)
    console.print(f"[green]Task '{title}' added![/green]")

@app.command()
def list():
    tasks = load_tasks()
    table = Table(title="Your Tasks")
    table.add_column("ID", style="dim", width=5)
    table.add_column("Title", style="bold cyan")
    table.add_column("Priority")
    table.add_column("Status")
    table.add_column("Due")
    table.add_column("Tags")

    for i, task in enumerate(tasks):
        due_style = "[red]" if task.due_date and task.due_date < datetime.now().strftime("%Y-%m-%d") else ""
        table.add_row(
            str(i + 1),
            task.title,
            task.priority.capitalize(),
            task.status,
            f"{due_style}{task.due_date}[/red]" if task.due_date else "-",
            ", ".join(task.tags)
        )

    console.print(table)

@app.command()
def update(index: int):
    tasks = load_tasks()
    if not (1 <= index <= len(tasks)):
        console.print("[red]Invalid task index.[/red]")
        raise typer.Exit()

    task = tasks[index - 1]
    console.print(f"Editing: [bold]{task.title}[/bold]")
    task.status = typer.prompt("New status (Pending/Completed)", default=task.status)
    task.due_date = typer.prompt("New due date (YYYY-MM-DD)", default=task.due_date)

    if task.due_date:
        try:
            datetime.strptime(task.due_date, "%Y-%m-%d")
        except ValueError:
            console.print("[red]Invalid date format![/red]")
            raise typer.Exit()

    save_tasks(tasks)
    console.print("[green]Task updated![/green]")

@app.command()
def delete(index: int):
    tasks = load_tasks()
    if not (1 <= index <= len(tasks)):
        console.print("[red]Invalid task index.[/red]")
        raise typer.Exit()

    task = tasks[index - 1]
    if Confirm.ask(f"Are you sure you want to delete '{task.title}'?"):
        tasks.pop(index - 1)
        save_tasks(tasks)
        console.print("[red]Task deleted.[/red]")

if __name__ == "__main__":
    app()
