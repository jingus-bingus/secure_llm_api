import os
import json
import psycopg2
from psycopg2 import sql

class Database_Manager:
    def __init__(self, user_id = None):
        self.user_id = user_id
        self.dbname = "secure_api"
        self.user = "postgres"
        self.password = "postgres"
        self.host = "127.0.0.1"
        self.port = "5432"

    def connect_to_database(self):
        try:
            connection = psycopg2.connect(
                dbname = self.dbname,
                user = self.user,
                password = self.password,
                host = self.host,
                port = self.port
            )

            return connection
        
        except psycopg2.Error as e:
            print(f"Error connecting to database: {e}")
            return None
        
    def create_tables(self):
        connection = self.connect_to_database()
        if connection is None:
            print("Failed to connect to the database.")
            return

        cursor = connection.cursor()

        try:
            cursor.execute('CREATE EXTENSION IF NOT EXISTS pgcrypto;')

            # Create users table
            cursor.execute(
                '''
                CREATE TABLE IF NOT EXISTS users (
                    user_id SERIAL PRIMARY KEY,
                    user_name TEXT,
                    password TEXT
                )
                '''
            )

            # Add totp_secret column if it doesn't exist
            cursor.execute(
                '''
                DO $$
                BEGIN
                    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='users' AND column_name='totp_secret') THEN
                        ALTER TABLE users ADD COLUMN totp_secret TEXT;
                    END IF;
                END
                $$;
                '''
            )

            # Create conversations table
            cursor.execute(
                '''
                CREATE TABLE IF NOT EXISTS conversations (
                    conversation_id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(user_id),
                    messages BYTEA
                )
                '''
            )

            connection.commit()
            print('Tables created or updated successfully.')
        except psycopg2.Error as e:
            print("Error creating or updating tables:", e)
        finally:
            if 'cursor' in locals() and cursor is not None:
                cursor.close()
            if 'connection' in locals() and connection is not None:
                connection.close()

    def insert_user(self, user_name, password, totp_secret):
        connection = self.connect_to_database()
        if connection is None:
            raise Exception("Failed to connect to the database.")

        try:
            with connection:
                with connection.cursor() as cursor:
                    query = '''
                    INSERT INTO users (user_name, password, totp_secret)
                    VALUES (%s, %s, %s)
                    RETURNING user_id
                    '''
                    cursor.execute(query, (user_name, password, totp_secret))
                    user_id = cursor.fetchone()[0]
                    connection.commit()
                    print("User inserted successfully.")
                    return user_id
        except psycopg2.Error as e:
            print("Error inserting user:", e)
            raise e
        finally:
<<<<<<< HEAD
            if 'cursor' in locals() and cursor is not None:
                cursor.close()
            if 'connection' in locals() and connection is not None:
=======
            if connection:
>>>>>>> database
                connection.close()

    # inserts a conversation given
    def insert_conversation(self, messages, key, user_id = None):
        if user_id:
            self.user_id = user_id
        try:
            connection = self.connect_to_database()
            if connection:
                with connection:
                    with connection.cursor() as cursor:
                        messages_json = json.dumps(messages)
                        query = '''
                        INSERT INTO conversations (user_id, messages)
                        VALUES (%s, 
                        pgp_sym_encrypt(%s::text, %s, 'cipher-algo=aes256')
                        )
                        RETURNING conversation_id
                        '''
                        cursor.execute(query, (self.user_id, messages_json, key))
                        conversation_id = cursor.fetchone()[0]
                        connection.commit()
                        print("conversation inserted")
                    return conversation_id

        except psycopg2.Error as e:
            print("Error inserting conversation:", e)
        finally:
            if 'cursor' in locals() and cursor is not None:
                cursor.close()
            if 'connection' in locals() and connection is not None:
                connection.close()

    #updates an existing conversation with new messages list
    def update_conversation(self, messages, conversation_id, key, user_id = None):
        if user_id:
            self.user_id = user_id
        try:
            connection = self.connect_to_database()
            if connection:
                with connection.cursor() as cursor:
                    messages_json = json.dumps(messages)
                    query = """
                    UPDATE conversations
                    SET messages = pgp_sym_encrypt(%s::text, %s, 'cipher-algo=aes256')
                    WHERE conversation_id = %s
                    """
                    cursor.execute(query, (messages_json, key, conversation_id))
                    connection.commit()

        except psycopg2.Error as e:
            print("Error updating conversation:", e)
        finally:
            if 'cursor' in locals() and cursor is not None:
                cursor.close()
            if 'connection' in locals() and connection is not None:
                connection.close()


    # retrieves messages for a conversation by the conversation id
    def retrieve_messages(self, conversation_id, key):
        try:
            connection = self.connect_to_database()
            if connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        '''
                        SELECT user_id, pgp_sym_decrypt(messages::BYTEA, %s, 'cipher-algo=aes256')::jsonb 
                        FROM conversations WHERE conversation_id = %s
                        ''',
                        [key, conversation_id]
                    )
                    conversation = cursor.fetchone()
                    if conversation:
                        user_id, messages = conversation
                        return messages
                    else:
                        return None
        except psycopg2.Error as e:
            print("Error retrieving conversation: ", e)
        finally:
            if 'cursor' in locals() and cursor is not None:
                cursor.close()
            if 'connection' in locals() and connection is not None:
                connection.close()

    def get_user_by_username(self, user_name):
        connection = self.connect_to_database()
        if connection is None:
            raise Exception("Failed to connect to the database.")

        cursor = None
        try:
