# Smart IT Helpdesk Ticket Management System

A desktop IT helpdesk application built for a **TCS Prime technical interview demonstration**.

Employees can submit IT support tickets. The system uses **simple, rule-based logic** (not AI or machine learning) to categorize the issue, calculate priority, assign a technician, and store everything in SQLite.

---

## Problem statement

In many offices, IT issues are reported through email or chat. Tickets can be miscategorized, given the wrong priority, or assigned unevenly to technicians. This project shows a small, explainable system that automates those first steps.

---

## Objective

Build a **local desktop application** where:

1. An employee submits a ticket description, urgency, and impact.
2. The system classifies the category using keywords.
3. The system calculates priority from urgency + impact.
4. The system assigns a technician based on category and current workload.
5. Tickets are stored in SQLite.
6. Admins/technicians can view, filter, and update ticket status.
7. A dashboard shows basic statistics.

---

## Features

- Simple login with two roles: **Employee** and **Admin/Technician**
- Create tickets (employee ID, name, description, urgency, impact)
- Keyword-based category classification
- Priority scoring (LOW / MEDIUM / HIGH / CRITICAL)
- Technician assignment by specialization and lowest open-ticket count
- SQLite storage with three tables
- Ticket statuses: OPEN, IN PROGRESS, RESOLVED
- Admin dashboard with counts, filters, and status updates
- Employee dashboard to create tickets and view only their own tickets

This project is a **rule-based ticket classification system**. It does **not** use AI, NLP libraries, or machine learning.

---

## Technology stack

| Layer | Choice | Why |
| --- | --- | --- |
| Language | Python 3 | Easy to read and explain |
| GUI | Tkinter (built-in) | No extra install, enough for a desktop demo |
| Database | SQLite via `sqlite3` | File-based, no server, no ORM |
| Libraries | Python standard library only | Interview-friendly |

Not used: Flask, Django, React, Node.js, Docker, cloud services, external APIs, MySQL, ML libraries.

---

## System workflow

```
Employee login
    -> Enter problem description, urgency, impact
    -> classifier.py finds the category from keywords
    -> priority.py calculates priority_score and label
    -> assignment.py picks a technician
    -> database.py saves the ticket in SQLite
    -> Employee sees the ticket in "My Tickets"

Admin / Technician login
    -> Dashboard shows Total / Open / Critical / Resolved
    -> Table shows all tickets
    -> Filter by status or priority
    -> Update status (OPEN / IN PROGRESS / RESOLVED)
    -> If resolved: set resolved_at and decrease open_ticket_count
```

---

## Database schema

### employees
| Column | Meaning |
| --- | --- |
| employee_id | Unique employee number (primary key) |
| name | Employee name |
| department | Department name |

### technicians
| Column | Meaning |
| --- | --- |
| technician_id | Auto-increment ID |
| name | Technician name |
| specialization | Network / Hardware / Software / Security |
| open_ticket_count | How many tickets are currently OPEN or IN PROGRESS |

### tickets
| Column | Meaning |
| --- | --- |
| ticket_id | Auto-increment ID |
| employee_id | Who raised the ticket (foreign key) |
| description | Problem text |
| category | Network / Hardware / Software / Security / Other |
| urgency | Low / Medium / High |
| impact | Low / Medium / High |
| priority | LOW / MEDIUM / HIGH / CRITICAL |
| priority_score | 2 to 6 |
| assigned_to | Technician name |
| status | OPEN / IN PROGRESS / RESOLVED |
| created_at | Created timestamp |
| resolved_at | Resolved timestamp (NULL until resolved) |

---

## How ticket classification works

The classifier is **keyword counting**, not machine learning.

1. Convert the description to lowercase.
2. For each category, count how many of its keywords appear in the text.
3. Choose the category with the **highest count**.
4. If the highest count is 0, category = **Other**.
5. If two categories tie, pick the first in this order: Network, Hardware, Software, Security.

Example: `"My laptop cannot connect to WiFi"`

- Network matches `wifi` (1)
- Hardware matches `laptop` (1)
- Tie → **Network** (first in the fixed order)

Example: `"Need to install a new software application"`

- Software matches `software`, `application`, `install` (3) → **Software**

---

## How priority calculation works

```
Low = 1, Medium = 2, High = 3
priority_score = urgency_score + impact_score
```

| Score | Priority |
| --- | --- |
| 2–3 | LOW |
| 4 | MEDIUM |
| 5 | HIGH |
| 6 | CRITICAL |

Example: High urgency + High impact = 3 + 3 = 6 → **CRITICAL**

---

## How technician assignment works

| Category | Specialist |
| --- | --- |
| Network | Ravi Kumar |
| Hardware | Priya Nair |
| Software | Arun Menon |
| Security | Karthik Rao |
| Other | Technician with the lowest open ticket count |

If more than one technician shares a specialization, the ticket goes to the one with the **lowest `open_ticket_count`**. Ties are broken by smaller `technician_id`.

When a ticket is created, that technician’s `open_ticket_count` increases by 1. When it is marked RESOLVED, the count decreases by 1.

---

## Project structure

```
smart_helpdesk/
├── main.py          Application entry point
├── database.py      SQLite connection, tables, CRUD
├── classifier.py    Keyword-based category classification
├── priority.py      Urgency + impact → priority
├── assignment.py    Technician assignment
├── gui.py           Tkinter login and dashboards
└── helpdesk.db      Created automatically on first run
```

---

## How to run the project

Requirements: Python 3 (Tkinter is included with standard Windows Python).

```bash
cd smart_helpdesk
python main.py
```

### Demo login

| Role | Username | Password |
| --- | --- | --- |
| Employee | `1024` to `1028` | `emp123` |
| Admin/Technician | `admin` | `admin123` |

Sample employees: Amit Sharma (1024), Neha Patel (1025), Rohan Iyer (1026), Sneha Reddy (1027), Vikram Singh (1028).

The first run creates `helpdesk.db` and inserts sample employees, technicians, and a few tickets so the admin dashboard is not empty.

---

## Future improvements

These are **not implemented** in the current project:

- Stronger authentication (hashed passwords, one password per user)
- Machine learning classification (would need labeled history; this would be a future enhancement, not the current design)
- Email or desktop notifications
- File attachments (screenshots)
- Reports and charts
- Role-based technician login (each technician sees only assigned tickets)
- Replace SQLite with MySQL if multiple computers must share one database

---

## Interview notes

See [INTERVIEW_PREPARATION.md](INTERVIEW_PREPARATION.md) for a 60-second pitch, file-by-file explanation, SQL, DSA, and likely TCS Prime questions.
