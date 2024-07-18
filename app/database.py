import json
import psycopg2
from psycopg2 import sql

class Database_Manager:
    def __init__(self, user_id = None):
        self.user_id = user_id

    def connect_to_database(self):
        try:
            connection = psycopg2.connect(
                dbname = "secure_api",
                user = "postgres",
                password = "postgres",
                host = "127.0.0.1",
                port = "5432"
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
            cursor.close()
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
            if connection:
                connection.close()

    # inserts a conversation given
    def insert_conversation(self, messages, user_id = None):
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
                        pgp_sym_encrypt(%s::text, 'dummy_secret_key', 'cipher-algo=aes256')
                        )
                        RETURNING conversation_id
                        '''
                        cursor.execute(query, (self.user_id, messages_json))
                        conversation_id = cursor.fetchone()[0]
                        connection.commit()
                        print("conversation inserted")
                    return conversation_id

        except psycopg2.Error as e:
            print("Error inserting conversation:", e)
        finally:
            cursor.close()
            connection.close()

    #updates an existing conversation with new messages list
    def update_conversation(self, messages, conversation_id, user_id = None):
        if user_id:
            self.user_id = user_id
        try:
            connection = self.connect_to_database()
            if connection:
                with connection.cursor() as cursor:
                    messages_json = json.dumps(messages)
                    query = """
                    UPDATE conversations
                    SET messages = pgp_sym_encrypt(%s::text, 'dummy_secret_key', 'cipher-algo=aes256')
                    WHERE conversation_id = %s
                    """
                    cursor.execute(query, (messages_json, conversation_id))
                    connection.commit()

        except psycopg2.Error as e:
            print("Error updating conversation:", e)
        finally:
            cursor.close()
            connection.close()


    # retrieves messages for a conversation by the conversation id
    def retrieve_messages(self, conversation_id):
        try:
            connection = self.connect_to_database()
            if connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        '''
                        SELECT user_id, pgp_sym_decrypt(messages::BYTEA, 'dummy_secret_key', 'cipher-algo=aes256')::jsonb 
                        FROM conversations WHERE conversation_id = %s
                        ''',
                        [conversation_id]
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
            cursor.close()
            connection.close()

    def get_user_by_username(self, user_name):
        connection = self.connect_to_database()
        if connection is None:
            raise Exception("Failed to connect to the database.")

        cursor = None
        try:
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
        except psycopg2.Error as e:
            print("Error fetching user by username:", e)
            raise e
        finally:
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
                connection.close()

    #retrieves all conversation ids with the first message of the conversations by user id
    def retrieve_conversations(self, user_id = None):
        if user_id:
            self.user_id = user_id
        try:
            connection = self.connect_to_database()
            if connection:
                with connection.cursor() as cursor:
                    cursor.execute(
                        '''
                        SELECT conversation_id, pgp_sym_decrypt(messages, 'dummy_secret_key')::jsonb 
                        FROM conversations WHERE user_id = %s
                        ''',
                        [self.user_id]
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