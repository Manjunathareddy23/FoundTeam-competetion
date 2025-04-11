import typer
from rich.console import Console
from rich.table import Table
from rich.prompt import Confirm
import json
import os
from typing import Optional, List
from datetime import datetime

app = typer.Typer()
console = Console()

DATA_FILE = "multiuser_tasks.json"
USERS_FILE = "users.json"

class Task:
    def __init__(self, title, description, assigned_to, created_by, status="Pending"):
        self.title = title
        self.description = description
        self.assigned_to = assigned_to
        self.created_by = created_by
        self.status = status

    def to_dict(self):
        return {
            "title": self.title,
            "description": self.description,
            "assigned_to": self.assigned_to,
            "created_by": self.created_by,
            "status": self.status
        }

    @staticmethod
    def from_dict(data):
        return Task(
            title=data["title"],
            description=data["description"],
            assigned_to=data["assigned_to"],
            created_by=data["created_by"],
            status=data["status"]
        )

class User:
    def __init__(self, username):
        self.username = username

    def to_dict(self):
        return {"username": self.username}

    @staticmethod
    def from_dict(data):
        return User(username=data["username"])

def load_tasks():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return [Task.from_dict(t) for t in json.load(f)]
    return []

def save_tasks(tasks):
    with open(DATA_FILE, "w") as f:
        json.dump([t.to_dict() for t in tasks], f, indent=2)

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            return [User.from_dict(u) for u in json.load(f)]
    return []

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump([u.to_dict() for u in users], f, indent=2)

@app.command()
def register(username: str):
    users = load_users()
    if any(u.username == username for u in users):
        console.print("[red]User already exists.[/red]")
        raise typer.Exit()
    users.append(User(username))
    save_users(users)
    console.print(f"[green]User '{username}' registered successfully![/green]")

@app.command()
def add(username: str, title: str, description: str, assign_to: str):
    users = load_users()
    if not any(u.username == username for u in users):
        console.print("[red]Invalid creator username.[/red]")
        raise typer.Exit()
    if not any(u.username == assign_to for u in users):
        console.print("[red]Assignee user does not exist.[/red]")
        raise typer.Exit()
    tasks = load_tasks()
    task = Task(title, description, assign_to, username)
    tasks.append(task)
    save_tasks(tasks)
    console.print(f"[green]Task '{title}' assigned to '{assign_to}'.[/green]")

@app.command()
def list(username: str):
    tasks = load_tasks()
    user_tasks = [t for t in tasks if t.assigned_to == username or t.created_by == username]

    table = Table(title=f"Tasks for {username}")
    table.add_column("Title", style="bold cyan")
    table.add_column("Description")
    table.add_column("Assigned To")
    table.add_column("Created By")
    table.add_column("Status")

    for task in user_tasks:
        table.add_row(task.title, task.description, task.assigned_to, task.created_by, task.status)

    console.print(table)

@app.command()
def report():
    tasks = load_tasks()
    total = len(tasks)
    completed = sum(1 for t in tasks if t.status.lower() == "completed")
    pending = total - completed

    console.print(f"[bold blue]Total Tasks:[/bold blue] {total}")
    console.print(f"[green]Completed Tasks:[/green] {completed}")
    console.print(f"[yellow]Pending Tasks:[/yellow] {pending}")

# ✅ Ready for milestone 5 next
if __name__ == "__main__":
    app()
