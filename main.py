from db_mysql import get_connection
from db_neo4j import get_neo4j_driver

rooms_cache = None


def view_speakers_sessions():
    print("Option 1 not built yet.")


def view_attendees_by_company():
    print("Option 2 not built yet.")


def add_new_attendee():
    print("Option 3 not built yet.")


def view_connected_attendees():
    print("Option 4 not built yet.")


def add_attendee_connection():
    print("Option 5 not built yet.")


def view_rooms():
    print("Option 6 not built yet.")


def main():
    while True:
        print("\n--- Conference Management App ---")
        print("1. View Speakers & Sessions")
        print("2. View Attendees by Company")
        print("3. Add New Attendee")
        print("4. View Connected Attendees")
        print("5. Add Attendee Connection")
        print("6. View Rooms")
        print("x. Exit")

        choice = input("Enter option: ").strip().lower()

        if choice == "1":
            view_speakers_sessions()
        elif choice == "2":
            view_attendees_by_company()
        elif choice == "3":
            add_new_attendee()
        elif choice == "4":
            view_connected_attendees()
        elif choice == "5":
            add_attendee_connection()
        elif choice == "6":
            view_rooms()
        elif choice == "x":
            print("Goodbye.")
            break
        else:
            continue


if __name__ == "__main__":
    main()