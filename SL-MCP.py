import streamlit as st
import pandas as pd
import sqlite3
import os
import utils
from mcp.server.fastmcp import FastMCP

workspace_path = os.path.dirname(os.path.abspath(__file__))
databases_config_path = os.path.join(workspace_path, "databases.json")

mcp = FastMCP("OpenQueryBI")

@mcp.tool()
def get_databases():
    """Get the list of all the databases. This will return a list of dictionaries with the name and description of each database.
    """
    databases = utils.get_databases(databases_config_path)
    databases = str(databases).replace("{","").replace("}","\n").capitalize()
    return databases

def get_tables(database_name:str):
    """Get the list of all the tables in the database. This will return a list of dictionaries with the name and description of each table.
    """
    database_info = utils.get_database_info(database_name, databases_config_path)
    conn = sqlite3.connect(workspace_path+"\\"+database_info["path"])
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    conn.close()
    return tables

@mcp.tool()
def get_database_info(database_name:str)->str:
    """Get the information of the database. This will return the tables and columns of the database.
    """
    database_info = utils.get_database_info(database_name, databases_config_path)
    conn = sqlite3.connect(workspace_path+"\\"+database_info["path"])
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    database_info.pop("path")
    database_info["tables"] = ""
    for table in tables:
        database_info["tables"] += table + '(Columns: '+get_table_columns(database_name, table)+')\n'
    conn.close()
    return f"""
    Database Name: {database_name}
    Type: {type}
    Tables: {database_info['tables']}
"""

def get_table_columns(database_name:str, table:str):
    """Get the columns of a table in the database. This will return the name of each column.
    """
    database_info = utils.get_database_info(database_name, databases_config_path)
    conn = sqlite3.connect(workspace_path+"\\"+database_info["path"])
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table})")
    columns = [row[1] for row in cursor.fetchall()]
    conn.close()
    return str(columns)

@mcp.tool()
def query_table(database_name, query,limit=100):
    database_info = utils.get_database_info(database_name, databases_config_path)
    conn = sqlite3.connect(workspace_path+"\\"+database_info['path'])
    if "limit" not in query.lower():
        query = f"{query} LIMIT {limit}"
    cursor = conn.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    columns = [column[0] for column in cursor.description]
    conn.close()
    return pd.DataFrame(result, columns=columns).to_string(index=False)

@mcp.tool()
def plot_from_sql(type:str,database_name:str,query:str,x:str,y:str,limit:int=100):
    """Plot a line chart from a SQL query. This will create a line chart with the x and y values.
    Arguments:
    type: The type of plot to create. This can be either "line" or "bar".
    database_name: The name of the database to use.
    query: The SQL query to execute.
    x: The name of the column to use for the x-axis.
    y: The name of the column to use for the y-axis.
    limit: The maximum number of rows to return from the query.
    """
    database_info = utils.get_database_info(database_name, databases_config_path)
    escaped_query = utils.clean_query(query)
    utils.run_command_in_background(f'streamlit run "{workspace_path}\\app.py" -- "plot_{type.lower()}_from_sql" "{workspace_path+"\\"+database_info['path']}" "{escaped_query}" "{x}" "{y}" {limit}')