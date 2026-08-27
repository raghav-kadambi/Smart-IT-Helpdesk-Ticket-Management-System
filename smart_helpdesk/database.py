"""
database.py
-----------
Handles SQLite connection, table creation, sample data, and CRUD.

This project uses Python's built-in sqlite3 module (no ORM).
"""

import os
import sqlite3
from datetime import datetime

# Database file is stored next to this script
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "helpdesk.db")


def get_connection():
    """Open a SQLite connection. row_factory lets us read rows like dictionaries."""
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_database():
    """Create tables if they do not exist, then insert sample data once."""
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS employees (
            employee_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            department TEXT NOT NULL
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS technicians (
            technician_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            specialization TEXT NOT NULL,
            open_ticket_count INTEGER NOT NULL DEFAULT 0
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS tickets (
            ticket_id INTEGER PRIMARY KEY AUTOINCREMENT,
            employee_id INTEGER NOT NULL,
            description TEXT NOT NULL,
            category TEXT NOT NULL,
            urgency TEXT NOT NULL,
            impact TEXT NOT NULL,
            priority TEXT NOT NULL,
            priority_score INTEGER NOT NULL,
            assigned_to TEXT NOT NULL,
            status TEXT NOT NULL,
            created_at TEXT NOT NULL,
            resolved_at TEXT,
            FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
        )
        """
    )

    connection.commit()
    _insert_sample_data(connection)
    connection.close()


def _insert_sample_data(connection):
    """Insert demo employees, technicians, and tickets only if the tables are empty."""
    cursor = connection.cursor()

    employee_count = cursor.execute("SELECT COUNT(*) FROM employees").fetchone()[0]
    if employee_count == 0:
        cursor.executemany(
            "INSERT INTO employees (employee_id, name, department) VALUES (?, ?, ?)",
            [
                (1024, "Amit Sharma", "Sales"),
                (1025, "Neha Patel", "Finance"),
                (1026, "Rohan Iyer", "HR"),
                (1027, "Sneha Reddy", "Operations"),
                (1028, "Vikram Singh", "Marketing"),
            ],
        )

    technician_count = cursor.execute("SELECT COUNT(*) FROM technicians").fetchone()[0]
    if technician_count == 0:
        cursor.executemany(
            "INSERT INTO technicians (name, specialization, open_ticket_count) VALUES (?, ?, ?)",
            [
                ("Ravi Kumar", "Network", 0),
                ("Priya Nair", "Hardware", 0),
                ("Arun Menon", "Software", 0),
                ("Karthik Rao", "Security", 0),
            ],
        )

    ticket_count = cursor.execute("SELECT COUNT(*) FROM tickets").fetchone()[0]
    if ticket_count == 0:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        sample_tickets = [
            (1024, "My laptop cannot connect to WiFi", "Network", "High", "High",
             "CRITICAL", 6, "Ravi Kumar", "OPEN", now, None),
            (1025, "Keyboard keys are not working", "Hardware", "Medium", "Medium",
             "MEDIUM", 4, "Priya Nair", "IN PROGRESS", now, None),
            (1026, "Need to install a new software application", "Software", "Low", "Low",
             "LOW", 2, "Arun Menon", "OPEN", now, None),
            (1027, "I received a phishing email asking for my password", "Security", "High", "Medium",
             "HIGH", 5, "Karthik Rao", "OPEN", now, None),
            (1028, "Printer is showing a paper jam error", "Hardware", "Medium", "Low",
             "MEDIUM", 3, "Priya Nair", "RESOLVED", now, now),
        ]
        cursor.executemany(
            """
            INSERT INTO tickets (
                employee_id, description, category, urgency, impact,
                priority, priority_score, assigned_to, status, created_at, resolved_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            sample_tickets,
        )

        # Open ticket counts must match OPEN + IN PROGRESS tickets
        cursor.execute(
            """
            UPDATE technicians
            SET open_ticket_count = (
                SELECT COUNT(*)
                FROM tickets
                WHERE tickets.assigned_to = technicians.name
                  AND tickets.status IN ('OPEN', 'IN PROGRESS')
            )
            """
        )

    connection.commit()


def get_employee_by_id(employee_id):
    """Return one employee row, or None if the ID is not found."""
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        "SELECT employee_id, name, department FROM employees WHERE employee_id = ?",
        (employee_id,),
    )
    row = cursor.fetchone()
    connection.close()
    return dict(row) if row else None


def get_all_technicians():
    """Return all technicians as a list of dictionaries."""
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        """
        SELECT technician_id, name, specialization, open_ticket_count
        FROM technicians
        ORDER BY technician_id
        """
    )
    rows = [dict(row) for row in cursor.fetchall()]
    connection.close()
    return rows


def get_technicians_by_specialization(specialization):
    """Return technicians who handle a given category/specialization."""
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        """
        SELECT technician_id, name, specialization, open_ticket_count
        FROM technicians
        WHERE specialization = ?
        ORDER BY open_ticket_count ASC, technician_id ASC
        """,
        (specialization,),
    )
    rows = [dict(row) for row in cursor.fetchall()]
    connection.close()
    return rows


