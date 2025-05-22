import sqlite3
import os
import json
import utils
from mcp.server.fastmcp import FastMCP
databases_config_path = None
mediator_path = None

mcp = FastMCP("OpenQueryBI")

workspace_path = os.path.dirname(os.path.abspath(__file__))
if workspace_path:
    databases_config_path = os.path.join(workspace_path, "databases.json")
    mediator_path=os.path.join(workspace_path, "mediators")
else:
    raise RuntimeError("WORKSPACE_FOLDER_PATHS not set or empty.")

@mcp.tool()
def get_databases():
    """Get the list of all the possible Databases. This will return a list of dictionaries with the name and description of each database.
    """
    with open(databases_config_path, 'r') as f:
        return json.load(f)

#after some time, update this to work with LangChain code instead
@mcp.tool()
def query_data(database_name:str,sql:str,limit_rows:int=10):
    """Execute the SQL query on the database. This will return a the result of the query.
    You can find the list of all the possible databases in the databases.json file, which you can access through the get_databases() function.
    ONLY EXECUTE READ-ONLY QUERIES. DO NOT EXECUTE INSERT, UPDATE OR DELETE QUERIES.
    This function can be used to validate the SQL query before creating the mediator.
    Arguments:
    database: str: The database to use. This can be any database supported by SQLAlchemy.
    sql: str: The SQL query to use. This can be any READ-ONLY valid SQL query.
    limit_rows: int=10: The number of rows to return. This will be used to limit the number of rows returned by the query.
    """
    db = utils.get_database_info(database_name,databases_config_path)
    if "sqlite" in db["type"]:
        conn = sqlite3.connect(workspace_path+"\\"+db["path"])
        cursor = conn.cursor()
        if "limit" not in sql.lower():
            sql = f"{sql} LIMIT {limit_rows}"
        cursor.execute(sql)
        result = cursor.fetchall()
        conn.close()
        return result
    else:
        raise ValueError("Database not supported")

@mcp.tool()
def create_mediator(Database:str,SQL:str,name:str, description:str, frequency:int=180):
    """Create a mediator for the database using a SQL query. This will create a directory with the name of the mediator and a config.json file inside it.
    This will also create a Excel file with the same name as the mediator inside the directory. This Excel file will be used to store the data from the database.
    Before running this function, make sure that the database is already created and the SQL query is valid.
    Arguments:
    Database: str: The database to use. This can be any database supported by SQLAlchemy.
    SQL: str: The SQL query to use. This can be any valid SQL query.
    name: str: The name of the mediator. This will be used to create the directory and the Excel file.
    description: str: The description of the mediator. This will be used to create the config.json file.
    frequency: int: The frequency in which the Excel file will be updated.
    """
    path = os.path.join(mediator_path, name)
    os.makedirs(path)
    utils.export_config({'Database': Database,'SQL': SQL,'name': name,'description': description,"frequency":frequency,'last_updated':0},path)
    with open(path+"\\"+name+".xlsx", 'w') as f: pass

@mcp.tool()
def get_mediator(name:str):
    """Get the mediator with the given name. This will return a dictionary with the name, description, database and SQL query of the mediator.
    Arguments:
    name: str: The name of the mediator. This will be used to get the directory and the Excel file.
    """
    path = os.path.join(mediator_path, name)
    if os.path.exists(path):
        return utils.import_config(path)
    else:
        raise ValueError("Mediator not found")

@mcp.tool()
def get_mediators():
    """Get the list of all the mediators. This will return a list of dictionaries with the name, description, database and SQL query of each mediator.
    """
    mediators = []
    for root, dirs, files in os.walk(mediator_path):
        for dir in dirs:
            path = os.path.join(root, dir)
            if os.path.exists(path):
                mediators.append(utils.import_config(path))
    return mediators

@mcp.tool()
def delete_mediator(name:str):
    """Delete the mediator with the given name. This will delete the directory and the Excel file.
    Arguments:
    name: str: The name of the mediator. This will be used to get the directory and the Excel file.
    """
    path = os.path.join(mediator_path, name)
    if os.path.exists(path):
        os.remove(path)
        os.rmdir(path)
    else:
        raise ValueError("Mediator not found")

@mcp.tool()
def update_mediator(name:str,SQL:str=None,frequency:int=None):
    """Update the mediator with the given name. This will update the SQL query and the frequency of the mediator.
    Arguments:
    name: str: The name of the mediator. This will be used to get the directory and the Excel file.
    SQL: str: The SQL query to use. This can be any valid SQL query.
    frequency: int: The frequency in which the Excel file will be updated.
    """
    path = os.path.join(mediator_path, name)
    if os.path.exists(path):
        config = utils.import_config(path)
        if SQL:
            config["SQL"] = SQL
        if frequency:
            config["frequency"] = frequency
        utils.export_config(config,path)
    else:
        raise ValueError("Mediator not found")