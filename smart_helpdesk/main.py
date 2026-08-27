"""
main.py
-------
Application entry point.

Run from this folder:
    python main.py
"""

import database
import gui


def main():
    try:
        database.initialize_database()
    except Exception as error:
        print("Could not initialize the database:", error)
        return

    gui.start_login()


if __name__ == "__main__":
    main()
