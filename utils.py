import json
import subprocess
import threading

def remove_key_from_dicts(dict_list, key_to_remove):
    return [{k: v for k, v in d.items() if k != key_to_remove} for d in dict_list]

def export_config(config:dict,path):
    with open(path+"\\config.json", 'w') as f:
        json.dump(config, f, indent=4)

def save_databases_info(databases: list, databases_config_path:str):
    with open(databases_config_path, 'w') as f:
        json.dump({"databases": databases}, f, indent=4)

def get_database_info(database_name:str,databases_config_path):
    """Get the information of the database. This will return a dictionary with the name and description of the database.
    """
    with open(databases_config_path, 'r') as f:
        databases = json.load(f)["databases"]
        for database in databases:
            if database["name"] == database_name:
                return database
    raise ValueError(f"Database {database_name} not found in {databases_config_path}")

def get_databases(databases_config_path:str):
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

from sqlalchemy import create_engine, text

class Database():
    def __init__(self, config:dict):
        self.dialect = config.get('dialect')

    def query(self, query:str):
        """Run a query on the database. This will return the result of the query.
        """
        raise NotImplementedError("This method should be implemented by subclasses.")
                                  
class SQLiteDatabase(Database):
    def __init__(self, config:dict):
        super().__init__(config)
        self.path = config.get('database')

    def query(self,query: str):
        connection_url = f"sqlite:///{self.path}"
        engine = create_engine(connection_url)
        with engine.connect() as conn:
            result = conn.execute(text(query))
            return result.fetchall(),list(result.keys())

    def get_table_columns(self, table:str):
        """Get the columns of a table in the SQLite database. This will return the name of each column.
        """
        query = f"PRAGMA table_info({table});"
        data, _ = self.query(query)
        columns = [str(column[1])+f'({column[2]})' for column in data]
        return columns
    
class PostgresDatabase(Database):
    
    def __init__(self, config:dict):
        super().__init__(config)
        self.host = config.get('host')
        self.port = config.get('port', 5432)
        self.database = config.get('database')
        self.username = config.get('username')
        self.password = config.get('password')
        self.sslmode = config.get('sslmode', 'require')
        self.channel_binding = config.get('channel_binding', 'require')

    def query(self, query:str):
        connection_url = (
        f"postgresql://{self.username}:{self.password}"
        f"@{self.host}/{self.database}"
        f"?sslmode={self.sslmode}&channel_binding={self.channel_binding}"
    )
        engine = create_engine(connection_url)
        with engine.connect() as conn:
            result = conn.execute(text(query))
            return result.fetchall(),list(result.keys())
        
    def get_table_columns(self, table:str):
        """Get the columns of a table in the SQLite database. This will return the name of each column.
        """
        query = f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{table}';"
        data, _ = self.query(query)
        columns = [str(column[0])+f'({column[1]})' for column in data]
        return columns
    

def get_database_class(database_info:dict)->Database:
    """Get the database class based on the dialect. This will return the class that will be used to connect to the database.
    """
    if database_info['config']['dialect'] == "sqlite":
        return SQLiteDatabase(database_info["config"])
    
    elif database_info['config']['dialect'] == "postgresql":
        return PostgresDatabase(database_info["config"])
    
    else:
        raise ValueError(f"Unsupported database dialect: {database_info['dialect']}")