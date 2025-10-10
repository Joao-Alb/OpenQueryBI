from langchain.agents import AgentType, initialize_agent
from langchain_anthropic.chat_models import ChatAnthropic
from langchain.tools import BaseTool
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
import os
from typing import Optional, Type
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import MCP functions
from main import get_databases, validate_query, plot_from_sql

# Initialize Claude
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
llm = ChatAnthropic(model="claude-3-opus-20240229", anthropic_api_key=ANTHROPIC_API_KEY, temperature=0)

# Tool input schemas
class QueryInput(BaseModel):
    database_name: str = Field(..., description="The name of the database to query")
    query: str = Field(..., description="The SQL query to execute (SELECT only)")
    limit: Optional[int] = Field(100, description="Maximum number of rows to return")

class PlotInput(BaseModel):
    type: str = Field(..., description="The type of plot ('line' or 'bar')")
    database_name: str = Field(..., description="The name of the database to use")
    query: str = Field(..., description="The SQL query to execute")
    x: str = Field(..., description="Column name for x-axis")
    y: str = Field(..., description="Column name for y-axis")
    limit: Optional[int] = Field(100, description="Maximum number of rows")
    update_interval: Optional[int] = Field(10, description="Update interval in seconds")
    title: Optional[str] = Field("Graph requested to AI", description="Title of the graph")

# LangChain tools
class DatabaseListTool(BaseTool):
    name: str ="list_databases"
    description: str = "Lists all available databases with their schemas and sample data"
    
    def _run(self):
        return get_databases()
    
    def _arun(self):
        raise NotImplementedError("Async not supported")

class QueryDatabaseTool(BaseTool):
    name: str ="query_database"
    description: str = "Execute a SQL query on a specified database (SELECT queries only)"
    args_schema: Type[BaseModel] = QueryInput
    
    def _run(self, database_name: str, query: str, limit: int = 100):
        return validate_query(database_name=database_name, query=query, limit=limit)
    
    def _arun(self):
        raise NotImplementedError("Async not supported")

class CreatePlotTool(BaseTool):
    name: str ="create_plot"
    description: str = "Create a line or bar plot from SQL query results"
    args_schema: Type[BaseModel] = PlotInput
    
    def _run(self, type: str, database_name: str, query: str, x: str, y: str,
             limit: int = 100, update_interval: int = 10, title: str = "Graph requested to AI"):
        return plot_from_sql(
            type=type,
            database_name=database_name,
            query=query,
            x=x,
            y=y,
            limit=limit,
            update_interval=update_interval,
            title=title
        )
    
    def _arun(self):
        raise NotImplementedError("Async not supported")

# Initialize tools
tools = [
    DatabaseListTool(),
    QueryDatabaseTool(),
    CreatePlotTool()
]

# Create the agent
agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.STRUCTURED_CHAT_ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    return_intermediate_steps=True
)

def process_query(user_input: str) -> str:
    """
    Process a natural language query using Claude and the available tools
    
    Args:
        user_input (str): The user's natural language query
        
    Returns:
        str: The response from the agent
    """
    try:
        response = agent.invoke(user_input)
        return response
    except Exception as e:
        return f"Error processing query: {str(e)}"

if __name__ == "__main__":
    while True:
        user_input = input("Enter your query (or 'exit' to quit): ")
        if user_input.lower() == 'exit':
            break
        response = process_query(user_input)
        print("Response:", response)