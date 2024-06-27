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
        
    # sets up the database with the necessary tables
    def create_tables(self):
        connection = self.connect_to_database()
        cursor = connection.cursor()

        try:
            cursor.execute('CREATE EXTENSION IF NOT EXISTS pgcrypto ;')
            # users tables creation
            cursor.execute(
                '''
                CREATE TABLE IF NOT EXISTS users(
                user_id SERIAL PRIMARY KEY,
                user_name TEXT,
                password TEXT
                )
                '''
            )
            
            # conversations tables creation
            cursor.execute(
                '''
                CREATE TABLE IF NOT EXISTS conversations(
                conversation_id SERIAL PRIMARY KEY,
                user_id SERIAL REFERENCES users(user_id),
                messages BYTEA
                );
                '''
            )

            connection.commit()
            print('tables created')
        except psycopg2.Error as e:
            print("Error creating table:", e)
        finally:
            if 'cursor' in locals() and cursor is not None:
                cursor.close()
            if 'connection' in locals() and connection is not None:
                connection.close()

    #inserts a new user to the users table
    def insert_user(self, user_name, password):
        try:
            connection = self.connect_to_database()
            if connection:
                with connection:
                    with connection.cursor() as cursor:
                        query = '''
                        INSERT INTO users (user_name, password)
                        VALUES (%s, %s)
                        RETURNING user_id
                        '''
                        cursor.execute(query, (user_name, password))
                        user_id = cursor.fetchone()[0]
                        connection.commit()
                        print("user inserted")
                    return user_id

        except psycopg2.Error as e:
            print("Error inserting user:", e)
        finally:
            if 'cursor' in locals() and cursor is not None:
                cursor.close()
            if 'connection' in locals() and connection is not None:
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
        try:
            connection = self.connect_to_database()
            if connection:
                cursor = self.connection.cursor()  
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
        except psycopg2.Error as e:
            print("Error fetching user by username:", e)
            raise
        finally:
            if 'cursor' in locals() and cursor is not None:
                cursor.close()
            if 'connection' in locals() and connection is not None:
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