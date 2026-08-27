# Smart IT Helpdesk Ticket Management System

An automated desktop IT helpdesk and incident management system designed for enterprise support teams.

The system streamlines internal IT support workflows by automatically categorizing submitted issues, calculating standard ITIL priority scores, assigning domain-specialized technicians through greedy load balancing, and tracking ticket lifecycles from creation to resolution.

---

## System Overview & Objectives

In modern organizations, IT support requests often arrive through fragmented, unstructured channels (emails, chat, phone calls). Without automated triage:
- Critical hardware or network outages wait in the same unorganized queues as minor software queries.
- Support tickets are frequently misclassified or misrouted.
- Support technicians experience unbalanced workloads.

This project delivers a **lightweight, desktop-based IT service management solution** developed in Python. It provides automated incident triage, real-time workload balancing, transparent audit tracking, and executive KPI reporting—all without requiring complex database server infrastructure.

---

## Core Capabilities & Features

### 1. Role-Based Access
- **Employee Portal:** Enables employees to submit new IT tickets, specify operational urgency and business impact, and monitor the live progress of their personal tickets.
- **Admin / Technician Portal:** Provides IT administrators and technicians with global ticket visibility, real-time KPI metrics, multi-criteria filtering, and status management.

### 2. Automated Rule-Based Classification
- Fast, deterministic keyword matching algorithm that tokenizes ticket descriptions and calculates frequency scores across domain dictionaries (`Network`, `Hardware`, `Software`, `Security`, and `Other`).
- Operates transparently without opaque black-box models or external API dependencies.

### 3. ITIL-Compliant Priority Scoring
- Combines categorical inputs (Urgency & Impact: Low, Medium, High) into a normalized numeric score ($2\text{ to }6$).
- Automatically maps scores to standardized incident response tiers: `LOW`, `MEDIUM`, `HIGH`, or `CRITICAL`.

### 4. Smart Dispatching & Load Balancing
- Routes incidents directly to technicians with matching domain specializations.
- Balances active workloads by dynamically selecting the specialist with the fewest active (`OPEN` or `IN PROGRESS`) tickets.
- Automatically handles general `"Other"` requests by routing to the technician with the lowest overall queue.

### 5. Complete Ticket Lifecycle Tracking
- Tracks status transitions: `OPEN` $\rightarrow$ `IN PROGRESS` $\rightarrow$ `RESOLVED`.
- Automatically timestamps creation and resolution times while synchronizing technician workload counters.

### 6. Interactive Executive Dashboard
- Real-time KPI summary cards displaying **Total**, **Open**, **Critical**, and **Resolved** ticket metrics.
- Dynamic filtering by ticket status and priority level.

---

## Technology Stack & Architecture

| Layer | Technology | Purpose |
| --- | --- | --- |
| **Language** | Python 3 | Core application runtime and business logic |
| **User Interface** | Tkinter (`tkinter.ttk`) | Native, responsive desktop graphical interface |
| **Data Storage** | Pure Python + JSON (`json` module) | In-memory dynamic collections with human-readable JSON persistence |
| **Standard Libraries** | `os`, `json`, `datetime` | Standard library components ensuring zero external package dependencies |

---

## System Architecture & Workflow

```
[Employee Portal]
       │
       ▼
[Enter Issue Details] ──► Urgency (1-3), Impact (1-3), Problem Description
       │
       ├─► 1. classifier.py: Token frequency matching determines Category
       ├─► 2. priority.py: Urgency + Impact matrix calculates Priority Score & Tier
       ├─► 3. assignment.py: Dispatches to domain specialist with lowest active load
       │
       ▼
[Data Persistence (database.py)] ──► Updates helpdesk_data.json & increments workload
       │
       ▼
[Admin & Technician Portal]
       │
       ├─► Real-time KPI Summary: Total, Open, Critical, Resolved counts
       ├─► Multi-factor filtering by Status and Priority
       └─► Status Updates: Resolving a ticket updates resolved_at and decrements technician queue
```

---

## Data Schema & Storage

The system utilizes an in-memory structured data model persisted to `helpdesk_data.json`:

### Employees (`employees`)
| Attribute | Type | Description |
| --- | --- | --- |
| `employee_id` | `int` | Unique employee identification number (e.g., `1024`) |
| `name` | `str` | Full employee name |
| `department` | `str` | Organizational department (Sales, Finance, HR, Operations, Marketing) |

### Technicians (`technicians`)
| Attribute | Type | Description |
| --- | --- | --- |
| `technician_id` | `int` | Unique technician identifier |
| `name` | `str` | Support technician name |
| `specialization` | `str` | Domain area: `Network`, `Hardware`, `Software`, `Security` |
| `open_ticket_count` | `int` | Current count of active (`OPEN` or `IN PROGRESS`) assigned tickets |

