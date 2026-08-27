"""
gui.py
------
Tkinter screens: Login, Employee Dashboard, Admin Dashboard.
"""

import sqlite3
from datetime import datetime
import tkinter as tk
from tkinter import ttk, messagebox

import assignment
import classifier
import database
import priority

# Simple corporate color palette
NAVY = "#1B365D"
BLUE = "#2E75B6"
LIGHT_BG = "#F4F6F8"
WHITE = "#FFFFFF"
DARK_TEXT = "#1F2933"
MUTED = "#52606D"


DEMO_EMPLOYEE_PASSWORD = "emp123"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"


def configure_styles(root):
    """Apply a clean ttk theme used by all windows."""
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    style.configure("TFrame", background=LIGHT_BG)
    style.configure("Card.TFrame", background=WHITE)
    style.configure("Header.TFrame", background=NAVY)
    style.configure("TLabel", background=LIGHT_BG, foreground=DARK_TEXT, font=("Segoe UI", 10))
    style.configure("Header.TLabel", background=NAVY, foreground=WHITE, font=("Segoe UI", 16, "bold"))
    style.configure("SubHeader.TLabel", background=NAVY, foreground="#D9E8F5", font=("Segoe UI", 10))
    style.configure("CardTitle.TLabel", background=WHITE, foreground=MUTED, font=("Segoe UI", 9))
    style.configure("CardValue.TLabel", background=WHITE, foreground=NAVY, font=("Segoe UI", 18, "bold"))
    style.configure("Title.TLabel", background=LIGHT_BG, foreground=NAVY, font=("Segoe UI", 14, "bold"))
    style.configure("Muted.TLabel", background=LIGHT_BG, foreground=MUTED, font=("Segoe UI", 9))
    style.configure("TButton", font=("Segoe UI", 10), padding=6)
    style.configure("Accent.TButton", font=("Segoe UI", 10, "bold"), padding=8)
    style.configure("Treeview", font=("Segoe UI", 9), rowheight=26)
    style.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"))
    style.configure("TCombobox", font=("Segoe UI", 10))
    style.configure("TEntry", font=("Segoe UI", 10))


def short_text(value, limit=40):
    """Keep long descriptions readable inside the table."""
    text = str(value or "")
    if len(text) <= limit:
        return text
    return text[: limit - 3] + "..."


def fill_ticket_table(tree, tickets):
    """Reload a Treeview with ticket rows."""
    for item in tree.get_children():
        tree.delete(item)

    for ticket in tickets:
        tree.insert(
            "",
            "end",
            values=(
                ticket["ticket_id"],
                ticket.get("employee_name", ticket["employee_id"]),
                short_text(ticket["description"]),
                ticket["category"],
                ticket["priority"],
                ticket["assigned_to"],
                ticket["status"],
                ticket["created_at"],
            ),
        )


