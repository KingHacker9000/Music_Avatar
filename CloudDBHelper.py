import sqlitecloud

def dict_row_factory(cursor, row):
    """Convert row tuples to dictionaries with column names as keys."""
    columns = [col[0] for col in cursor.description]  # Get column names
    return {columns[i]: row[i] for i in range(len(row))}  # Map column names to row values


class CloudDB:
    def __init__(self, db_connection, db_name = 'Interactions'):
        self.conn = sqlitecloud.connect(db_connection)
        self.conn.row_factory = dict_row_factory
        self.conn.execute(f"USE DATABASE {db_name}")

        
    # Function to create a new interactions table with a user_id, timestamp, Old_Form_Id, New_Form_Id; Where user_id is a Integer, timestamp is a DateTime, Old_Form_Id and New_Form_Id are references to the form_id in the Forms table
    def create_interactions_table(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS Interactions (
                user_id INTEGER REFERENCES Users(user_id),
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                Old_Form_Id INTEGER REFERENCES Forms(form_id),
                New_Form_Id INTEGER REFERENCES Forms(form_id)
            )
        """)
        self.conn.commit()

    # Function to create a new users table with a user_id, user name
    def create_users_table(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS Users (
                user_id INTEGER PRIMARY KEY,
                user_name TEXT
            )
        """)
        self.conn.commit()

    # Function to create a new forms table with a form_id, song_name, character, Energy, Instrument, Captions; Where form_id is a Integer, and the rest are Strings
    def create_forms_table(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS Forms (
                form_id INTEGER PRIMARY KEY,
                song_name TEXT,
                character TEXT,
                Energy TEXT,
                Instrument TEXT,
                Captions TEXT
            )
        """)
        self.conn.commit()

    # Function that takes in 2 lists, first list consists of all the information for the old form, second list consists of all the information for the new form
    # The function will then insert the information into the forms table for each, then insert the resulting form_id's into the interactions table
    def insert_forms(self, user_id, old_form_info, new_form_info):
        """
        Form Info is a list of tuples, each tuple contains the information for a form
        The first tuple is the old form, the second tuple is the new form
        
        Each tuple contains the following information:
        song_name, character, Energy, Instrument, Captions
        """
        # Insert the old form into the forms table
        self.conn.execute("""
            INSERT INTO Forms (song_name, character, Energy, Instrument, Captions) VALUES (?, ?, ?, ?, ?);
        """, old_form_info)
        self.conn.commit()

        # Insert the new form into the forms table  
        self.conn.execute("""
            INSERT INTO Forms (song_name, character, Energy, Instrument, Captions) VALUES (?, ?, ?, ?, ?);
        """, new_form_info)
        self.conn.commit()

        # Get the form_id's of the newly inserted forms and return them
        old_form_id = self.conn.execute("SELECT form_id FROM Forms WHERE song_name = ? AND character = ? AND Energy = ? AND Instrument = ? AND Captions = ?", old_form_info).fetchone()['form_id']
        new_form_id = self.conn.execute("SELECT form_id FROM Forms WHERE song_name = ? AND character = ? AND Energy = ? AND Instrument = ? AND Captions = ?", new_form_info).fetchone()['form_id']
        
        # Insert the interaction into the interactions table
        self.conn.execute("""
            INSERT INTO Interactions (user_id, Old_Form_Id, New_Form_Id) VALUES (?, ?, ?);
        """, (user_id, old_form_id, new_form_id))
        self.conn.commit()

    def close(self):
        self.conn.close()

