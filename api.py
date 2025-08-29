import utils
from main import databases_config_path
from fastapi import FastAPI,Body

app = FastAPI()

@app.post("/set_databases_configs/")
def set_databases_configs(databases: list=Body(...)):
    """Set the databases configuration. This will overwrite the existing configuration.
    Arguments:
    databases: A list of dictionaries with the database configuration.
    """
    utils.save_databases_info(databases, databases_config_path)
    return {"message": "Databases configuration updated successfully.","ok":True}