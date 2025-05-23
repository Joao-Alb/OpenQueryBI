import streamlit as st
import pandas as pd
import sqlite3
import sys

def plot_line_from_sql(database_path:str,query:str,x:str,y:str,limit:int=100):
    """Plot a line chart from a SQL query. This will create a line chart with the x and y values.
    """
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    cursor.execute(query)
    result = cursor.fetchall()
    columns = [column[0] for column in cursor.description]
    conn.close()
    df = pd.DataFrame(result, columns=columns)
    return st.line_chart(df.set_index(x)[y])


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "plot_line_from_sql":
            database_path = sys.argv[2]
            query = sys.argv[3]
            x = sys.argv[4]
            y = sys.argv[5]
            plot_line_from_sql(database_path,query,x,y)