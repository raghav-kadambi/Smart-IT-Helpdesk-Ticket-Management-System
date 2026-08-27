# Interview Preparation — Smart IT Helpdesk Ticket Management System

Use this file to **explain the project in your own words**. Do not memorize it word-for-word. Speak naturally.

**Honest description:** this is a **rule-based** helpdesk system. It does **not** use AI.

---

## A. 60-second project explanation

I built a desktop IT helpdesk application in Python. Employees log in, type a problem description, and choose urgency and impact. The system then does three automatic steps: it classifies the ticket into Network, Hardware, Software, Security, or Other using keyword matching; it calculates priority by adding urgency and impact scores; and it assigns the ticket to a technician based on category and who currently has the fewest open tickets. Everything is stored in SQLite. Admins can view statistics, filter tickets, and update status from OPEN to IN PROGRESS to RESOLVED. I used Tkinter for the GUI so the whole project runs locally with `python main.py` and no extra servers.

---

## B. 2-minute detailed project explanation

IT support teams receive many issues every day. If tickets are not categorized and prioritized consistently, important problems wait too long and some technicians get overloaded.

My project is a small desktop system with two roles. An employee logs in with their employee ID. They enter a description, urgency, and impact. I did not use machine learning. Classification is a dictionary of keywords. For example, wifi and router map to Network. I count matches per category and take the highest score. If nothing matches, the category is Other.

Priority is a formula. Low is 1, Medium is 2, High is 3. Score = urgency + impact. 2–3 is LOW, 4 is MEDIUM, 5 is HIGH, 6 is CRITICAL. This is easy to justify to a business user.

Assignment uses four technicians: Ravi for Network, Priya for Hardware, Arun for Software, Karthik for Security. If the category is Other, I pick the technician with the lowest open ticket count. When a ticket is saved, that count increases. When it is resolved, it decreases and `resolved_at` is set.

The database has three tables: employees, technicians, and tickets. I used Python’s built-in sqlite3 module, not an ORM, so I can explain every SQL statement. The GUI has a login screen, an employee screen to create and view own tickets, and an admin dashboard with totals and filters.

I kept the architecture in six files so each file has one job: database, classifier, priority, assignment, GUI, and main.

---

## C. Why I chose Python

- It is widely used at TCS and in interviews.
- The syntax is readable, which helps when explaining code.
- `sqlite3` and `tkinter` are built in, so the demo has almost no setup.
- I can show functions, dictionaries, loops, and SQL in one small project.

---

## D. Why I chose Tkinter

- It ships with Python. The interviewer can run it without pip packages.
- It is enough for forms, buttons, and a table (Treeview).
- A web stack (Flask + HTML) would add routing, templates, and a browser, which is extra complexity for this demo.
- I wanted to talk about desktop event-driven UI, not web frameworks.

---

## E. Why I chose SQLite

- It is a file-based database. No separate database server.
- Perfect for a single-user desktop demo.
- I can show CREATE TABLE, INSERT, SELECT with JOIN, and UPDATE.
- Data survives after the program closes.

---

## F. Why I didn’t use MySQL

MySQL needs a server process, user accounts, and installation. For a laptop demo and an interview, that is extra failure risk. SQLite is enough for one application on one machine. I would consider MySQL later if many users on different PCs needed one shared database.

---

## G. Why I didn’t use machine learning

- I do not have a large labeled dataset of tickets.
- ML would need training, accuracy metrics, and extra libraries.
- Interviewers often ask “how does it work?” Keyword counting is fully explainable.
- ML can be wrong in ways that are hard to debug in a 15-minute demo.

Keyword matching is honest and limited. I would mention ML only as a **future improvement**, not as something this project already does.

---

## H. Complete workflow

1. `main.py` starts and calls `initialize_database()`.
2. If tables are empty, sample employees, technicians, and tickets are inserted.
3. Login window opens.
4. **Employee path:** validate ID + demo password → employee dashboard.
5. Employee submits description + urgency + impact.
6. Validation: description not empty; urgency and impact selected; employee exists.
7. `classify_ticket(description)` → category.
8. `calculate_priority(urgency, impact)` → label + score.
9. `assign_technician(category)` → technician name.
10. `insert_ticket(...)` stores the row and increments `open_ticket_count`.
11. Employee table refreshes.
12. **Admin path:** dashboard loads `get_statistics()` and `get_all_tickets()`.
13. Admin can filter by status and priority.
14. Admin selects a row and updates status.
15. If status becomes RESOLVED, set `resolved_at` and decrement open count. If a resolved ticket is reopened, clear `resolved_at` and increment again.

