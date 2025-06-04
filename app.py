import streamlit as st
import pandas as pd
import utils
import sys
import time

functions = {
    "plot_line_from_sql": st.bar_chart,
    "plot_bar_from_sql": st.line_chart
}

def get_dataframe_from_sql(database_name:str,query:str,limit:int=100):
    """Get a dataframe from a SQL query. This will return a dataframe with the result of the query.
    """
    if "limit" not in query.lower():
        query = f"{query} LIMIT {limit}"
    db_info = utils.get_database_info(database_name,"databases.json")
    return utils.get_db(db_info).query(query)

def plot_line_from_sql(database_name:str,query:str,x:str,y:str,limit:int=100):
    """Plot a line chart from a SQL query. This will create a line chart with the x and y values.
    """
    df = get_dataframe_from_sql(database_name,query,limit)
    if x not in df.columns or y not in df.columns:
        raise ValueError(f"Columns {x} and {y} must be present in the dataframe.")
    return st.line_chart(df.set_index(x)[y])

def plot_bar_from_sql(database_name:str,query:str,x:str,y:str,limit:int=100):
    """Plot a bar chart from a SQL query using Streamlit. This will create a bar chart with the x and y values.
    """
    df = get_dataframe_from_sql(database_name,query,limit)
    st.write(df)
    if x not in df.columns or y not in df.columns:
        raise ValueError(f"Columns {x} and {y} must be present in the dataframe.")
    return st.bar_chart(df.set_index(x)[y])

def plot_from_sql(plot_type:str,database_name:str,query:str,x:str,y:str,update_interval:int = 180, limit:int=100):
    """Plot a bar chart from a SQL query using Streamlit. This will create a bar chart with the x and y values.
    """
    df = get_dataframe_from_sql(database_name,query,limit)
    if x not in df.columns or y not in df.columns:
        raise ValueError(f"Columns {x} and {y} must be present in the dataframe.")
    
    while True:
        st.empty()  # clear old content
        functions[plot_type](df.set_index(x)[y])
        time.sleep(update_interval)
        st.rerun()

if __name__ == "__main__":
    if len(sys.argv) <= 1:
        st.write("No arguments provided. Running default plot.")
        plot_from_sql("plot_bar_from_sql","inventory_management", "SELECT product_name, COUNT(DISTINCT supplier_id) as supplier_count FROM inventory JOIN supplier_products ON inventory.product_ID = supplier_products.product_id GROUP BY product_name ORDER BY supplier_count DESC", "product_name", "supplier_count",update_interval=10)
    if len(sys.argv) > 1:
        plot_type = sys.argv[1]
        database_name = sys.argv[2]
        query = sys.argv[3]
        x = sys.argv[4]
        y = sys.argv[5]
        limit = int(sys.argv[6]) if len(sys.argv) > 6 else 100
        update_interval = int(sys.argv[7]) if len(sys.argv) > 7 else 180
        st.write(sys.argv[8] if len(sys.argv) > 8 else "Graph requested to AI")
        plot_from_sql(plot_type,database_name,query,x,y)