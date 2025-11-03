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
    with open("plot_info.json", "r") as f:
        plots = json.load(f)
    if plot_id in plots:
        print(plots[plot_id])
        return plots[plot_id]
    raise ValueError(f"Plot with id {plot_id} not found.")

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