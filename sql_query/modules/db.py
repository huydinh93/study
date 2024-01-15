# create a class PostgresManager using psycopg2 to manage the PostgreSQL database
# this class will have these functions:
# FUNCTION:
# __init__
# __enter__
# __exit__
# connect_with_url
# close_connection
# upsert(self, table_name, _dict)
# delete(self, table_name, _id)
# get(self, table_name, _id)
# get_all(self, table_name)
# run_sql(self, sql)class PostgresManager:
import psycopg2
from psycopg2 import sql

class PostgresManager:
    def __init__(self, connection_url=None):
        self.connection_url = connection_url
        self.conn = None
        self.cursor = None

    def __enter__(self):
        self.connect_with_url(self.connection_url)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_connection()

    def connect_with_url(self, connection_url):
        try:
            self.conn = psycopg2.connect(connection_url)
            self.cursor = self.conn.cursor()
        except Exception as e:
            print(f"Error connecting to PostgreSQL database: {e}")

    def close_connection(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

    def upsert(self, table_name, _dict):
        columns = _dict.keys()
        values = [_dict[column] for column in columns]
        on_conflict = f"ON CONFLICT (id) DO UPDATE SET " + ", ".join([f"{col}=EXCLUDED.{col}" for col in columns])

        query = sql.SQL("INSERT INTO {} ({}) VALUES ({}) {}").format(
            sql.Identifier(table_name),
            sql.SQL(', ').join(map(sql.Identifier, columns)),
            sql.SQL(', ').join(sql.Placeholder() * len(values)),
            sql.SQL(on_conflict)
        )
        
        try:
            self.cursor.execute(query, values)
            self.conn.commit()
        except Exception as e:
            print(f"Error executing upsert: {e}")

    def delete(self, table_name, _id):
        try:
            query = sql.SQL("DELETE FROM {} WHERE id = %s").format(sql.Identifier(table_name))
            self.cursor.execute(query, (_id,))
            self.conn.commit()
        except Exception as e:
            print(f"Error executing delete: {e}")

    def get(self, table_name, _id):
        try:
            query = sql.SQL("SELECT * FROM {} WHERE id = %s").format(sql.Identifier(table_name))
            self.cursor.execute(query, (_id,))
            return self.cursor.fetchone()
        except Exception as e:
            print(f"Error executing get: {e}")

    def get_all(self, table_name):
        try:
            query = sql.SQL("SELECT * FROM {}").format(sql.Identifier(table_name))
            self.cursor.execute(query)
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error executing get_all: {e}")

    def run_sql(self, sql):
        try:
            self.cursor.execute(sql)
            self.conn.commit()
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error running SQL command: {e}")

    def get_all_tables(self):
        try:
            self.cursor.execute("""
                SELECT table_schema || '.' || table_name
                FROM information_schema.tables
                WHERE table_type = 'BASE TABLE'
                AND table_schema NOT IN ('pg_catalog', 'information_schema');
            """)
            return [table[0] for table in self.cursor.fetchall()]
        except Exception as e:
            print(f"Error getting all tables: {e}")

    def get_table_definition(self, table_name):
        try:
            query = sql.SQL("""
                SELECT column_name, data_type, is_nullable
                FROM information_schema.columns
                WHERE table_name = %s;
            """)
            self.cursor.execute(query, (table_name.split('.')[1],))  # Split to get the table name without schema
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error getting table definition: {e}")
# Usage example:
# with PostgresManager('your_connection_url') as db_manager:
#     db_manager.run_sql('your_sql_command')