### Tickets (`tickets`)
| Attribute | Type | Description |
| --- | --- | --- |
| `ticket_id` | `int` | Auto-incrementing sequential ticket identifier |
| `employee_id` | `int` | Reference ID of the submitting employee |
| `description` | `str` | Full text problem description |
| `category` | `str` | Assigned domain (`Network`, `Hardware`, `Software`, `Security`, `Other`) |
| `urgency` | `str` | Operational urgency level (`Low`, `Medium`, `High`) |
| `impact` | `str` | Business impact level (`Low`, `Medium`, `High`) |
| `priority` | `str` | Priority tier (`LOW`, `MEDIUM`, `HIGH`, `CRITICAL`) |
| `priority_score` | `int` | Mathematical priority score ($2 \text{ to } 6$) |
| `assigned_to` | `str` | Name of the assigned support technician |
| `status` | `str` | Current lifecycle state (`OPEN`, `IN PROGRESS`, `RESOLVED`) |
| `created_at` | `str` | Creation timestamp (`YYYY-MM-DD HH:MM:SS`) |
| `resolved_at` | `str` / `None` | Resolution timestamp (`None` while ticket remains open) |

---

## Core Algorithms

### 1. Frequency-Based Keyword Classification (`classifier.py`)
- Standardizes text to lowercase and scans against domain-specific keyword dictionaries:
  - **Network:** `wifi`, `wi-fi`, `internet`, `router`, `network`, `connection`, `lan`, `vpn`
  - **Hardware:** `keyboard`, `mouse`, `screen`, `laptop`, `printer`, `monitor`, `cpu`, `battery`
  - **Software:** `software`, `application`, `install`, `installation`, `program`, `update`, `license`
  - **Security:** `virus`, `malware`, `phishing`, `password`, `hacked`, `security`, `otp`, `unauthorized`
- Identifies the category with the highest frequency match. Defaults to `"Other"` if no keywords match.

### 2. Incident Priority Matrix (`priority.py`)
- Maps categorical levels to integer weights: $\text{Low} = 1$, $\text{Medium} = 2$, $\text{High} = 3$.
- $\text{Priority Score} = \text{Urgency Weight} + \text{Impact Weight}$.

| Score Range | Priority Tier | Operational Definition |
| :---: | :---: | :--- |
| **2 – 3** | `LOW` | Minor issue with minimal productivity impact |
| **4** | `MEDIUM` | Standard operational problem affecting a single user |
| **5** | `HIGH` | Significant impediment affecting vital business workflows |
| **6** | `CRITICAL` | Severe outage, core system failure, or security breach |

### 3. Load-Balanced Dispatching (`assignment.py`)
- Filters technician pool by domain specialization.
- Applies a greedy optimization strategy to pick the technician with the minimal active queue:
  $$\text{Target Technician} = \min(\text{candidates}, \text{key}=(\text{open\_ticket\_count}, \text{technician\_id}))$$

---

## Project Structure

```
Smart-IT-Helpdesk-Ticket-Management-System/
│
├── main.py               # Main application entry point
├── database.py           # Data access layer, CRUD operations & JSON persistence
├── classifier.py         # Keyword-based category classification engine
├── priority.py           # Urgency/Impact priority scoring module
├── assignment.py         # Technician routing & load balancing module
├── gui.py                # Desktop GUI implementation (Login, Employee, Admin)
├── helpdesk_data.json    # JSON database file (auto-seeded on first run)
└── README.md             # Complete project documentation
```

---

## Installation & Execution

### Prerequisites
- Python 3.8+ (Tkinter and standard libraries are included with standard Python installations).

### Running the Application
```powershell
python main.py
```

### Default Credentials

| Portal | User Identifier | Password |
| --- | --- | --- |
| **Employee Portal** | `1024` (or `1025`–`1028`) | `emp123` |
| **Admin / Technician Portal** | `admin` | `admin123` |

*Pre-configured Sample Employees:*
- `1024`: Amit Sharma (Sales)
- `1025`: Neha Patel (Finance)
- `1026`: Rohan Iyer (HR)
- `1027`: Sneha Reddy (Operations)
- `1028`: Vikram Singh (Marketing)

---

## Planned Enhancements

- **Security:** Salted password hashing (e.g., `bcrypt` / `argon2`) with individual user registration.
- **Client-Server Storage:** Storage adapter interface allowing seamless connection to PostgreSQL or MySQL for multi-workstation deployments.
- **Machine Learning Classification:** Supervised text classification model (TF-IDF + Logistic Regression) trained on historical incident logs.
- **Automated Notifications:** SMTP email and desktop system tray alerts on status updates.
- **Reporting & Analytics:** Incident trend visualization and CSV export functionality for monthly SLA reporting.
