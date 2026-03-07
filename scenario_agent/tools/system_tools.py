import sqlite3
import subprocess


def query_database(query: str):

    conn = sqlite3.connect("company.db")
    cursor = conn.cursor()

    cursor.execute(query)
    result = cursor.fetchall()

    conn.close()

    return str(result)


def run_shell(command: str):

    result = subprocess.run(
        command.split(),
        capture_output=True,
        text=True
    )

    return result.stdout