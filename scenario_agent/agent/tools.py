from langchain_core.tools import tool
import sqlite3
import subprocess


@tool
def DatabaseQuery(query: str) -> str:
    """Query internal ticket database."""
    conn = sqlite3.connect("data/mock_tickets.db")
    result = conn.execute(query).fetchall()
    conn.close()
    return str(result)


@tool
def Shell(command: str) -> str:
    """Run system commands."""
    result = subprocess.run(
        command.split(),
        capture_output=True,
        text=True
    )
    return result.stdout or result.stderr or ""


@tool
def Email(to: str) -> str:
    """Send emails to employees."""
    return f"Simulated email sent to {to}"


tools = [DatabaseQuery, Shell, Email]
