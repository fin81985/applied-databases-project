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
            print("Invalid gender input. Please enter either Male or Female.")
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

        # This sql query inserts a new attendee into the attendee table with the provided details. 
        # If the insertion is successful, print a success message. 
        # 
        # If there is an error during insertion, print the error message.
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
    while True:
        attendee_input = input("Enter Attendee ID: ").strip()

        if not attendee_input.isdigit():
            print("Invalid attendee ID")
            continue

        attendee_id = int(attendee_input)

        try:
            # First check MySQL
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT attendeeName FROM attendee WHERE attendeeID = %s",
                (attendee_id,)
            )
            attendee = cursor.fetchone()
            conn.close() 
            # This sql query checks if the attendee ID exists in the attendee table. 
            # If it does not, print a message and return to the main menu. 
            # Otherwise, store the attendee name for later use.

            if attendee is None:
                print("Attendee does not exist")
                break

            attendee_name = attendee[0]

            # Then check Neo4j connections
            driver = get_neo4j_driver()
            with driver.session() as session:
                result = session.run("""
                    MATCH (a:Attendee {AttendeeID: $attendee_id})-[:CONNECTED_TO]-(b:Attendee)
                    RETURN b.AttendeeID AS connected_id
                    ORDER BY connected_id
                """, attendee_id=attendee_id)
                # This neo4j query matches the attendee node with the specified attendee ID and finds all connected attendees through the CONNECTED_TO relationship. 
                # It returns the connected attendee IDs ordered by ID.

                connected_ids = [record["connected_id"] for record in result]

            driver.close()

            print(f"\nAttendee: {attendee_name}")

            if not connected_ids:
                print("No connections")
                break

            conn = get_connection()
            cursor = conn.cursor()

            print("\nConnected Attendees:")
            for connected_id in connected_ids:
                cursor.execute(
                    "SELECT attendeeName FROM attendee WHERE attendeeID = %s",
                    (connected_id,)
                ) 
                # This sql query retrieves the name of each connected attendee based on their attendee ID. 
                # If the attendee ID does not exist, it will return "Unknown".
                result = cursor.fetchone()
                connected_name = result[0] if result else "Unknown"
                print(f"{connected_id} - {connected_name}")

            conn.close()
            break

        except Exception as e:
            print("Error viewing connected attendees:", e)
            break

# option 5 - prompts user to enter the name of an attendee to connect with, then creates a connection in Neo4j.
def add_attendee_connection():
    while True:
        id1_input = input("Enter first Attendee ID: ").strip()
        id2_input = input("Enter second Attendee ID: ").strip()

        # Must both be numeric
        if not id1_input.isdigit() or not id2_input.isdigit():
            print("Invalid attendee ID")
            continue

        id1 = int(id1_input)
        id2 = int(id2_input)

        # Cannot connect attendee to themself
        if id1 == id2:
            print("An attendee cannot be CONNECTED_TO themself")
            continue

        try:
            # Check both exist in MySQL
            conn = get_connection()
            cursor = conn.cursor()

            cursor.execute(
                "SELECT attendeeName FROM attendee WHERE attendeeID = %s",
                (id1,)
            ) # This sql query checks if the first attendee ID exists in the attendee table. 
            #If it does not, print a message and return to the main menu. Otherwise, store the attendee name for later use.
            attendee1 = cursor.fetchone()

            cursor.execute(
                "SELECT attendeeName FROM attendee WHERE attendeeID = %s",
                (id2,)
            ) # This sql query checks if the second attendee ID exists in the attendee table. 
            # If it does not, print a message and return to the main menu. Otherwise, store the attendee name for later use.
            attendee2 = cursor.fetchone()

            conn.close()

            if attendee1 is None or attendee2 is None:
                print("One or both attendees do not exist")
                continue

            # Check existing Neo4j connection
            driver = get_neo4j_driver()
            with driver.session() as session:
                existing = session.run("""
                    MATCH (a:Attendee {AttendeeID: $id1})-[:CONNECTED_TO]-(b:Attendee {AttendeeID: $id2})
                    RETURN a
                """, id1=id1, id2=id2).single()# This neo4j query checks if there is already a CONNECTED_TO relationship between the two specified attendees. 
                # If there is, print a message and return to the main menu. Otherwise, proceed to create the connection.

                if existing:
                    print("These attendees are already connected")
                    driver.close()
                    continue

                # Make sure nodes exist, then create relationship
                session.run("""
                    MERGE (a:Attendee {AttendeeID: $id1})
                    MERGE (b:Attendee {AttendeeID: $id2})
                    MERGE (a)-[:CONNECTED_TO]-(b)
                """, id1=id1, id2=id2)# This neo4j query uses MERGE to ensure that nodes for both attendees exist 
                # then creates a CONNECTED_TO relationship between them.

            driver.close()
            print(f"Attendee {id1} is now CONNECTED_TO attendee {id2}")
            break

        except Exception as e:
            print("Error adding attendee connection:", e)
            break

# option 6 - lists all rooms and their details. Caches results to avoid repeated database queries.
def view_rooms():
    global rooms_cache

    if rooms_cache is None:
        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT roomID, roomName, capacity FROM room") # This sql query retrieves the room ID, room name, and capacity for all rooms in the room table. 
            # The results are stored in the rooms_cache variable to avoid repeated database queries on subsequent calls to this function.
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

# options 7 - prompts user for attendee name (or part of name) and lists matching attendees. Uses SQL query with LIKE operator to search for attendees by name.
def search_attendee():
    name = input("Enter attendee name (or part of name): ").strip()

    try:
        conn = get_connection()
        cursor = conn.cursor()

        query = """
        SELECT attendeeID, attendeeName, attendeeDOB
        FROM attendee
        WHERE attendeeName LIKE %s
        ORDER BY attendeeName
        """

        cursor.execute(query, ("%" + name + "%",))
        results = cursor.fetchall()

        if results:
            print("\n--- Matching Attendees ---")
            for row in results:
                print(f"ID: {row[0]}")
                print(f"Name: {row[1]}")
                print(f"DOB: {row[2]}")
                print("-------------------")
        else:
            print("No attendees found")

        conn.close()

    except Exception as e:
        print("Error searching attendees:", e)
        
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
        print("7. Search Attendee by Name")
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
        elif choice == "7":
            search_attendee()
        elif choice == "x":
            print("Goodbye.")
            break


if __name__ == "__main__":
    main()