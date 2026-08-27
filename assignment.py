"""
assignment.py
-------------
Assigns a technician based on ticket category and current open workload.
"""

import database

# Each IT category is handled by a matching specialization.
CATEGORY_TO_SPECIALIZATION = {
    "Network": "Network",
    "Hardware": "Hardware",
    "Software": "Software",
    "Security": "Security",
}


def assign_technician(category):
    """
    Return the technician name who should receive this ticket.

    Algorithm:
    1. If category is Network/Hardware/Software/Security, look at technicians
       with that specialization.
    2. If category is Other (or no specialist exists), consider all technicians.
    3. Assign the ticket to the technician with the lowest open_ticket_count.
    4. If two technicians have the same load, pick the smaller technician_id
       so the result is predictable.
    """
    specialization = CATEGORY_TO_SPECIALIZATION.get(category)

    if specialization:
        candidates = database.get_technicians_by_specialization(specialization)
    else:
        candidates = []

    # "Other" tickets, or a missing specialist, go to general support:
    # the technician who currently has the fewest open tickets.
    if not candidates:
        candidates = database.get_all_technicians()

    if not candidates:
        raise ValueError("No technicians are available in the system.")

    chosen = min(
        candidates,
        key=lambda tech: (tech["open_ticket_count"], tech["technician_id"]),
    )
    return chosen["name"]
