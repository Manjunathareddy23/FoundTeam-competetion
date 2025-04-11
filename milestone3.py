import typer
from rich.console import Console
from rich.prompt import Confirm
import json
import os
import csv
from typing import List
from datetime import datetime

from milestone2 import Task, load_tasks, save_tasks

app = typer.Typer()
console = Console()

BACKUP_JSON = "backup_tasks.json"
BACKUP_CSV = "backup_tasks.csv"

@app.command()
def backup(format: str = typer.Option("json", help="Backup format: json or csv")):
    tasks = load_tasks()

    if format == "json":
        with open(BACKUP_JSON, "w") as f:
            json.dump([t.to_dict() for t in tasks], f, indent=2)
        console.print(f"[green]Tasks backed up to {BACKUP_JSON}[/green]")

    elif format == "csv":
        with open(BACKUP_CSV, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Title", "Description", "Priority", "Status", "Due Date", "Tags", "Recurring"])
            for t in tasks:
                writer.writerow([
                    t.title,
                    t.description,
                    t.priority,
                    t.status,
                    t.due_date,
                    ",".join(t.tags),
                    t.recurring or "-"
                ])
        console.print(f"[green]Tasks backed up to {BACKUP_CSV}[/green]")
    else:
        console.print("[red]Unsupported format. Use 'json' or 'csv'.[/red]")

@app.command()
def restore(file: str = typer.Option(..., prompt=True)):
    if not os.path.exists(file):
        console.print("[red]Backup file does not exist.[/red]")
        raise typer.Exit()

    ext = file.split(".")[-1]

    try:
        if ext == "json":
            with open(file, "r") as f:
                data = json.load(f)
                tasks = [Task.from_dict(d) for d in data]
                save_tasks(tasks)
                console.print(f"[green]Tasks restored from {file}[/green]")
        else:
            console.print("[red]Only JSON restore is currently supported.[/red]")
    except Exception as e:
        console.print(f"[red]Failed to restore: {e}[/red]")

if __name__ == "__main__":
    app()