---

## I. Every Python file

| File | Responsibility |
| --- | --- |
| `main.py` | Entry point. Creates the database, then starts the GUI. |
| `database.py` | Connect to SQLite, create tables, seed sample data, CRUD, statistics. |
| `classifier.py` | Keyword dictionary and category selection. |
| `priority.py` | Convert urgency/impact to score and label. |
| `assignment.py` | Choose technician by specialization and workload. |
| `gui.py` | Login, employee dashboard, admin dashboard. |

I avoided circular imports: `database.py` does not import classifier/assignment. The GUI calls those modules, then asks the database to save.

---

## J. Database tables

**employees** — master data for people who raise tickets. Primary key is `employee_id` (business key like 1024).

**technicians** — master data for support staff. `open_ticket_count` is denormalized on purpose so assignment is a simple “pick minimum count” without recounting every time. I still keep it consistent in insert/update code.

**tickets** — transactional data. `employee_id` is a foreign key. `resolved_at` is NULL until the ticket is finished.

---

## K. Important SQL queries used

**Create ticket**

```sql
INSERT INTO tickets (
    employee_id, description, category, urgency, impact,
    priority, priority_score, assigned_to, status, created_at, resolved_at
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);
```

**Increase technician load**

```sql
UPDATE technicians
SET open_ticket_count = open_ticket_count + 1
WHERE name = ?;
```

**Employee’s own tickets (JOIN)**

```sql
SELECT t.ticket_id, e.name AS employee_name, t.description, t.category,
       t.priority, t.assigned_to, t.status, t.created_at
FROM tickets t
JOIN employees e ON t.employee_id = e.employee_id
WHERE t.employee_id = ?
ORDER BY t.ticket_id DESC;
```

**Admin filters** — same JOIN, plus optional:

```sql
AND t.status = ?
AND t.priority = ?
```

**Dashboard counts**

```sql
SELECT COUNT(*) FROM tickets;
SELECT COUNT(*) FROM tickets WHERE status IN ('OPEN', 'IN PROGRESS');
SELECT COUNT(*) FROM tickets WHERE priority = 'CRITICAL';
SELECT COUNT(*) FROM tickets WHERE status = 'RESOLVED';
```

**Resolve ticket**

```sql
UPDATE tickets SET status = ?, resolved_at = ? WHERE ticket_id = ?;
UPDATE technicians
SET open_ticket_count = CASE
    WHEN open_ticket_count > 0 THEN open_ticket_count - 1
    ELSE 0
END
WHERE name = ?;
```

I use **parameterized queries** (`?`) to avoid SQL injection.

---

## L. Data structures used and why

| Structure | Where | Why |
| --- | --- | --- |
| Dictionary | `CATEGORY_KEYWORDS` | Category → list of keywords. O(1) lookup of a category’s word list. |
| Dictionary | `LEVEL_SCORES` | Map Low/Medium/High to 1/2/3. |
| Dictionary | `CATEGORY_TO_SPECIALIZATION` | Map ticket category to technician skill. |
| List | Keyword lists, technician candidates | Ordered collection to loop through. |
| Tuple | `min(..., key=lambda ...)` tie-break | Compare (open_count, technician_id). |
| sqlite3.Row / dict | Query results | Named fields like `ticket["status"]`. |

I did not use trees or graphs because the data is tabular. The “smart” parts are linear scans over small dictionaries.

---

## M. Time complexity of important algorithms

Assume:

- `C` = number of categories (here 4)
- `K` = keywords per category (small, about 8)
- `L` = length of the description string
- `T` = number of technicians (here 4)
- `N` = number of tickets in the table

**Classification**  
For each category, for each keyword, check `keyword in text`.  
Time: **O(C × K × L)** in the worst case (Python `in` for substrings scans the text).  
With tiny C and K this is effectively constant for an interview demo.

**Priority**  
Two dictionary lookups + addition + if/elif. **O(1)**.

**Assignment**  
Fetch matching technicians (SQL), then `min` over at most T rows. **O(T)**.

**Insert ticket**  
SQL INSERT + UPDATE. Database I/O, not a heavy CPU algorithm.

**Filter tickets**  
SQL SELECT. Time depends on SQLite and indexes. Without extra indexes, a full scan is **O(N)**. For this demo N is small.

**Space**  
Keyword dictionary is **O(C × K)**. Tickets live on disk, not all in memory except the current table view.

---

## N. Possible limitations

