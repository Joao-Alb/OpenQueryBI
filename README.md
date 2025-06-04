# OpenQueryBI

A tool that helps Large Language Models (LLMs) create Dashboards and visualizations through database connections using Streamlit.

## Features
- SQL query execution with safety limits
- Dynamic chart generation (bar, line)
- Database configuration management
- Streamlit integration for visualization

## Installation
```bash
pip install -e .
```

## Project Structure
```
OpenQueryBI/
├── app.py              # Streamlit application
├── databases.json      # Database configurations
├── SL-MCP.py          # Main MCP tool functions
├── utils.py           # Utility functions
└── test/              # Test databases
    ├── crm.db
    └── inventory_management.db
```

## Usage
1. Configure your databases in `databases.json`
2. Use the MCP tools to query and visualize data:

```python
from SL_MCP import plot_from_sql

# Create a bar chart
plot_from_sql(
    type="bar",
    database_name="crm",
    query="SELECT product_name, COUNT(*) as count FROM orders GROUP BY product_name",
    x="product_name",
    y="count"
)
```

## Available Functions
- `query_table`: Execute SQL queries with result limits
- `plot_from_sql`: Generate charts from SQL queries
- `get_table_columns`: Retrieve column information
- `get_databases_list`: List available databases

## Requirements
- Python >= 3.12
- Streamlit >= 1.45.1
- MCP CLI >= 1.9.0
- SQLite3

## Development
To contribute:
1. Clone the repository
2. Install dependencies: `pip install -e ".[dev]"`
3. Run tests: `pytest`