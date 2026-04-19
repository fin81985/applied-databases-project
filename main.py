from db_mysql import get_connection
from db_neo4j import get_neo4j_driver

rooms_cache = None

# options 1 - prompts user for speaker name (or part of name) and lists matching speakers, their sessions, and room details. Uses SQL query to search for speakers and join with room details.
def view_speakers_sessions():
    speaker_search = input("Enter speaker name (or part of name): ").strip()

    try:
        conn = get_connection()
        cursor = conn.cursor()
        
# This sql query joins the session and room tables to get the speaker name, session title, and room name for sessions 
# where the speaker name matches the search string. 
# The results are ordered by speaker name and session title.

        query = """
        SELECT s.speakerName, s.sessionTitle, r.roomName
        FROM session s
        JOIN room r ON s.roomID = r.roomID
        WHERE s.speakerName LIKE %s
        ORDER BY s.speakerName, s.sessionTitle
        """

        cursor.execute(query, ("%" + speaker_search + "%",))
        results = cursor.fetchall()

        if results:
            print("\n--- Matching Speakers & Sessions ---")
            for row in results:
                print(f"Speaker: {row[0]}")
                print(f"Session: {row[1]}")
                print(f"Room: {row[2]}")
                print("-------------------")
        else:
            print("No speakers match search string")

        conn.close()

    except Exception as e:
        print("Error loading speaker sessions:", e)

# option 2 - groups attendees by company and lists them.
def view_attendees_by_company():
    while True:
        company_input = input("Enter Company ID: ").strip()

        try:
            company_id = int(company_input)
            if company_id <= 0:
                print("Invalid company ID")
                continue
        except ValueError:
            print("Invalid company ID")
            continue

        try:
            conn = get_connection()
            cursor = conn.cursor()
            
# This sql query selects the company name from the company table where the company ID matches the user input.
            cursor.execute(
                "SELECT companyName FROM company WHERE companyID = %s",
                (company_id,)
            )
            company = cursor.fetchone()

            if company is None:# If the company ID does not exist in the database, print a message and return to the main menu.
                print("Company does not exist")
                conn.close()
                continue

            print(f"\nCompany: {company[0]}")
            
# This sql query joins the attendee, registration, session, and room tables to get the attendee name, DOB, session title, speaker name, and room name for attendees who are registered for sessions and belong to the specified company. 
# The results are ordered by attendee
            query = """
            SELECT 
                a.attendeeName,
                a.attendeeDOB,
                s.sessionTitle,
                s.speakerName,
                r.roomName
            FROM attendee a
            JOIN registration reg ON a.attendeeID = reg.attendeeID
            JOIN session s ON reg.sessionID = s.sessionID
            JOIN room r ON s.roomID = r.roomID
            WHERE a.attendeeCompanyID = %s
            ORDER BY a.attendeeName, s.sessionTitle
            """

            cursor.execute(query, (company_id,))
            results = cursor.fetchall()# If there are no attendees for the specified company, print a message and return to the main menu. Otherwise, print the attendee details and their sessions.

            if not results:
                print("No attendees for this company")
                conn.close()
                break

            print("\n--- Attendees and Sessions ---")
            for row in results:
                print(f"Attendee: {row[0]}")
                print(f"DOB: {row[1]}")
                print(f"Session: {row[2]}")
                print(f"Speaker: {row[3]}")
                print(f"Room: {row[4]}")
                print("-------------------")

            conn.close()
            break

        except Exception as e:
            print("Error loading attendees by company:", e)
            break

# option 3 - prompts user for attendee details and adds them to the database.
def add_new_attendee():
    try:
        conn = get_connection()
        cursor = conn.cursor()

        attendee_id = input("Enter Attendee ID: ").strip()
        attendee_name = input("Enter Attendee Name: ").strip()
        attendee_dob = input("Enter Attendee DOB (YYYY-MM-DD): ").strip()
        attendee_gender = input("Enter Gender (Male/Female): ").strip()
        company_id = input("Enter Company ID: ").strip()

        # Check gender
        if attendee_gender not in ["Male", "Female"]:
            print("Invalid gender")
            conn.close()
            return

        # Check duplicate attendee ID
        cursor.execute(
            "SELECT attendeeID FROM attendee WHERE attendeeID = %s",
            (attendee_id,)# This sql query checks if the attendee ID already exists in the attendee table. If it does, print a message and return to the main menu.
        )
        if cursor.fetchone() is not None:
            print("Attendee ID already exists")
            conn.close()
            return

        # Check company exists
        cursor.execute(
            "SELECT companyID FROM company WHERE companyID = %s",
            (company_id,)# This sql query checks if the company ID exists in the company table. If it does not, print a message and return to the main menu.
        )
        if cursor.fetchone() is None:
            print("Invalid Company ID")
            conn.close()
            return

        # This sql query inserts a new attendee into the attendee table with the provided details. If the insertion is successful, print a success message. If there is an error during insertion, print the error message.
        query = """
        INSERT INTO attendee (
            attendeeID,
            attendeeName,
            attendeeDOB,
            attendeeGender,
            attendeeCompanyID
        )
        VALUES (%s, %s, %s, %s, %s)
        """

        cursor.execute(query, (
            attendee_id,
            attendee_name,
            attendee_dob,
            attendee_gender,
            company_id
        ))
        conn.commit()

        print("Attendee successfully added")
        conn.close()

    except Exception as e:
        print("Error:", e)

# option 4 - lists attendees connected to the user (based on connections in Neo4j).
def view_connected_attendees():
    print("Option 4 not built yet.")

# option 5 - prompts user to enter the name of an attendee to connect with, then creates a connection in Neo4j.
def add_attendee_connection():
    print("Option 5 not built yet.")

# option 6 - lists all rooms and their details. Caches results to avoid repeated database queries.
def view_rooms():
    global rooms_cache

    if rooms_cache is None:
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT roomID, roomName, capacity FROM room")
            rooms_cache = cursor.fetchall()
            conn.close()
        except Exception as e:
            print("Error loading rooms:", e)
            return

    print("\n--- Rooms ---")
    for room in rooms_cache:
        print(f"Room ID: {room[0]}")
        print(f"Room Name: {room[1]}")
        print(f"Capacity: {room[2]}")
        print("-------------------")

# Main menu loop that prompts user for options and calls corresponding functions. Continues until user chooses to exit.
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