def insert_ticket(ticket_data):
    """
    Save a new ticket and increase the assigned technician's open ticket count.

    ticket_data is a dictionary with the ticket fields.
    Returns the new ticket_id.
    """
    connection = get_connection()
    cursor = connection.cursor()
    try:
        cursor.execute(
            """
            INSERT INTO tickets (
                employee_id, description, category, urgency, impact,
                priority, priority_score, assigned_to, status, created_at, resolved_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                ticket_data["employee_id"],
                ticket_data["description"],
                ticket_data["category"],
                ticket_data["urgency"],
                ticket_data["impact"],
                ticket_data["priority"],
                ticket_data["priority_score"],
                ticket_data["assigned_to"],
                ticket_data["status"],
                ticket_data["created_at"],
                ticket_data.get("resolved_at"),
            ),
        )
        ticket_id = cursor.lastrowid
        cursor.execute(
            """
            UPDATE technicians
            SET open_ticket_count = open_ticket_count + 1
            WHERE name = ?
            """,
            (ticket_data["assigned_to"],),
        )
        connection.commit()
        return ticket_id
    except sqlite3.Error as error:
        connection.rollback()
        raise error
    finally:
        connection.close()


def get_tickets_by_employee(employee_id):
    """Return all tickets created by one employee, newest first."""
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        """
        SELECT t.ticket_id, t.employee_id, e.name AS employee_name, t.description,
               t.category, t.urgency, t.impact, t.priority, t.priority_score,
               t.assigned_to, t.status, t.created_at, t.resolved_at
        FROM tickets t
        JOIN employees e ON t.employee_id = e.employee_id
        WHERE t.employee_id = ?
        ORDER BY t.ticket_id DESC
        """,
        (employee_id,),
    )
    rows = [dict(row) for row in cursor.fetchall()]
    connection.close()
    return rows


def get_all_tickets(status_filter="All", priority_filter="All"):
    """Return tickets for the admin table. Filters can be All or a specific value."""
    connection = get_connection()
    cursor = connection.cursor()

    query = """
        SELECT t.ticket_id, t.employee_id, e.name AS employee_name, t.description,
               t.category, t.urgency, t.impact, t.priority, t.priority_score,
               t.assigned_to, t.status, t.created_at, t.resolved_at
        FROM tickets t
        JOIN employees e ON t.employee_id = e.employee_id
        WHERE 1 = 1
    """
    params = []

    if status_filter != "All":
        query += " AND t.status = ?"
        params.append(status_filter)

    if priority_filter != "All":
        query += " AND t.priority = ?"
        params.append(priority_filter)

    query += " ORDER BY t.ticket_id DESC"
    cursor.execute(query, params)
    rows = [dict(row) for row in cursor.fetchall()]
    connection.close()
    return rows


def get_ticket_by_id(ticket_id):
    """Return one ticket, or None if it does not exist."""
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(
        """
        SELECT t.ticket_id, t.employee_id, e.name AS employee_name, t.description,
               t.category, t.urgency, t.impact, t.priority, t.priority_score,
               t.assigned_to, t.status, t.created_at, t.resolved_at
        FROM tickets t
        JOIN employees e ON t.employee_id = e.employee_id
        WHERE t.ticket_id = ?
        """,
        (ticket_id,),
    )
    row = cursor.fetchone()
    connection.close()
    return dict(row) if row else None


def update_ticket_status(ticket_id, new_status):
    """
    Update ticket status.

    Rules:
    - OPEN / IN PROGRESS: ticket stays open
    - RESOLVED: set resolved_at and decrease technician open_ticket_count
    - If a resolved ticket is reopened, clear resolved_at and increase the count again
    """
    ticket = get_ticket_by_id(ticket_id)
    if ticket is None:
        raise ValueError("Ticket not found.")

    old_status = ticket["status"]
    if old_status == new_status:
        return

    connection = get_connection()
    cursor = connection.cursor()
    try:
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        was_open = old_status in ("OPEN", "IN PROGRESS")
        will_be_open = new_status in ("OPEN", "IN PROGRESS")

        if new_status == "RESOLVED":
            cursor.execute(
                "UPDATE tickets SET status = ?, resolved_at = ? WHERE ticket_id = ?",
                (new_status, now, ticket_id),
            )
        else:
            cursor.execute(
                "UPDATE tickets SET status = ?, resolved_at = NULL WHERE ticket_id = ?",
                (new_status, ticket_id),
            )

        if was_open and not will_be_open:
            cursor.execute(
                """
                UPDATE technicians
                SET open_ticket_count = CASE
                    WHEN open_ticket_count > 0 THEN open_ticket_count - 1
                    ELSE 0
                END
                WHERE name = ?
                """,
                (ticket["assigned_to"],),
            )
        elif (not was_open) and will_be_open:
            cursor.execute(
                """
                UPDATE technicians
                SET open_ticket_count = open_ticket_count + 1
                WHERE name = ?
                """,
                (ticket["assigned_to"],),
            )

        connection.commit()
    except sqlite3.Error as error:
        connection.rollback()
        raise error
    finally:
        connection.close()


def get_statistics():
    """Return simple dashboard counts."""
    connection = get_connection()
    cursor = connection.cursor()
    stats = {
        "total": cursor.execute("SELECT COUNT(*) FROM tickets").fetchone()[0],
        "open": cursor.execute(
            "SELECT COUNT(*) FROM tickets WHERE status IN ('OPEN', 'IN PROGRESS')"
        ).fetchone()[0],
        "critical": cursor.execute(
            "SELECT COUNT(*) FROM tickets WHERE priority = 'CRITICAL'"
        ).fetchone()[0],
        "resolved": cursor.execute(
            "SELECT COUNT(*) FROM tickets WHERE status = 'RESOLVED'"
        ).fetchone()[0],
    }
    connection.close()
    return stats