class LoginWindow:
    """Very simple demonstration login. Not real authentication."""

    def __init__(self, root):
        self.root = root
        self.root.title("Smart IT Helpdesk - Login")
        self.root.geometry("520x460")
        self.root.configure(bg=LIGHT_BG)
        self.root.resizable(False, False)
        configure_styles(self.root)
        self._build()

    def _build(self):
        header = ttk.Frame(self.root, style="Header.TFrame")
        header.pack(fill="x")
        ttk.Label(header, text="Smart IT Helpdesk", style="Header.TLabel").pack(pady=(18, 2))
        ttk.Label(
            header,
            text="Ticket Management System",
            style="SubHeader.TLabel",
        ).pack(pady=(0, 18))

        form = ttk.Frame(self.root, padding=30)
        form.pack(fill="both", expand=True)

        ttk.Label(form, text="Sign in to continue", style="Title.TLabel").grid(
            row=0, column=0, columnspan=2, sticky="w", pady=(0, 16)
        )

        ttk.Label(form, text="Role").grid(row=1, column=0, sticky="w", pady=6)
        self.role_var = tk.StringVar(value="Employee")
        role_box = ttk.Combobox(
            form,
            textvariable=self.role_var,
            values=["Employee", "Admin/Technician"],
            state="readonly",
            width=32,
        )
        role_box.grid(row=1, column=1, sticky="w", pady=6)

        ttk.Label(form, text="Username / Employee ID").grid(row=2, column=0, sticky="w", pady=6)
        self.username_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.username_var, width=35).grid(
            row=2, column=1, sticky="w", pady=6
        )

        ttk.Label(form, text="Password").grid(row=3, column=0, sticky="w", pady=6)
        self.password_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.password_var, show="*", width=35).grid(
            row=3, column=1, sticky="w", pady=6
        )

        ttk.Button(form, text="Login", style="Accent.TButton", command=self._login).grid(
            row=4, column=0, columnspan=2, pady=18, sticky="ew"
        )

        demo = (
            "Demo login (for interview demonstration)\n"
            "Employee: ID 1024 to 1028  |  Password: emp123\n"
            "Admin/Technician: username admin  |  Password: admin123"
        )
        ttk.Label(form, text=demo, style="Muted.TLabel", justify="left").grid(
            row=5, column=0, columnspan=2, sticky="w"
        )

        form.columnconfigure(1, weight=1)

    def _login(self):
        role = self.role_var.get()
        username = self.username_var.get().strip()
        password = self.password_var.get().strip()

        if not username or not password:
            messagebox.showerror("Invalid login", "Please enter username and password.")
            return

        if role == "Admin/Technician":
            if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
                self.root.destroy()
                AdminDashboard()
            else:
                messagebox.showerror("Invalid login", "Admin username or password is incorrect.")
            return

        try:
            employee_id = int(username)
        except ValueError:
            messagebox.showerror("Invalid login", "Employee ID must be a number, for example 1024.")
            return

        employee = database.get_employee_by_id(employee_id)
        if employee is None:
            messagebox.showerror("Invalid login", "This Employee ID does not exist in the system.")
            return

        if password != DEMO_EMPLOYEE_PASSWORD:
            messagebox.showerror("Invalid login", "Incorrect employee password.")
            return

        self.root.destroy()
        EmployeeDashboard(employee)