- Login is a demo only (shared employee password, hardcoded admin).
- Keyword matching fails on spelling errors (`wi-fi` vs `wify`) and on new slang.
- Tie-breaking always prefers Network if scores are equal.
- `open_ticket_count` could drift if someone edits the DB by hand.
- SQLite is not ideal for many simultaneous writers on a network share.
- No attachments, comments, or SLA timers.
- Admin and technician share one login; a technician cannot see “only my tickets.”
- GUI is single-process; closing the window ends the session.

---

## O. Future improvements

Label these clearly as **future**, not current features:

1. Hash passwords (e.g. SHA-256 or better, unique password per user).
2. Technician-specific login and inbox.
3. Audit log of status changes.
4. Optional ML classifier **after** collecting labeled tickets (future enhancement only).
5. Search box and date-range filters.
6. Export to CSV.
7. MySQL/PostgreSQL if the app must be multi-user on a network.

---

## P. Likely TCS Prime interview questions (30+)

For each item: the question, a short answer, a likely follow-up, and the follow-up answer.

### 1. Python — What does this project do?

**Answer:** It is a desktop helpdesk that stores tickets in SQLite and uses rules to classify, prioritize, and assign them.

**Follow-up:** Is it an AI project?  
**Follow-up answer:** No. Classification is keyword matching. ML would be a future idea if we had labeled data.

### 2. Python — Why split the code into multiple files?

**Answer:** Each file has one responsibility. That is easier to test, explain, and change. If I change priority rules, I only edit `priority.py`.

**Follow-up:** What is this principle called?  
**Follow-up answer:** Separation of concerns. It is also similar to a simple layered design: GUI → logic → database.

### 3. Python — Where did you use functions vs classes?

**Answer:** Database, classifier, priority, and assignment are functions. GUI uses classes because each window has state (entry widgets, the logged-in employee).

**Follow-up:** Could the whole app be functions only?  
**Follow-up answer:** Yes, but window state is cleaner as an object with `self.tree` and `self.employee`.

### 4. OOP — What is encapsulation in your GUI?

**Answer:** `EmployeeDashboard` keeps widgets and the employee dictionary on `self`. Other screens do not touch those widgets directly.

**Follow-up:** Did you use inheritance?  
**Follow-up answer:** No. I did not need a class hierarchy for three screens. Adding inheritance without a reason would be over-engineering.

### 5. OOP — What is the difference between a class and a module here?

**Answer:** A module is a `.py` file of functions and data. A class groups data + behavior for one window instance.

**Follow-up:** Is `CATEGORY_KEYWORDS` a class attribute?  
**Follow-up answer:** No. It is a module-level dictionary, which is fine for read-only config.

### 6. DSA — Why a dictionary for keywords?

**Answer:** I need to map a category name to its word list. A dict is the natural key-value structure.

**Follow-up:** Why not a list of tuples?  
**Follow-up answer:** A list would work, but a dict makes the category the key and is clearer when explaining the algorithm.

### 7. DSA — How do you pick the technician with the lowest load?

**Answer:** I load candidate technicians and use Python `min` with a key of `(open_ticket_count, technician_id)`.

**Follow-up:** What is the complexity?  
**Follow-up answer:** O(T) to scan technicians. T is tiny. If T were huge, I could keep a heap, but that is unnecessary here.

### 8. DSA — How does `keyword in text` work?

**Answer:** It searches for a substring in the description.

**Follow-up:** What is a drawback?  
**Follow-up answer:** Short words can false-match, and typos are missed. A real system might use tokenization or a better matcher later.

### 9. SQL — Why parameterized queries?

**Answer:** User text is passed as `?` parameters, not concatenated into SQL. That reduces SQL injection risk.

**Follow-up:** Show a bad pattern.  
**Follow-up answer:** `"... WHERE id = " + user_input` is dangerous. Always bind parameters.

### 10. SQL — Why JOIN employees and tickets?

**Answer:** Tickets store `employee_id` only. JOIN fetches the employee name for the table.

**Follow-up:** What kind of JOIN?  
**Follow-up answer:** INNER JOIN. Every ticket must belong to an existing employee because of the foreign key.

### 11. SQL — What is a primary key vs foreign key?

**Answer:** Primary key uniquely identifies a row (`ticket_id`, `employee_id`). Foreign key (`tickets.employee_id`) must match `employees.employee_id`.

**Follow-up:** What happens if you insert a ticket for employee 9999?  
**Follow-up answer:** SQLite rejects it when foreign keys are on (`PRAGMA foreign_keys = ON`), and the GUI also checks the employee exists first.

