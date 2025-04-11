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

if __name__ == "__main__":
    app()