class EmployeeDashboard:
    """Employees can create tickets and view only their own tickets."""

    def __init__(self, employee):
        self.employee = employee
        self.root = tk.Tk()
        self.root.title("Smart IT Helpdesk - Employee")
        self.root.geometry("980x640")
        self.root.configure(bg=LIGHT_BG)
        configure_styles(self.root)
        self._build()
        self._refresh_tickets()
        self.root.mainloop()

    def _build(self):
        header = ttk.Frame(self.root, style="Header.TFrame")
        header.pack(fill="x")
        ttk.Label(
            header,
            text=f"Welcome, {self.employee['name']}",
            style="Header.TLabel",
        ).pack(side="left", padx=20, pady=14)
        ttk.Label(
            header,
            text=f"ID: {self.employee['employee_id']}  |  {self.employee['department']}",
            style="SubHeader.TLabel",
        ).pack(side="left", padx=10)
        ttk.Button(header, text="Logout", command=self._logout).pack(side="right", padx=20, pady=14)

        body = ttk.Frame(self.root, padding=16)
        body.pack(fill="both", expand=True)

        form_card = ttk.LabelFrame(body, text="Create Ticket", padding=12)
        form_card.pack(fill="x")

        ttk.Label(form_card, text="Employee ID").grid(row=0, column=0, sticky="w", padx=6, pady=4)
        self.emp_id_var = tk.StringVar(value=str(self.employee["employee_id"]))
        ttk.Entry(form_card, textvariable=self.emp_id_var, width=22, state="readonly").grid(
            row=0, column=1, sticky="w", padx=6, pady=4
        )

        ttk.Label(form_card, text="Employee Name").grid(row=0, column=2, sticky="w", padx=6, pady=4)
        self.emp_name_var = tk.StringVar(value=self.employee["name"])
        ttk.Entry(form_card, textvariable=self.emp_name_var, width=28, state="readonly").grid(
            row=0, column=3, sticky="w", padx=6, pady=4
        )

        ttk.Label(form_card, text="Urgency").grid(row=1, column=0, sticky="w", padx=6, pady=4)
        self.urgency_var = tk.StringVar()
        ttk.Combobox(
            form_card,
            textvariable=self.urgency_var,
            values=["Low", "Medium", "High"],
            state="readonly",
            width=20,
        ).grid(row=1, column=1, sticky="w", padx=6, pady=4)

        ttk.Label(form_card, text="Impact").grid(row=1, column=2, sticky="w", padx=6, pady=4)
        self.impact_var = tk.StringVar()
        ttk.Combobox(
            form_card,
            textvariable=self.impact_var,
            values=["Low", "Medium", "High"],
            state="readonly",
            width=26,
        ).grid(row=1, column=3, sticky="w", padx=6, pady=4)

        ttk.Label(form_card, text="Problem Description").grid(
            row=2, column=0, sticky="nw", padx=6, pady=4
        )
        self.description_box = tk.Text(form_card, width=70, height=4, font=("Segoe UI", 10))
        self.description_box.grid(row=2, column=1, columnspan=3, sticky="ew", padx=6, pady=4)

        ttk.Button(
            form_card,
            text="Submit Ticket",
            style="Accent.TButton",
            command=self._submit_ticket,
        ).grid(row=3, column=1, sticky="w", padx=6, pady=8)

        table_card = ttk.LabelFrame(body, text="My Tickets", padding=12)
        table_card.pack(fill="both", expand=True, pady=(12, 0))

        columns = (
            "ticket_id",
            "employee",
            "description",
            "category",
            "priority",
            "assigned_to",
            "status",
            "created_at",
        )
        self.tree = ttk.Treeview(table_card, columns=columns, show="headings")
        headings = {
            "ticket_id": "Ticket ID",
            "employee": "Employee",
            "description": "Description",
            "category": "Category",
            "priority": "Priority",
            "assigned_to": "Assigned Technician",
            "status": "Status",
            "created_at": "Created Time",
        }
        widths = {
            "ticket_id": 80,
            "employee": 110,
            "description": 220,
            "category": 90,
            "priority": 80,
            "assigned_to": 130,
            "status": 100,
            "created_at": 140,
        }
        for column in columns:
            self.tree.heading(column, text=headings[column])
            self.tree.column(column, width=widths[column], anchor="center")

        scroll = ttk.Scrollbar(table_card, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

    def _refresh_tickets(self):
        tickets = database.get_tickets_by_employee(self.employee["employee_id"])
        fill_ticket_table(self.tree, tickets)

    def _submit_ticket(self):
        description = self.description_box.get("1.0", "end").strip()
        urgency = self.urgency_var.get().strip()
        impact = self.impact_var.get().strip()

        if not description:
            messagebox.showerror("Missing information", "Please enter a problem description.")
            return
        if not urgency:
            messagebox.showerror("Missing information", "Please select urgency.")
            return
        if not impact:
            messagebox.showerror("Missing information", "Please select impact.")
            return

        employee_id = self.employee["employee_id"]
        employee = database.get_employee_by_id(employee_id)
        if employee is None:
            messagebox.showerror("Invalid employee ID", "This employee does not exist.")
            return

        try:
            category = classifier.classify_ticket(description)
            priority_label, priority_score = priority.calculate_priority(urgency, impact)
            assigned_to = assignment.assign_technician(category)
            created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            ticket_id = database.insert_ticket(
                {
                    "employee_id": employee_id,
                    "description": description,
                    "category": category,
                    "urgency": urgency,
                    "impact": impact,
                    "priority": priority_label,
                    "priority_score": priority_score,
                    "assigned_to": assigned_to,
                    "status": "OPEN",
                    "created_at": created_at,
                }
            )
        except (ValueError, sqlite3.Error) as error:
            messagebox.showerror("Could not create ticket", str(error))
            return

        messagebox.showinfo(
            "Ticket created",
            (
                f"Ticket #{ticket_id} has been created.\n\n"
                f"Category: {category}\n"
                f"Priority: {priority_label} (score {priority_score})\n"
                f"Assigned to: {assigned_to}"
            ),
        )
        self.description_box.delete("1.0", "end")
        self.urgency_var.set("")
        self.impact_var.set("")
        self._refresh_tickets()

    def _logout(self):
        self.root.destroy()
        start_login()


class AdminDashboard:
    """Admin/technician view: statistics, filters, and status updates."""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Smart IT Helpdesk - Admin")
        self.root.geometry("1100x680")
        self.root.configure(bg=LIGHT_BG)
        configure_styles(self.root)
        self._build()
        self._refresh()
        self.root.mainloop()

    def _build(self):
        header = ttk.Frame(self.root, style="Header.TFrame")
        header.pack(fill="x")
        ttk.Label(header, text="Admin / Technician Dashboard", style="Header.TLabel").pack(
            side="left", padx=20, pady=14
        )
        ttk.Button(header, text="Logout", command=self._logout).pack(side="right", padx=20, pady=14)

        body = ttk.Frame(self.root, padding=16)
        body.pack(fill="both", expand=True)

        stats_row = ttk.Frame(body)
        stats_row.pack(fill="x")
        self.stat_labels = {}
        titles = [
            ("total", "Total Tickets"),
            ("open", "Open Tickets"),
            ("critical", "Critical Tickets"),
            ("resolved", "Resolved Tickets"),
        ]
        for key, title in titles:
            card = ttk.Frame(stats_row, style="Card.TFrame", padding=12)
            card.pack(side="left", expand=True, fill="x", padx=6)
            ttk.Label(card, text=title, style="CardTitle.TLabel").pack(anchor="w")
            value_label = ttk.Label(card, text="0", style="CardValue.TLabel")
            value_label.pack(anchor="w")
            self.stat_labels[key] = value_label

        filter_row = ttk.Frame(body)
        filter_row.pack(fill="x", pady=12)

        ttk.Label(filter_row, text="Filter by Status").pack(side="left")
        self.status_filter = tk.StringVar(value="All")
        ttk.Combobox(
            filter_row,
            textvariable=self.status_filter,
            values=["All", "OPEN", "IN PROGRESS", "RESOLVED"],
            state="readonly",
            width=16,
        ).pack(side="left", padx=8)

        ttk.Label(filter_row, text="Filter by Priority").pack(side="left", padx=(16, 0))
        self.priority_filter = tk.StringVar(value="All")
        ttk.Combobox(
            filter_row,
            textvariable=self.priority_filter,
            values=["All", "LOW", "MEDIUM", "HIGH", "CRITICAL"],
            state="readonly",
            width=16,
        ).pack(side="left", padx=8)

        ttk.Button(filter_row, text="Apply Filters", command=self._refresh).pack(side="left", padx=8)

        table_card = ttk.LabelFrame(body, text="All Tickets", padding=12)
        table_card.pack(fill="both", expand=True)

        columns = (
            "ticket_id",
            "employee",
            "description",
            "category",
            "priority",
            "assigned_to",
            "status",
            "created_at",
        )
        self.tree = ttk.Treeview(table_card, columns=columns, show="headings")
        headings = {
            "ticket_id": "Ticket ID",
            "employee": "Employee",
            "description": "Description",
            "category": "Category",
            "priority": "Priority",
            "assigned_to": "Assigned Technician",
            "status": "Status",
            "created_at": "Created Time",
        }
        widths = {
            "ticket_id": 80,
            "employee": 120,
            "description": 240,
            "category": 90,
            "priority": 80,
            "assigned_to": 140,
            "status": 100,
            "created_at": 140,
        }
        for column in columns:
            self.tree.heading(column, text=headings[column])
            self.tree.column(column, width=widths[column], anchor="center")

        scroll = ttk.Scrollbar(table_card, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        update_row = ttk.Frame(body)
        update_row.pack(fill="x", pady=12)
        ttk.Label(update_row, text="Update selected ticket status").pack(side="left")
        self.new_status_var = tk.StringVar(value="IN PROGRESS")
        ttk.Combobox(
            update_row,
            textvariable=self.new_status_var,
            values=["OPEN", "IN PROGRESS", "RESOLVED"],
            state="readonly",
            width=16,
        ).pack(side="left", padx=8)
        ttk.Button(
            update_row,
            text="Update Status",
            style="Accent.TButton",
            command=self._update_status,
        ).pack(side="left")

    def _refresh(self):
        stats = database.get_statistics()
        for key, label in self.stat_labels.items():
            label.config(text=str(stats[key]))

        tickets = database.get_all_tickets(
            status_filter=self.status_filter.get(),
            priority_filter=self.priority_filter.get(),
        )
        fill_ticket_table(self.tree, tickets)

    def _update_status(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("No ticket selected", "Please select a ticket from the table.")
            return

        ticket_id = self.tree.item(selected[0], "values")[0]
        new_status = self.new_status_var.get()

        try:
            database.update_ticket_status(int(ticket_id), new_status)
        except (ValueError, sqlite3.Error) as error:
            messagebox.showerror("Could not update ticket", str(error))
            return

        messagebox.showinfo("Status updated", f"Ticket #{ticket_id} is now {new_status}.")
        self._refresh()

    def _logout(self):
        self.root.destroy()
        start_login()


def start_login():
    root = tk.Tk()
    LoginWindow(root)
    root.mainloop()
