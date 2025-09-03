import pandas as pd
from sqlalchemy import create_engine, text
import os
import utils
from mcp.server.fastmcp import FastMCP
import json

PORT = 8002

workspace_path = os.path.dirname(os.path.abspath(__file__))
databases_config_path = os.path.join(workspace_path, "databases.json")

mcp = FastMCP("OpenQueryBI",host="0.0.0.0", port=PORT)

def __query(query: str, database_info:dict):
   
    if database_info['dialect'] == "sqlite":
        connection_url = f"sqlite:///{database_info['database']}"
    
    elif database_info['dialect'] == "postgresql":
        connection_url = (
        f"postgresql://{database_info['username']}:{database_info['password']}"
        f"@{database_info['host']}/{database_info['database']}"
        f"?sslmode={database_info.get('sslmode','require')}&channel_binding={database_info.get('channel_binding','require')}"
    )

    else:
       connection_url = (
        f"{database_info['dialect']}://{database_info['username']}:{database_info['password']}"
        f"@{database_info['host']}:{database_info['port']}/{database_info['database']}"
    )
    engine = create_engine(connection_url)
    with engine.connect() as conn:
        result = conn.execute(text(query))
        return result.fetchall(),list(result.keys())

@mcp.tool()
def get_databases():
    """Get the list of all the databases. This will return a list of dictionaries with the name and description of each database.
    """
    databases = utils.get_databases(databases_config_path)
    for db in databases:
        Database = utils.get_database_class(db)
        schemas = Database.export_schema_as_sql()
        for attr in ["tables","config"]:
            db.pop(attr)
        db['tables'] = [{v:Database.get_sample_rows(table=k,limit=3,format=True)} for d in schemas for k, v in d.items()]
    output = "Databases available:\n"
    for db in databases:
        output += utils.get_database_prompt(db)+"\n####\n"
    return output

def get_tables(database_name:str):
    """Get the list of all the tables in the database. This will return a list of dictionaries with the name and description of each table.
    """
    database_info = utils.get_database_info(database_name, databases_config_path)
    data = __query("SELECT name FROM sqlite_master WHERE type='table';",database_info["config"])
    return [row[0] for row in data]


def get_table_columns(database_name:str, table:str):
    """Get the columns of a table in the database. This will return the name of each column.
    """
    database_info = utils.get_database_info(database_name, databases_config_path)
    database = utils.get_database_class(database_info)
    columns = database.get_table_columns(table)
    return ", ".join(columns)

@mcp.tool()
def validate_query(database_name: str, query: str, limit: int = 100):
    """Query a table in the database. This will return the result of the query.
    Run this function carefully. This will execute the query in the database.
    DO NOT USE THIS FUNCTION FOR INSERT, UPDATE OR DELETE QUERIES.
    This function is only for SELECT queries. Only execute read only queries.
    Please run this function before using the plot_from_sql function.
    Arguments:
    database_name: The name of the database to use.
    query: The SQL query to execute.""" 
    database_info = utils.get_database_info(database_name, databases_config_path)
    if "limit" not in query.lower():
        query = f"{query} LIMIT {limit}"
    data,columns = __query(query,database_info["config"])
    return pd.DataFrame(data, columns=columns).to_string(index=False)

@mcp.tool()
def plot_from_sql(type:str,database_name:str,query:str,x:str,y:str,limit:int=100, update_interval:int=10, title:str="Graph requested to AI"):
    """Plot a line chart from a SQL query. This will create a line chart with the x and y values.
    Please be sure that the query is working. Validate the query using the query_table function before calling this function.
    The query must return a table with the x and y values. The x and y values must be in the same table.
    This function will create a live graph that will be visible in the UI for the user.
    Arguments:
    type: The type of plot to create. This can be either "line" or "bar".
    database_name: The name of the database to use.
    query: The SQL query to execute.
    x: The name of the column to use for the x-axis.
    y: The name of the column to use for the y-axis.
    limit: The maximum number of rows to return from the query. Default is 100 rows,
    update_interval: The interval in seconds to update the graph. Default is 180 seconds,
    title: The title of the graph. Default is "Graph requested to AI".
    """
    database_info = utils.get_database_info(database_name, databases_config_path)
    with open(os.path.join(workspace_path, "plot_info.json"), "r") as f:
        plots = json.load(f)
    plot_data = {
    "type":type,
    "database_configs": database_info["config"],
    "x": x,
    "y": y,
    "query": utils.clean_query(query),
    "limit": limit,
    "update_interval": update_interval,
    "title": title
    }
    plot_id = utils.generate_plot_id(plot_data)
    if plot_id not in plots:
        plots[plot_id] = plot_data
        with open(os.path.join(workspace_path, "plot_info.json"), "w") as f:
            json.dump(plots, f, indent=4)
    return {
        'plot_id': plot_id,
        'message': f'Plot created with id {plot_id}, This plot will be visible in the UI.'
    }

if __name__ == "__main__":
    print(f"Starting OpenQueryBI MCP server on port {PORT}...")
    print(f"Connect to this server using http://localhost:{PORT}/sse")
    mcp.run(transport="sse")