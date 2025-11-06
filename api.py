import utils
from main import databases_config_path
from fastapi import FastAPI,Body, Request
from pydantic import BaseModel
import json
from ai import process_query
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/databases")
def set_databases_configs(databases: list=Body(...)):
    """Set the databases configuration. This will overwrite the existing configuration.
    Arguments:
    databases: A list of dictionaries with the database configuration.
    """
    utils.save_databases_info(databases, databases_config_path)
    return {"message": "Databases configuration updated successfully.","ok":True}

@app.get("/plots/{plot_id}")
def get_plot(plot_id:str):
    plot = get_plot_data(plot_id)
    plot.update(get_plot_info(plot_id))
    return plot

@app.get("/plots/{plot_id}/data")
def get_plot_data(plot_id:str):
    plot_info = utils.get_plot_info(plot_id)
    data = utils.get_database_class(plot_info["database_configs"]).query(plot_info["query"])
    return {
        "x": [row[plot_info["x"]] for row in data],
        "y": [row[plot_info["y"]] for row in data]
    }

@app.get("/plots/{plot_id}/info")
def get_plot_info(plot_id:str):
    plot_info = utils.get_plot_info(plot_id)
    plot_info.pop("database_configs")
    return plot_info

class QueryRequest(BaseModel):
    query: str

@app.post("/ai")
async def get_ai_completion(data: QueryRequest):
    """Get a response from the AI agent.
    Arguments:
    query: The query to send to the AI agent.
    """
    response = process_query(data.query)
    response.pop("input")
    return response