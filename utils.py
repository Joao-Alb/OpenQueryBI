import json
import subprocess
import threading

def export_config(config:dict,path):
    with open(path+"\\config.json", 'w') as f:
        json.dump(config, f, indent=4)

def get_database_info(database_name:str,databases_config_path)->dict:
    """Get the information of the database. This will return a dictionary with the name and description of the database.
    """
    with open(databases_config_path, 'r') as f:
        databases = json.load(f)["databases"]
        for database in databases:
            if database["name"] == database_name:
                return database
    raise ValueError(f"Database {database_name} not found in {databases_config_path}")

def get_databases_list(databases_config_path:str):
    """Get the list of all the databases. This will return a list of dictionaries with the name and description of each database.
    """
    with open(databases_config_path, 'r') as f:
        databases = json.load(f)
        return databases["databases"]

def run_command_in_background(cmd):
    thread = threading.Thread(target=run_command, args=(cmd,))
    thread.start()

def run_command(cmd):
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,startupinfo=startupinfo)
    stdout, stderr = process.communicate()
    print("Output:", stdout)
    if stderr:
        print("Error:", stderr)

def clean_query(query:str):
    """Clean the query. This will remove the limit and order by clauses from the query.
    """
    return query.replace('"', '\\"').replace('\n', ' ').replace("'","")

import sqlite3
import pandas as pd
class Database():
    def __init__(self):
        raise NotImplementedError("Database class is not implemented, use one of its childs.")
    
    def get_tables(self):
        """Get the list of all the tables in the database. This will return a list of dictionaries with the name and description of each table.
        """
        raise NotImplementedError("get_tables method is not implemented, use one of its childs.")
    
    def get_table_columns(self):
        """Get the columns of a table in the database. This will return the name of each column.
        """
        raise NotImplementedError("get_table_columns method is not implemented, use one of its childs.")
    
    def get_database_info(self):
        """Get the information of the database. This will return the tables and columns of the database.
        """
        raise NotImplementedError("get_database_info method is not implemented, use one of its childs.")
    
    def query(self):
        """Query the database. This will return a dataframe with the result of the query.
        """
        raise NotImplementedError("validate_query method is not implemented, use one of its childs.")

class SQLiteDatabase(Database):
    
    def with_sqlite_connection(func):
        """Decorator that handles SQLite connection management.
        Opens connection, creates cursor, executes function, and ensures proper cleanup.
        """
        def wrapper(self, *args, **kwargs):
            self.conn = sqlite3.connect(self.path)
            self.cursor = self.conn.cursor()
            try:
                return func(self, *args, **kwargs)
            finally:
                self.cursor.close()
                self.conn.close()
        return wrapper


    def __init__(self, name:str, path:str):
        self.name = name
        self.path = path
        self.type = "sqlite"

    @with_sqlite_connection
    def get_tables(self):
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in self.cursor.fetchall()]
        return tables
    
    @with_sqlite_connection
    def get_table_columns(self, table:str):
        self.cursor.execute(f"PRAGMA table_info({table})")
        columns = [row[1] for row in self.cursor.fetchall()]
        return columns
    
    @with_sqlite_connection
    def get_database_info(self):
        """Get the information of the database. This will return the tables and columns of the database.
        """
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [row[0] for row in self.cursor.fetchall()]
        db_tables = ""
        for table in tables:
            db_tables += table + '(Columns: '+self.get_table_columns(table)+')\n'
        return f"""
        Database Name: {self.name}
        Type: {self.type}
        Tables: {db_tables}"""
    
    def query_string(self, query:str):
        return self.query(query).to_string(index=False)
    
    @with_sqlite_connection
    def query(self, query:str):
        self.cursor.execute(query)
        result = self.cursor.fetchall()
        columns = [column[0] for column in self.cursor.description]
        return pd.DataFrame(result, columns=columns)
    
def get_db(database_info:str)-> Database:
    """Get the database object. This will return a database object based on the type of the database.
    """
    if database_info["type"] == "sqlite":
        return SQLiteDatabase(database_info["name"], database_info["path"])
    else:
        raise ValueError(f"Database type {database_info['type']} is not supported.")