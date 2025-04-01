import sqlitecloud
import os

def dict_row_factory(cursor, row):
    """Convert row tuples to dictionaries with column names as keys."""
    columns = [col[0] for col in cursor.description]  # Get column names
    return {columns[i]: row[i] for i in range(len(row))}  # Map column names to row values


class CloudDB:
    def __init__(self, connection_string, db_name='AvatarInteractions'):

        self.connection_string = connection_string
        self.db_name = db_name
        self.conn = sqlitecloud.connect(connection_string)
        self.conn.row_factory = dict_row_factory
        self.conn.execute(f"USE DATABASE {db_name};")
        self.create_all_tables()

    def _execute_query(self, query, params=None, fetch_one=False, fetch_all=False):

        try:
            cursor = None
            if params:
                cursor = self.conn.execute(query, params)
            else:
                cursor = self.conn.execute(query)

            result = None
            if fetch_one:
                result = cursor.fetchone()
            elif fetch_all:
                result = cursor.fetchall()
            
            self.conn.commit()

            return result
        
        except sqlitecloud.exceptions.SQLiteCloudIntegrityError as e:
            print(f"SQLiteCloudIntegrityError: {e}")
            self.conn.close()
            self.conn = sqlitecloud.connect(self.connection_string)
            self.conn.row_factory = dict_row_factory
            self.conn.execute(f"USE DATABASE {self.db_name};")
    
    def create_users_table(self):

        query = """CREATE TABLE IF NOT EXISTS Users (user_id INTEGER PRIMARY KEY AUTOINCREMENT, user_name TEXT);"""

        self._execute_query(query)

    def create_forms_table(self):

        query = """CREATE TABLE IF NOT EXISTS Forms ( form_id INTEGER PRIMARY KEY AUTOINCREMENT, song_name TEXT NOT NULL, character TEXT NOT NULL, Instrument TEXT NOT NULL, Captions TEXT NOT NULL);"""

        index_query = """CREATE INDEX IF NOT EXISTS idx_forms_lookup ON Forms (song_name, character, Instrument, Captions);"""
        self._execute_query(query)
        self._execute_query(index_query)


    def create_interactions_table(self):
        
        query = """CREATE TABLE IF NOT EXISTS Interactions (interaction_id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT NOT NULL REFERENCES Users(user_id), timestamp DATETIME DEFAULT CURRENT_TIMESTAMP, Old_Form_Id INTEGER REFERENCES Forms(form_id), New_Form_Id INTEGER NOT NULL REFERENCES Forms(form_id));"""

        self._execute_query(query)

    def create_all_tables(self):
        
        self.create_users_table()
        self.create_forms_table()
        self.create_interactions_table()

        print("All database tables checked/created.")

    def drop_all_tables(self):
        for table_name in ["Users", "Forms", "Interactions"]:
            drop_query = f"DROP TABLE IF EXISTS {table_name};"
            self._execute_query(drop_query)
            print(f"Dropped table: {table_name}")

    def add_user(self, user_name):
        
        query = """INSERT INTO Users (user_name) VALUES (?);"""
        self._execute_query(query, (user_name))
        print(f"Added user: {user_name}")

    def add_form(self, form_info):
        if form_info[0] == "":
            form_info[0] = "NULL"
        if form_info[1] == "":
            form_info[1] = "NULL"
        if form_info[2] == "":
            form_info[2] = "NULL"
        if form_info[3] == "":
            form_info[3] = "NULL"

        form_id = self.get_form_id((form_info[0], form_info[1], form_info[2], form_info[3]))
        if form_id is not None:
            print(f"Form already exists: {form_info[0]} - {form_info[1]} - {form_info[2]} - {form_info[3]}")
            return form_id

        query = """INSERT INTO Forms (song_name, character, instrument, captions) VALUES (?, ?, ?, ?);"""
        self._execute_query(query, (form_info[0], form_info[1], form_info[2], form_info[3]))
        form_id = self.get_form_id((form_info[0], form_info[1], form_info[2], form_info[3]))
        
        if form_id is None:
            print(f"ERROR: Failed to add form: {form_info[0]} - {form_info[1]} - {form_info[2]} - {form_info[3]}")
            return None
        print(f"Added form: {form_info[0]} - {form_info[1]} - {form_info[2]} - {form_info[3]}")
        return form_id

    def get_form_id(self, form_info):

        query = """SELECT form_id FROM Forms WHERE song_name = ? AND character = ? AND instrument = ? AND captions = ?;"""
        form_id = self._execute_query(query, form_info, fetch_one=True)
        if form_id is None:
            return None
        return form_id["form_id"]

    def add_interaction(self, user_id, old_form_info, new_form_info):
        
        old_form_id = self.add_form(old_form_info)
        new_form_id = self.add_form(new_form_info)

        query = """INSERT INTO Interactions (user_id, old_form_id, new_form_id) VALUES (?, ?, ?);"""
        self._execute_query(query, (user_id, old_form_id, new_form_id))
        print(f"Added interaction: {user_id} - {old_form_info} - {new_form_info}")

    def close(self):
        """Closes the database connection."""
        if self.conn:
            self.conn.close()


if __name__ == "__main__":

    DELETE_TEST = False
    from dotenv import load_dotenv
    load_dotenv()
    connection_host = os.environ.get("SQLite_Connection")
    connection_apikey = os.environ.get("SQLite_apikey")
    connection_string = f"{connection_host}apikey={connection_apikey}"

    if not connection_string:
        print("Error: SQLITECLOUD_CONNECTION_STRING environment variable not set.")
        exit(1)


    db = CloudDB(connection_string, db_name='AvatarInteractions')
    if DELETE_TEST and input("Delete all tables? (y/n): ") == "y":
        db.drop_all_tables()
        exit()

    db.add_user("John Doe")
    db.add_user("Jane Doe")
    #db.add_form(("Song1", "Character1", "Instrument1", "off"))
    #db.add_interaction("user1", ("Song1", "Character1", "Instrument1", "off"), ("Song1", "Character1", "Instrument1", "on"))
    db.close()