### 12. DBMS — SQLite vs MySQL?

**Answer:** SQLite is embedded in the app as a file. MySQL is a client-server database. I used SQLite for a local demo.

**Follow-up:** ACID?  
**Follow-up answer:** SQLite transactions support commit and rollback. I use rollback if an insert fails so the technician count does not update without a ticket.

### 13. DBMS — What is normalization in your schema?

**Answer:** Employees and technicians are separate from tickets, so names are not typed repeatedly as the only source of truth. Tickets reference `employee_id`.

**Follow-up:** You store `assigned_to` as a name. Is that normalized?  
**Follow-up answer:** It is a simplification. A stricter design would store `technician_id` as a foreign key. I stored the name to keep queries and the GUI table simple for the interview.

### 14. DBMS — Why keep `open_ticket_count` on technicians?

**Answer:** Assignment needs the current load quickly. I update it when tickets are created or resolved.

**Follow-up:** Could you compute COUNT(*) instead?  
**Follow-up answer:** Yes: `SELECT COUNT(*) FROM tickets WHERE assigned_to = ? AND status IN ('OPEN','IN PROGRESS')`. That avoids denormalization. I stored the count to show a simple load-balancing field.

### 15. OS — What happens when you run `python main.py`?

**Answer:** The OS starts a Python process. It opens or creates `helpdesk.db`, then Tkinter opens a window and waits in an event loop.

**Follow-up:** What is an event loop?  
**Follow-up answer:** The GUI waits for events (click, type). Callbacks like `_submit_ticket` run when the user clicks Submit.

### 16. OS — File vs database?

**Answer:** I could have saved tickets as JSON, but SQLite gives querying, filters, and joins.

**Follow-up:** Where is the DB file?  
**Follow-up answer:** In the `smart_helpdesk` folder, next to the scripts. It is just a file on disk.

### 17. OS — Is this multi-threaded?

**Answer:** No. Tkinter and sqlite3 calls run on the main thread. That is enough for this demo.

**Follow-up:** When would you use threads?  
**Follow-up answer:** If a slow network call blocked the UI. This app has no network I/O.

### 18. Computer Networks — Does this app use the network?

**Answer:** No. No HTTP APIs, no cloud. Login and data are local.

**Follow-up:** How would it work on a company network?  
**Follow-up answer:** Put the database on a server (MySQL) and run clients against it, or build a web app. That is a future architecture change.

### 19. Computer Networks — Relate tickets to real IT issues.

**Answer:** Network tickets are like connectivity problems (Wi-Fi, VPN). Security tickets are like phishing. The category is only a label for routing, not a packet-level diagnosis.

**Follow-up:** What is phishing?  
**Follow-up answer:** A social-engineering attack, often email, trying to steal a password. My system only detects the word “phishing” in the text.

### 20. Software engineering — What is the SDLC of this project?

**Answer:** Requirements (helpdesk features) → simple design (6 modules, 3 tables) → implementation → manual testing of classify/priority/status → documentation (README).

**Follow-up:** Did you write unit tests?  
**Follow-up answer:** I tested modules by running Python checks on classify, priority, insert, and status update. Formal pytest files would be a next step.

### 21. Software engineering — How do you handle errors?

**Answer:** Validate empty description, missing urgency/impact, bad login, unknown employee ID. Database errors are caught and shown in a message box. Invalid login shows an error dialog.

**Follow-up:** What is the difference between validation and exception handling?  
**Follow-up answer:** Validation checks user input before work starts. Exceptions catch unexpected failures such as a SQLite error.

### 22. Software engineering — How would you test classification?

**Answer:** Give sample sentences: Wi-Fi → Network, keyboard → Hardware, no keywords → Other, and a tie case.

**Follow-up:** What is a tie case in your code?  
**Follow-up answer:** “Laptop cannot connect to WiFi” matches Hardware and Network once each. I pick Network because of a fixed category order.

### 23. Project architecture — Describe the architecture.

**Answer:** Presentation (`gui.py`), business rules (`classifier`, `priority`, `assignment`), data (`database.py` + SQLite). `main.py` wires startup.

**Follow-up:** Is this MVC?  
**Follow-up answer:** It is similar: GUI is the view, functions are the controller/logic, SQLite is the model. I did not implement a strict MVC framework.

### 24. Project architecture — Why not Flask?

**Answer:** Flask needs a browser and a running server. Tkinter is one process and matches “desktop helpdesk demo.”

