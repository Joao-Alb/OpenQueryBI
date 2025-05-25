import streamlit as st
import pandas as pd
import sqlite3
import sys

def get_dataframe_from_sql(database_path:str,query:str,limit:int=100):
    """Get a dataframe from a SQL query. This will return a dataframe with the result of the query.
    """
    if "limit" not in query.lower():
        query = f"{query} LIMIT {limit}"
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    columns = [column[0] for column in cursor.description]
    conn.close()
    return pd.DataFrame(result, columns=columns)

def plot_line_from_sql(database_path:str,query:str,x:str,y:str,limit:int=100):
    """Plot a line chart from a SQL query. This will create a line chart with the x and y values.
    """
    df = get_dataframe_from_sql(database_path,query,limit)
    if x not in df.columns or y not in df.columns:
        raise ValueError(f"Columns {x} and {y} must be present in the dataframe.")
    return st.line_chart(df.set_index(x)[y])

def plot_bar_from_sql(database_path:str,query:str,x:str,y:str,limit:int=100):
    """Plot a bar chart from a SQL query using Streamlit. This will create a bar chart with the x and y values.
    """
    df = get_dataframe_from_sql(database_path,query,limit)
    if x not in df.columns or y not in df.columns:
        raise ValueError(f"Columns {x} and {y} must be present in the dataframe.")
    return st.bar_chart(df.set_index(x)[y])

functions = {
    "plot_line_from_sql": plot_line_from_sql,
    "plot_bar_from_sql": plot_bar_from_sql
}

if __name__ == "__main__":
    if len(sys.argv) > 1:
        func = functions.get(sys.argv[1])
        if func:
            database_path = sys.argv[2]
            query = sys.argv[3]
            x = sys.argv[4]
            y = sys.argv[5]
            func(database_path,query,x,y)
        else:
            raise Exception(ValueError(f"Function {sys.argv[1]} not found."))