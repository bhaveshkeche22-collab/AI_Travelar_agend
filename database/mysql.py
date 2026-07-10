from dotenv import load_dotenv
load_dotenv()
import os
import requests
import pymysql

def get_connection():
    return pymysql.connect(
        host=os.getenv("MYSQL_HOST"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE"),
        cursorclass=pymysql.cursors.DictCursor
    )

def save_chat_history(user_message: str, ai_response: str):
    conn = get_connection()
    cursor = conn.cursor()

    sql = """
    INSERT INTO chat_history(user_message, ai_response)
    VALUES(%s, %s)
    """

    cursor.execute(sql, (user_message, ai_response))
    conn.commit()

    cursor.close()
    conn.close()


def save_trip(destination: str, budget: str, days: int):
    conn = get_connection()
    cursor = conn.cursor()

    sql = """
    INSERT INTO trips(destination, budget, days)
    VALUES(%s, %s, %s)
    """

    cursor.execute(sql, (destination, budget, days))
    conn.commit()

    cursor.close()
    conn.close()

def get_chat_history():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM chat_history
        ORDER BY id DESC
    """)

    history = cursor.fetchall()

    cursor.close()
    conn.close()

    return history

def get_previous_trips():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM trips
        ORDER BY id DESC
    """)

    trips = cursor.fetchall()

    cursor.close()
    conn.close()

    return trips