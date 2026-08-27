"""
database.py
-----------
Pure Python data store using in-memory Lists, Dictionaries, and JSON file persistence.

No database server, no SQL, and no external dependencies required.
Uses Python's built-in `json` and `os` modules.
"""

import json
import os
from datetime import datetime

# Path to the JSON data file stored in the project folder
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "helpdesk_data.json")


def _get_default_sample_data():
    """Return initial sample data with employees, technicians, and demo tickets."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return {
        "employees": [
            {"employee_id": 1024, "name": "Amit Sharma", "department": "Sales"},
            {"employee_id": 1025, "name": "Neha Patel", "department": "Finance"},
            {"employee_id": 1026, "name": "Rohan Iyer", "department": "HR"},
            {"employee_id": 1027, "name": "Sneha Reddy", "department": "Operations"},
            {"employee_id": 1028, "name": "Vikram Singh", "department": "Marketing"},
        ],
        "technicians": [
            {"technician_id": 1, "name": "Ravi Kumar", "specialization": "Network", "open_ticket_count": 1},
            {"technician_id": 2, "name": "Priya Nair", "specialization": "Hardware", "open_ticket_count": 1},
            {"technician_id": 3, "name": "Arun Menon", "specialization": "Software", "open_ticket_count": 1},
            {"technician_id": 4, "name": "Karthik Rao", "specialization": "Security", "open_ticket_count": 1},
        ],
        "tickets": [
            {
                "ticket_id": 1,
                "employee_id": 1024,
                "description": "My laptop cannot connect to WiFi",
                "category": "Network",
                "urgency": "High",
                "impact": "High",
                "priority": "CRITICAL",
                "priority_score": 6,
                "assigned_to": "Ravi Kumar",
                "status": "OPEN",
                "created_at": now,
                "resolved_at": None,
            },
            {
                "ticket_id": 2,
                "employee_id": 1025,
                "description": "Keyboard keys are not working",
                "category": "Hardware",
                "urgency": "Medium",
                "impact": "Medium",
                "priority": "MEDIUM",
                "priority_score": 4,
                "assigned_to": "Priya Nair",
                "status": "IN PROGRESS",
                "created_at": now,
                "resolved_at": None,
            },
            {
                "ticket_id": 3,
                "employee_id": 1026,
                "description": "Need to install a new software application",
                "category": "Software",
                "urgency": "Low",
                "impact": "Low",
                "priority": "LOW",
                "priority_score": 2,
                "assigned_to": "Arun Menon",
                "status": "OPEN",
                "created_at": now,
                "resolved_at": None,
            },
            {
                "ticket_id": 4,
                "employee_id": 1027,
                "description": "I received a phishing email asking for my password",
                "category": "Security",
                "urgency": "High",
                "impact": "Medium",
                "priority": "HIGH",
                "priority_score": 5,
                "assigned_to": "Karthik Rao",
                "status": "OPEN",
                "created_at": now,
                "resolved_at": None,
            },
            {
                "ticket_id": 5,
                "employee_id": 1028,
                "description": "Printer is showing a paper jam error",
                "category": "Hardware",
                "urgency": "Medium",
                "impact": "Low",
                "priority": "MEDIUM",
                "priority_score": 3,
                "assigned_to": "Priya Nair",
                "status": "RESOLVED",
                "created_at": now,
                "resolved_at": now,
            },
        ],
    }


def _load_data():
    """Load and parse the JSON file into a Python dictionary."""
    if not os.path.exists(DATA_FILE):
        data = _get_default_sample_data()
        _save_data(data)
        return data

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, OSError):
        data = _get_default_sample_data()
        _save_data(data)
        return data


def _save_data(data):
    """Save the Python dictionary back to the JSON file."""
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=4)


def initialize_database():
    """Initialize the JSON data file if it does not exist."""
    _load_data()


def get_employee_by_id(employee_id):
    """
    Search for an employee by their ID.
    Returns the employee dictionary, or None if not found.
    """
    data = _load_data()
    for employee in data["employees"]:
        if employee["employee_id"] == int(employee_id):
            return dict(employee)
    return None


def get_all_technicians():
    """Return all technicians as a list of dictionaries."""
    data = _load_data()
    return sorted(data["technicians"], key=lambda t: t["technician_id"])


def get_technicians_by_specialization(specialization):
    """
    Return technicians matching a given specialization,
    sorted by open_ticket_count ascending, then technician_id ascending.
    """
    data = _load_data()
    matching = [t for t in data["technicians"] if t["specialization"] == specialization]
    return sorted(matching, key=lambda t: (t["open_ticket_count"], t["technician_id"]))


def insert_ticket(ticket_data):
    """
    Save a new ticket and increment the assigned technician's open_ticket_count.
    Returns the new integer ticket_id.
    """
    data = _load_data()

    # Generate next sequential ticket ID
    existing_ids = [t["ticket_id"] for t in data["tickets"]]
    next_id = max(existing_ids, default=0) + 1

    # Create the new ticket record
    new_ticket = {
        "ticket_id": next_id,
        "employee_id": int(ticket_data["employee_id"]),
        "description": str(ticket_data["description"]),
        "category": str(ticket_data["category"]),
        "urgency": str(ticket_data["urgency"]),
        "impact": str(ticket_data["impact"]),
        "priority": str(ticket_data["priority"]),
        "priority_score": int(ticket_data["priority_score"]),
        "assigned_to": str(ticket_data["assigned_to"]),
        "status": str(ticket_data["status"]),
        "created_at": str(ticket_data["created_at"]),
        "resolved_at": ticket_data.get("resolved_at"),
    }
    data["tickets"].append(new_ticket)

    # Increase assigned technician's open ticket count
    for tech in data["technicians"]:
        if tech["name"] == new_ticket["assigned_to"]:
            tech["open_ticket_count"] += 1
            break

    _save_data(data)
    return next_id


def get_tickets_by_employee(employee_id):
    """
    Return all tickets created by a specific employee, newest first.
    Enriches each ticket with the employee's name.
    """
    data = _load_data()
    emp_map = {e["employee_id"]: e["name"] for e in data["employees"]}

    employee_tickets = []
    for t in data["tickets"]:
        if t["employee_id"] == int(employee_id):
            ticket_copy = dict(t)
            ticket_copy["employee_name"] = emp_map.get(t["employee_id"], str(t["employee_id"]))
            employee_tickets.append(ticket_copy)

    # Sort descending by ticket_id (newest first)
    return sorted(employee_tickets, key=lambda t: t["ticket_id"], reverse=True)


def get_all_tickets(status_filter="All", priority_filter="All"):
    """
    Return all tickets matching optional status and priority filters, newest first.
    """
    data = _load_data()
    emp_map = {e["employee_id"]: e["name"] for e in data["employees"]}

    filtered_tickets = []
    for t in data["tickets"]:
        if status_filter != "All" and t["status"] != status_filter:
            continue
        if priority_filter != "All" and t["priority"] != priority_filter:
            continue

        ticket_copy = dict(t)
        ticket_copy["employee_name"] = emp_map.get(t["employee_id"], str(t["employee_id"]))
        filtered_tickets.append(ticket_copy)

    return sorted(filtered_tickets, key=lambda t: t["ticket_id"], reverse=True)


def get_ticket_by_id(ticket_id):
    """Return a single ticket dictionary by ticket_id, or None if not found."""
    data = _load_data()
    emp_map = {e["employee_id"]: e["name"] for e in data["employees"]}
    for t in data["tickets"]:
        if t["ticket_id"] == int(ticket_id):
            ticket_copy = dict(t)
            ticket_copy["employee_name"] = emp_map.get(t["employee_id"], str(t["employee_id"]))
            return ticket_copy
    return None


def update_ticket_status(ticket_id, new_status):
    """
    Update a ticket's status.
    - If status becomes RESOLVED: sets resolved_at and decreases open_ticket_count.
    - If a resolved ticket is reopened: clears resolved_at and increases open_ticket_count.
    """
    data = _load_data()
    target_ticket = None
    for t in data["tickets"]:
        if t["ticket_id"] == int(ticket_id):
            target_ticket = t
            break

    if target_ticket is None:
        raise ValueError("Ticket not found.")

    old_status = target_ticket["status"]
    if old_status == new_status:
        return

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    was_open = old_status in ("OPEN", "IN PROGRESS")
    will_be_open = new_status in ("OPEN", "IN PROGRESS")

    # Update ticket fields
    target_ticket["status"] = new_status
    if new_status == "RESOLVED":
        target_ticket["resolved_at"] = now
    else:
        target_ticket["resolved_at"] = None

    # Update technician workload counter
    assigned_name = target_ticket["assigned_to"]
    for tech in data["technicians"]:
        if tech["name"] == assigned_name:
            if was_open and not will_be_open:
                tech["open_ticket_count"] = max(0, tech["open_ticket_count"] - 1)
            elif (not was_open) and will_be_open:
                tech["open_ticket_count"] += 1
            break

    _save_data(data)


def get_statistics():
    """Return summary KPI statistics for the Admin Dashboard."""
    data = _load_data()
    tickets = data["tickets"]

    total = len(tickets)
    open_count = sum(1 for t in tickets if t["status"] in ("OPEN", "IN PROGRESS"))
    critical = sum(1 for t in tickets if t["priority"] == "CRITICAL")
    resolved = sum(1 for t in tickets if t["status"] == "RESOLVED")

    return {
        "total": total,
        "open": open_count,
        "critical": critical,
        "resolved": resolved,
    }
