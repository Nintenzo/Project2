from dotenv import load_dotenv
from datetime import datetime
import sqlite3
import json
import os


load_dotenv()
def create_db_users():
    conn = sqlite3.connect("circle_users.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        password TEXT,
        final_identity TEXT,
        original_identity TEXT,
        pronouns TEXT,
        bio TEXT,
        headline TEXT,
        location TEXT,
        avatar TEXT,
        remember_user_token TEXT,
        user_session_identifier TEXT,
        memeber_id INTEGER,
        public_uid TEXT,
        community_member_id INTEGER,
        introduction TEXT,
        introduction_date TEXT
        role TEXT DEFAULT 'member'
    )
    """)
    return conn, cursor


def insert_users(name, email, password, final_identity, original_identity, pronouns, bio, headline, location, avatar, remember_user_token, user_session_identifier, memeber_id, public_uid, community_member_id, introduction, introduction_date):
    conn, cursor = create_db_users()
    try:
        cursor.execute("""
        INSERT INTO users (name, email, password, final_identity, original_identity, pronouns, bio, headline, location, avatar, remember_user_token, user_session_identifier, memeber_id, public_uid, community_member_id, introduction, introduction_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)

        """, (name, email, password, final_identity, original_identity, pronouns, bio, headline, location, avatar, remember_user_token, user_session_identifier, memeber_id, public_uid, community_member_id, introduction, introduction_date))
        conn.commit()
        print("Data inserted successfully!")
    except sqlite3.Error as e:
        print(f"Error inserting data: {e}")
    return


def fetch_introduction():
    conn, cursor = create_db_users()
    cursor.execute("""SELECT 
                   email, name, headline,
                   location, introduction_date
                   FROM users
                   WHERE introduction = True""")
    
    result = cursor.fetchall()
    return result


def fetch_inappropriate_posts():
    conn, cursor = create_post_db()
    cursor.execute("""SELECT 
                   email, ai_title,
                   post_id
                   FROM posts
                   WHERE post_category = 'inappropriate'""")
    
    result = cursor.fetchall()
    return result


def update_introduction(email):
    conn, cursor = create_db_users()
    cursor.execute("""
                UPDATE users
                SET introduction = false
                WHERE email = ?
            """, (email,))
    conn.commit()
    print('Introduction Updated')


def update_inappropriate(post_id):
    conn, cursor = create_post_db()
    array = json.dumps([])
    cursor.execute(f"""
                UPDATE posts
                SET post_category = 'done', needed_likes = '{array}', needed_comments = '{array}'
                WHERE post_id = ?
            """, (post_id,))
    conn.commit()
    print('Category Updated')


def create_db_space():
    conn = sqlite3.connect("spaces.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS spaces (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        space_name TEXT NOT NULL,
        original TEXT NOT NULL,
        space_id INTEGER NOT NULL,
        keywords TEXT NOT NULL,
        context TEXT NOT NULL
    )
    """)
    return conn, cursor


def insert_space(space_name, original, space_id, keywords, context):
    conn, cursor = create_db_space()
    try:

        cursor.execute("""
        INSERT INTO spaces (space_name, original, space_id, keywords, context)
        VALUES (?, ?, ?, ?, ?)

        """, (space_name, original, space_id, keywords, context))
        conn.commit()
        print("Data inserted successfully!")
    except sqlite3.Error as e:
        print(f"Error inserting data: {e}")
    return


def fetch_spaces_id(x):
    conn, cursor = create_db_space()
    cursor = conn.cursor()
    data = cursor.execute(f"""
    SELECT {x} FROM spaces
    """)
    return data


