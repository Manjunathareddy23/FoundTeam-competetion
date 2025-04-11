import typer
from rich.console import Console
from rich.table import Table
from rich.prompt import Confirm
from datetime import datetime, timedelta
import json
import os
from typing import Optional, List

app = typer.Typer()
console = Console()

DATA_FILE = "tasks.json"

class Task:
    def __init__(self, title, description, priority, due_date, tags, status="Pending", recurring=None):
        self.title = title
        self.description = description
        self.priority = priority
        self.due_date = due_date
        self.tags = tags
        self.status = status
        self.recurring = recurring

    def to_dict(self):
        return {
            "title": self.title,
            "description": self.description,
            "priority": self.priority,
            "due_date": self.due_date,
            "tags": self.tags,
            "status": self.status,
            "recurring": self.recurring
        }

    @staticmethod
    def from_dict(data):
        return Task(
            title=data["title"],
            description=data["description"],
            priority=data["priority"],
            due_date=data["due_date"],
            tags=data["tags"],
            status=data.get("status", "Pending"),
            recurring=data.get("recurring")
        )

def load_tasks() -> List[Task]:
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return [Task.from_dict(t) for t in json.load(f)]
    return []

def save_tasks(tasks: List[Task]):
    with open(DATA_FILE, "w") as f:
        json.dump([t.to_dict() for t in tasks], f, indent=2)

def generate_recurring_task(task: Task):
    if task.recurring and task.due_date:
        due = datetime.strptime(task.due_date, "%Y-%m-%d")
        now = datetime.now()
        while due < now:
            if task.recurring == "daily":
                due += timedelta(days=1)
            elif task.recurring == "weekly":
                due += timedelta(weeks=1)
            elif task.recurring == "monthly":
                due += timedelta(days=30)
        task.due_date = due.strftime("%Y-%m-%d")
    return task

@app.command()
def add(
    title: str = typer.Option(..., prompt=True),
    description: str = typer.Option("", prompt="Description"),
    priority: str = typer.Option("medium", prompt="Priority (low/medium/high)"),
    due_date: str = typer.Option("", prompt="Due date (YYYY-MM-DD)"),
    tags_input: str = typer.Option("", prompt="Tags (comma-separated, optional)"),
    recurring: Optional[str] = typer.Option(None, prompt="Recurring? (daily/weekly/monthly/none)", show_default=False)
):
    try:
        if due_date:
            datetime.strptime(due_date, "%Y-%m-%d")
    except ValueError:
        console.print("[red]Invalid date format! Use YYYY-MM-DD[/red]")
        raise typer.Exit()

    if recurring == "none":
        recurring = None

    tags = [t.strip() for t in tags_input.split(",") if t.strip()]

    task = Task(
        title=title,
        description=description,
        priority=priority.lower(),
        due_date=due_date,
        tags=tags,
        recurring=recurring
    )
    tasks = load_tasks()
    tasks.append(task)
    save_tasks(tasks)
    console.print(f"[green]Task '{title}' added![/green]")

@app.command()
def list(
    filter_tag: Optional[str] = typer.Option(None),
    search: Optional[str] = typer.Option(None),
    sort_by: Optional[str] = typer.Option(None)
):
    tasks = load_tasks()

    for t in tasks:
        if t.recurring:
            generate_recurring_task(t)
    save_tasks(tasks)

    if filter_tag:
        tasks = [t for t in tasks if filter_tag in t.tags]

    if search:
        tasks = [t for t in tasks if search.lower() in t.title.lower() or search.lower() in t.description.lower() or search.lower() in t.status.lower()]

    if sort_by == "due":
        tasks.sort(key=lambda x: x.due_date or "9999-99-99")
    elif sort_by == "priority":
        order = {"low": 3, "medium": 2, "high": 1}
        tasks.sort(key=lambda x: order.get(x.priority, 99))

    table = Table(title="Your Tasks")
    table.add_column("ID", style="dim", width=5)
    table.add_column("Title", style="bold cyan")
    table.add_column("Priority")
    table.add_column("Status")
    table.add_column("Due")
    table.add_column("Tags")
    table.add_column("Recurring")

    for i, task in enumerate(tasks):
        due_style = "[red]" if task.due_date and task.due_date < datetime.now().strftime("%Y-%m-%d") else ""
        table.add_row(
            str(i + 1),
            task.title,
            task.priority.capitalize(),
            task.status,
            f"{due_style}{task.due_date}[/red]" if task.due_date else "-",
            ", ".join(task.tags),
            task.recurring or "-"
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

    new_status = typer.prompt("New status (Pending/Completed)", default=task.status)
    new_due = typer.prompt("New due date (YYYY-MM-DD)", default=task.due_date or "")
    if new_due:
        try:
            datetime.strptime(new_due, "%Y-%m-%d")
        except ValueError:
            console.print("[red]Invalid date format![/red]")
            raise typer.Exit()

    task.status = new_status
    task.due_date = new_due
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

@app.command()
def export(format: str = typer.Option("json")):
    tasks = load_tasks()
    if format == "json":
        with open("backup_tasks.json", "w") as f:
            json.dump([t.to_dict() for t in tasks], f, indent=2)
        console.print("[green]Tasks exported to backup_tasks.json[/green]")
    elif format == "csv":
        import csv
        with open("backup_tasks.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Title", "Description", "Priority", "Status", "Due Date", "Tags", "Recurring"])
            for t in tasks:
                writer.writerow([t.title, t.description, t.priority, t.status, t.due_date, ",".join(t.tags), t.recurring])
        console.print("[green]Tasks exported to backup_tasks.csv[/green]")
    else:
        console.print("[red]Unsupported export format[/red]")

# ✅ FIXED this line
if __name__ == "__main__":
    app()