<<<<<<< HEAD
            connection = self.connect_to_database()
            if connection:
                cursor = connection.cursor()  
                query = '''
                SELECT user_id, user_name, password
                FROM users
                WHERE user_name = %s
                '''
                cursor.execute(query, (user_name,))
                user = cursor.fetchone()
                if user:
                    return {
                        "user_id": user[0],
                        "user_name": user[1],
                        "password": user[2]
                    }
                else:
                    return None
=======
            cursor = connection.cursor()
            query = '''
            SELECT user_id, user_name, password, totp_secret
            FROM users
            WHERE user_name = %s
            '''
            cursor.execute(query, (user_name,))
            user = cursor.fetchone()
            if user:
                return {
                    "user_id": user[0],
                    "user_name": user[1],
                    "password": user[2],
                    "totp_secret": user[3]
                }
            else:
                return None
>>>>>>> database
        except psycopg2.Error as e:
            print("Error fetching user by username:", e)
            raise e
        finally:
<<<<<<< HEAD
            if 'cursor' in locals() and cursor is not None:
                cursor.close()
            if 'connection' in locals() and connection is not None:
=======
            if cursor:
                cursor.close()
            if connection:
                connection.close()

    def get_user_by_id(self, user_id):
        connection = self.connect_to_database()
        if connection is None:
            raise Exception("Failed to connect to the database.")

        try:
            with connection:
                with connection.cursor() as cursor:
                    query = '''
                    SELECT user_id, user_name, password, totp_secret
                    FROM users
                    WHERE user_id = %s
                    '''
                    cursor.execute(query, (user_id,))
                    user = cursor.fetchone()
                    if user:
                        return {
                            "user_id": user[0],
                            "user_name": user[1],
                            "password": user[2],
                            "totp_secret": user[3]
                        }
                    else:
                        return None
        except psycopg2.Error as e:
            print("Error fetching user by ID:", e)
            raise e
        finally:
            if connection:
>>>>>>> database
                connection.close()

    #retrieves all conversation ids with the first message of the conversations by user id
    def retrieve_conversations(self, key, user_id = None):
        if user_id:
            self.user_id = user_id
        try:
            connection = self.connect_to_database()
            if connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        '''
                        SELECT conversation_id, pgp_sym_decrypt(messages, %s)::jsonb 
                        FROM conversations WHERE user_id = %s
                        ''',
                        [key, self.user_id]
                    )
                    conversations = []
                    rows = cursor.fetchall()

                    for row in rows:
                        conversation_id, messages = row
                        entry = {
                            'conversation_id' : conversation_id,
                            'messages': messages[1]['content']
                        }
                        conversations.append(entry)
                    return conversations
        except psycopg2.Error as e:
            print("Error retrieving conversation: ", e)
        finally:
<<<<<<< HEAD
            if 'cursor' in locals() and cursor is not None:
                cursor.close()
            if 'connection' in locals() and connection is not None:
                connection.close()

    def rotate_key(self, old_key, new_key):
        try:
            connection = self.connect_to_database()
            if connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        '''
                        SELECT conversation_id, pgp_sym_decrypt(messages, %s)::jsonb
                        FROM conversations
                        ''',
                        [old_key]
                    )
                    rows = cursor.fetchall()

                    for row in rows:
                        conversation_id, messages = row
                        self.update_conversation(messages, conversation_id, new_key)
                        
        except psycopg2.Error as e:
            print("Error rotating key: ", e)
        finally:
            if 'cursor' in locals() and cursor is not None:
                cursor.close()
            if 'connection' in locals() and connection is not None:
                connection.close()

    def backup(self):
        command_str = "pg_dump -U " + self.user + " -h " + self.host + " -p " + self.port + " " + self.dbname + " > backup.sql"
        os.system(command_str)

    def restore(self):
        command_str = "pg_restore -U " + self.user + " -h " + self.host + " -p " + self.port + " -d " + self.dbname + " -f backup.sql"
        os.system(command_str)
=======
            cursor.close()
            connection.close()

    def set_totp_secret(self, user_id, totp_secret):
        connection = self.connect_to_database()
        if connection:
            with connection:
                with connection.cursor() as cursor:
                    try:
                        query = '''
                        UPDATE users
                        SET totp_secret = %s
                        WHERE user_id = %s
                        '''
                        cursor.execute(query, (totp_secret, user_id))
                        connection.commit()
                    except psycopg2.Error as e:
                        print(f"Error setting TOTP secret: {e}")

    def get_totp_secret(self, user_id):
        connection = self.connect_to_database()
        if connection:
            with connection:
                with connection.cursor() as cursor:
                    try:
                        query = '''
                        SELECT totp_secret
                        FROM users
                        WHERE user_id = %s
                        '''
                        cursor.execute(query, (user_id,))
                        result = cursor.fetchone()
                        if result:
                            return result[0]
                        else:
                            return None
                    except psycopg2.Error as e:
                        print(f"Error fetching TOTP secret: {e}")
>>>>>>> database
