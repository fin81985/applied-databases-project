import mysql.connector
from neo4j import GraphDatabase
import config

def get_connection():
    return mysql.connector.connect(
        host=config.MYSQL_HOST,
        user=config.MYSQL_USER,
        password=config.MYSQL_PASSWORD,
        database=config.MYSQL_DB
    )


def get_neo4j_driver():
    return GraphDatabase.driver(
        config.NEO4J_URI,
        auth=(config.NEO4J_USER, config.NEO4J_PASSWORD)
    )
    


def test_connection():
    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT COUNT(*) FROM attendee")
        result = cursor.fetchone()

        print("MySQL connected successfully!")
        print("Number of attendees:", result[0])

        conn.close()

    except Exception as e:
        print("MySQL Error:", e)


def test_neo4j():
    try:
        driver = get_neo4j_driver()

        with driver.session() as session:
            result = session.run("MATCH (a:Attendee) RETURN COUNT(a) AS total")
            count = result.single()["total"]

            print("Neo4j connected successfully!")
            print("Number of attendee nodes:", count)

        driver.close()

    except Exception as e:
        print("Neo4j Error:", e)


if __name__ == "__main__":
    test_connection()
    print()
    test_neo4j()