**Follow-up:** Pros of Flask?  
**Follow-up answer:** Multiple users, no desktop install, easier remote access. I accepted that tradeoff for simplicity.

### 25. Python — What is `if __name__ == "__main__"`?

**Answer:** The code inside runs only when the file is executed directly, not when imported.

**Follow-up:** Why does that matter?  
**Follow-up answer:** `main.py` can be imported in tests without opening the GUI.

### 26. Python — What is `row_factory = sqlite3.Row`?

**Answer:** Rows behave like dictionaries: `row["status"]` instead of `row[10]`.

**Follow-up:** Why is that better?  
**Follow-up answer:** Column order can change. Names are readable in an interview.

### 27. SQL — Difference between WHERE and JOIN?

**Answer:** JOIN combines tables. WHERE filters rows (status = OPEN, employee_id = 1024).

**Follow-up:** Filter in Python vs SQL?  
**Follow-up answer:** SQL is better so we do not load every ticket into memory. I filter status and priority in the SELECT.

### 28. DBMS — What does AUTOINCREMENT do?

**Answer:** `ticket_id` and `technician_id` are generated by SQLite.

**Follow-up:** Why is employee_id not autoincrement?  
**Follow-up answer:** It is a company ID (1024). That is a natural/business key, not a surrogate key.

### 29. OS — What is a deadlock? Does your app have one?

**Answer:** Deadlock is when two processes wait on each other for locks. This app is single-user and single-threaded, so deadlock is not a practical issue.

**Follow-up:** SQLite locking?  
**Follow-up answer:** SQLite can lock the database file if two programs write at once. I run only one GUI at a time.

### 30. Computer Networks — OSI model vs this project?

**Answer:** This app does not implement the OSI stack. If we later used HTTP, that would sit around Layer 7. Today it is a local application.

**Follow-up:** Then why mention networks?  
**Follow-up answer:** The ticket *categories* include Network as a business domain (Wi-Fi, VPN), not as a networking protocol I implemented.

### 31. Python — Mutable default arguments — did you avoid them?

**Answer:** Yes. I do not use `def f(data=[])`. Ticket data is a new dict each submit.

**Follow-up:** Why are mutable defaults bad?  
**Follow-up answer:** The same list/dict is reused across calls, which causes bugs.

### 32. DSA — Stable assignment / fairness?

**Answer:** Lowest open count is a simple load balancer. It is not globally optimal scheduling.

**Follow-up:** What if all counts are equal?  
**Follow-up answer:** Smaller `technician_id` wins, so assignment is deterministic.

### 33. Software engineering — What is a use case?

**Answer:** Example: “Employee submits a Wi-Fi issue and sees it assigned to Ravi with CRITICAL priority.”

**Follow-up:** Actor?  
**Follow-up answer:** Employee and Admin/Technician.

### 34. DBMS — NULL vs empty string for `resolved_at`?

**Answer:** I store NULL until resolved, then a timestamp string. NULL means “not resolved yet.”

**Follow-up:** How do you query unresolved tickets?  
**Follow-up answer:** `WHERE resolved_at IS NULL` or `WHERE status != 'RESOLVED'`.

### 35. Python — Exception hierarchy in your code?

**Answer:** `ValueError` for business rules (bad urgency, ticket not found). `sqlite3.Error` for database failures. The GUI catches both.

**Follow-up:** Would you create custom exceptions?  
**Follow-up answer:** Only if the app grew. For this size, ValueError is enough.

---

## Extra talking points (short)

- **Demo credentials** are shown on the login screen on purpose. This is not production security.
- **Sample data** runs only when tables are empty, so restarting the app does not duplicate employees.
- **Status values** are stored as text: OPEN, IN PROGRESS, RESOLVED.
- If asked “scale this to 10,000 users,” say: web frontend, server API, MySQL, real auth, indexes on `status` and `employee_id`, and do not use a desktop Tkinter client as the only interface.

---

## Suggested live demo script (2–3 minutes)

1. Run `python main.py`.
2. Log in as **1024 / emp123**.
3. Submit: “My laptop cannot connect to WiFi”, High, High.
4. Show the popup: category, priority CRITICAL, assigned technician.
5. Logout. Log in as **admin / admin123**.
6. Point to Total / Open / Critical / Resolved.
7. Filter Priority = CRITICAL.
8. Set the new ticket to IN PROGRESS, then RESOLVED.
9. Say: resolving sets `resolved_at` and reduces the technician’s open count.

Practice this until you can do it without reading notes.
