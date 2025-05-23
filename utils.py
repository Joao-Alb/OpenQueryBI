import json
import subprocess
import threading

def export_config(config:dict,path):
    with open(path+"\\config.json", 'w') as f:
        json.dump(config, f, indent=4)

def get_database_info(database_name:str,databases_config_path):
    """Get the information of the database. This will return a dictionary with the name and description of the database.
    """
    with open(databases_config_path, 'r') as f:
        databases = json.load(f)["databases"]
        for database in databases:
            if database["name"] == database_name:
                return database
    raise ValueError(f"Database {database_name} not found in {databases_config_path}")


def run_command_in_background(cmd):
    thread = threading.Thread(target=run_command, args=(cmd,))
    thread.start()

def run_command(cmd):
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout, stderr = process.communicate()
    print("Output:", stdout)
    if stderr:
        print("Error:", stderr)