def create_post_db():
    conn = sqlite3.connect("reddit_scrap.db")
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT,
        original_title TEXT,
        original_description TEXT,
        ai_title TEXT,
        ai_description TEXT,
        post_id INTEGER,
        space_id INTEGER,
        links TEXT NOT NULL,
        needed_likes INTEGER,
        needed_comments INTEGER,
        post_category TEX,
        last_updated TEXT DEFAULT "2000-01-1"
    )
    """)
    return conn, cursor


def insert_post(email, original_title, original_description, ai_title, ai_description, post_id, space_id, links, needed_likes, needed_comments, post_category):
    conn, cursor = create_post_db()
    try:

        cursor.execute("""
        INSERT INTO posts (email, original_title, original_description, ai_title, ai_description, post_id, space_id, links, needed_likes, needed_comments, post_category)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)

        """, (email, original_title, original_description, ai_title, ai_description, post_id, space_id, links, needed_likes, needed_comments, post_category))
        conn.commit()
        print("Data inserted successfully!")
    except sqlite3.Error as e:
        print(f"Error inserting data: {e}")
    return


def fetch_posts(intro=False):
	introduction_space_id = os.getenv('INTRODUCTION_SPACE_ID')
	conn, cursor = create_post_db()

	cursor.execute(f"""SELECT post_id, space_id, needed_likes, needed_comments FROM posts WHERE last_updated < '{datetime.now().date()}'""")
	all_posts = cursor.fetchall()

	filtered_posts = []

	for post_id, space_id, likes_json, comments_json in all_posts:
		try:
			likes = json.loads(likes_json)

			if not isinstance(likes, list) or not all(isinstance(x, (int, float)) for x in likes):
				continue

			if not any(like > 0 for like in likes):
				continue

		except (json.JSONDecodeError, TypeError):
			continue

		if intro and str(post_id) == str(introduction_space_id):
			continue

		filtered_posts.append((post_id, space_id, likes_json, comments_json))

	return filtered_posts

def add_col(db, table, col, type, default):
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    cursor.execute(f"""ALTER TABLE {table}
                   ADD COLUMN {col} {type} DEFAULT {default }""")
    conn.commit()
    conn.close() 


def fetch_post_byID(post_id):
    conn, cursor = create_post_db()
    cursor.execute(f"""
    SELECT * FROM posts
    WHERE post_id = {post_id}""")
    result = cursor.fetchone()
    return result


def check_if_posted(link, cursor):
    """Checks if a post with the given link and a non-null post_id exists."""
    sql = (
        "SELECT EXISTS (SELECT 1 FROM posts "
        "WHERE links = ? AND post_id IS NOT NULL)"
    )
    try:
        cursor.execute(sql, (link,))
        exists = cursor.fetchone()[0]
        return exists == 1
    except sqlite3.Error as e:
        print(f"Error checking link existence: {e}")
        return False


def get_post_data(post_id):
    """Fetches post data by post_id."""
    conn, cursor = create_post_db()
    cursor.execute("""
    SELECT email, post_category, ai_title, 
    ai_description FROM posts
    WHERE post_id = ?
    """, (post_id,))
    result = cursor.fetchone()
    conn.close()
    return result


def last_updater(post_id):
    conn, cursor = create_post_db()
    cursor.execute("""
    UPDATE posts 
    SET last_updated = ?
    WHERE post_id = ? """, (datetime.now().date(),post_id,))
    conn.commit()
    conn.close()

def decrement_likes_comments(post_id, value, decrement=1):
    conn, cursor = create_post_db()
    cursor.execute(f"SELECT {value} FROM posts WHERE post_id = ?", (post_id,))
    array = cursor.fetchone()
    array = json.loads(array[0])
    try:
        array[0] -= decrement
    except Exception:
        return
    if array[0] <= 0:
        array.remove(array[0])
        if value == "needed_likes":
            last_updater(post_id)
    array = json.dumps(array)
    cursor.execute(f"""
    UPDATE posts
    SET {value} = '{array}'
    WHERE post_id = {post_id}
    """)
    conn.commit()
    conn.close()
    
def get_member_info(email):
    conn, cursor = create_db_users()
    cursor = conn.cursor()
    cursor.execute("SELECT name, final_identity, original_identity, role FROM users WHERE email = ?", (email,))
    identity = cursor.fetchall()
    return identity

def get_user_cookies(email):
	conn, cursor = create_db_users()
	cursor.execute("""
		SELECT remember_user_token, user_session_identifier FROM users
		WHERE email = ?
	""", (email,))
	cookies = cursor.fetchall()
	return cookies

def get_user_password(email):
    conn, cursor = create_db_users()
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM users WHERE email = ?", (email,))
    result = cursor.fetchone()
    return result

def update_cookies(remember_user_token, user_session_identifier, email):
    conn, cursor = create_db_users()
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET remember_user_token = ?, user_session_identifier = ? WHERE email = ?",
        (remember_user_token, user_session_identifier, email))
    conn.commit()
    print("cookies updated")
    return


def get_random_user_email(column_name="email", limit=1):
    """Fetches a random email from the users table."""
    try:
        conn, cursor = create_db_users()
        cursor = conn.cursor()
        cursor.execute(f"SELECT {column_name} FROM users ORDER BY RANDOM() LIMIT ?", (limit,))
        result = cursor.fetchone()
        if result:
            return result[0]
        else:
            print("Warning: No users found in the database.")
            return None
    except sqlite3.Error as e:
        print(f"Database error fetching random email: {e}")
        return None
    finally:
        if conn:
            conn.close()


            
def delete_post(post_id):
    try:
        conn, cursor = create_post_db()
        cursor.execute("DELETE FROM posts WHERE post_id = ?", (post_id,))
        conn.commit()
        print('posted deleted')
        return
    except Exception as e:
        print(e)
        return

    

def get_users_count():
    try:
        conn, cursor = create_db_users()
        cursor = conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]
        return count
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return None
    finally:
        if conn:
            conn.close()
