# Connect AI Client

Python client for Connect AI's REST API, providing efficient metadata discovery and SQL query execution with optimized token usage.

## Installation

### Requirements

```bash
pip install requests
```

Python 3.10+ required (uses modern type hints with `tuple[str, str]`).

For Python 3.8-3.9, change type hints to use `typing.Tuple`:
```python
from typing import Tuple
def get_auth_credentials() -> Tuple[str, str]:
```

## Setup

Set environment variables for authentication:

```bash
export CONNECT_AI_EMAIL="your-email@example.com"
export CONNECT_AI_TOKEN="your-access-token"
```

Or in Python:
```python
import os
os.environ['CONNECT_AI_EMAIL'] = 'your-email@example.com'
os.environ['CONNECT_AI_TOKEN'] = 'your-access-token'
```

## Quick Start

```python
from connect_ai_client import (
    get_catalogs,
    get_tables,
    execute_query_compact
)

# List all connections
catalogs = get_catalogs()
print([c.catalogName for c in catalogs])

# List tables
tables = get_tables(
    catalog_name='Salesforce_Integraite',
    schema_name='Salesforce'
)
print([t.TABLE_NAME for t in tables[:10]])

# Execute optimized query
result = execute_query_compact(
    'SELECT Name, AnnualRevenue FROM Salesforce_Integraite.Salesforce.Account LIMIT 10'
)
print(result)
```

## API Reference

### Metadata Operations

#### `get_catalogs() -> List[Catalog]`

Retrieves all available catalogs (data sources).

```python
catalogs = get_catalogs()
for catalog in catalogs:
    print(catalog.catalogName)
```

#### `get_schemas(catalog_name=None, schema_name=None) -> List[Schema]`

Retrieves available schemas, optionally filtered.

```python
schemas = get_schemas('Salesforce_Integraite')
for schema in schemas:
    print(schema.TABLE_SCHEMA)
```

#### `get_tables(catalog_name=None, schema_name=None, table_name=None, table_type=None) -> List[Table]`

Retrieves table metadata with optional filtering.

```python
tables = get_tables(
    catalog_name='Salesforce_Integraite',
    schema_name='Salesforce'
)
for table in tables:
    print(f'{table.TABLE_NAME} ({table.TABLE_TYPE})')
```

### Query Operations

#### `execute_query(query, default_schema=None, schema_only=False, parameters=None) -> QueryResult`

Executes a SQL query and returns full results with schema.

```python
result = execute_query(
    query='SELECT Id, Name FROM Salesforce_Integraite.Salesforce.Account LIMIT 5'
)
print(f'Columns: {[col.columnName for col in result.schema]}')
print(f'Rows: {result.rows}')
```

#### `execute_query_compact(query) -> List[Dict[str, Any]]`

**Token-optimized query execution** - returns minimal JSON format.

```python
# Returns list of dictionaries (one per row)
result = execute_query_compact(
    'SELECT Name, AnnualRevenue FROM Salesforce_Integraite.Salesforce.Account LIMIT 10'
)
# [{'Name': 'Acme Corp', 'AnnualRevenue': 1000000}, ...]
```

**Use this for maximum token efficiency** - 58-65% token savings vs full schema.

#### `format_query_results(result, compact=False) -> str`

Formats query results as a readable table or compact JSON.

```python
result = execute_query('SELECT * FROM Account LIMIT 5')

# Formatted table
print(format_query_results(result))

# Compact JSON
print(format_query_results(result, compact=True))
```

### Helper Functions

#### `get_table_columns(catalog_name, schema_name, table_name) -> QueryResult`

Gets column metadata for a specific table.

```python
columns = get_table_columns(
    'Salesforce_Integraite',
    'Salesforce',
    'Account'
)
for col in columns.schema:
    print(f'{col.columnName}: {col.dataTypeName}')
```

## Usage Examples

### Example 1: Explore Available Data

```python
from connect_ai_client import get_catalogs, get_schemas, get_tables

# Discover what data sources exist
catalogs = get_catalogs()
print('Available data sources:')
for catalog in catalogs:
    print(f'  - {catalog.catalogName}')

    # Get schemas for this catalog
    schemas = get_schemas(catalog.catalogName)
    for schema in schemas:
        print(f'    └─ {schema.TABLE_SCHEMA}')

        # Get tables in this schema
        tables = get_tables(
            catalog_name=catalog.catalogName,
            schema_name=schema.TABLE_SCHEMA
        )
        print(f'       Tables: {len(tables)}')
```

### Example 2: Cross-System Analytics (Token-Optimized)

```python
from connect_ai_client import execute_query_compact
import json

# Join Salesforce and Zendesk data in a single query
query = """
    SELECT
        a.Name AS AccountName,
        a.AnnualRevenue,
        COUNT(t.Id) AS OpenTickets
    FROM Salesforce_Integraite.Salesforce.Account a
    LEFT JOIN Zendesk_Integraite.Zendesk.Tickets t
        ON a.Id = t.AccountId
        AND t.Status IN ('new', 'open', 'pending')
    WHERE a.AnnualRevenue IS NOT NULL
    GROUP BY a.Name, a.AnnualRevenue
    ORDER BY a.AnnualRevenue DESC
    LIMIT 10
"""

# Use compact format for token efficiency
result = execute_query_compact(query)
print(json.dumps(result, indent=2))
```

### Example 3: Formatted Output for Display

```python
from connect_ai_client import execute_query, format_query_results

query = """
    SELECT Status, COUNT(*) as Count
    FROM Zendesk_Integraite.Zendesk.Tickets
    GROUP BY Status
    ORDER BY Count DESC
"""

result = execute_query(query)
print(format_query_results(result))

# Output:
# Status  | Count
# --------+------
# open    | 150
# pending | 89
# closed  | 1250
```

### Example 4: Use in Data Processing Pipeline

```python
import pandas as pd
from connect_ai_client import execute_query_compact

# Get data
data = execute_query_compact(
    'SELECT * FROM Salesforce_Integraite.Salesforce.Opportunity WHERE Stage = "Closed Won"'
)

# Convert to pandas DataFrame
df = pd.DataFrame(data)

# Process
df['CloseMonth'] = pd.to_datetime(df['CloseDate']).dt.to_period('M')
monthly_revenue = df.groupby('CloseMonth')['Amount'].sum()

print(monthly_revenue)
```

### Example 5: Automated Reporting Script

```python
#!/usr/bin/env python3
"""
Daily sales report - runs via cron without LLM
"""
import os
from datetime import datetime
from connect_ai_client import execute_query_compact

def generate_daily_report():
    query = """
        SELECT
            Account.Name,
            SUM(Opportunity.Amount) as Revenue,
            COUNT(Opportunity.Id) as Deals
        FROM Salesforce_Integraite.Salesforce.Opportunity
        JOIN Salesforce_Integraite.Salesforce.Account
            ON Opportunity.AccountId = Account.Id
        WHERE Opportunity.CloseDate >= CURRENT_DATE - 7
        AND Opportunity.StageName = 'Closed Won'
        GROUP BY Account.Name
        ORDER BY Revenue DESC
        LIMIT 20
    """

    results = execute_query_compact(query)

    # Generate report
    print(f"Weekly Sales Report - {datetime.now().strftime('%Y-%m-%d')}")
    print("=" * 60)
    for row in results:
        print(f"{row['Name']}: ${row['Revenue']:,.2f} ({row['Deals']} deals)")

if __name__ == '__main__':
    generate_daily_report()
```

## Token Efficiency Comparison

Based on real-world benchmarks:

| Operation | Standard Query | Compact Query | Savings |
|-----------|---------------|---------------|---------|
| List 10 tables | ~11,000 tokens | ~3,800 tokens | **65%** |
| Top accounts query | ~1,500 tokens | ~1,000 tokens | **34%** |
| Cross-system join | ~2,100 tokens | ~870 tokens | **58%** |

**Always use `execute_query_compact()` for recurring queries and automation.**

## Error Handling

```python
from connect_ai_client import execute_query_compact

try:
    result = execute_query_compact('SELECT * FROM InvalidTable')
except ValueError as e:
    print(f'Configuration error: {e}')
except Exception as e:
    print(f'API error: {e}')
```

## Integration with LangChain

```python
from langchain.tools import Tool
from connect_ai_client import execute_query_compact

def query_connect_ai(query: str) -> str:
    """Execute SQL query via Connect AI"""
    import json
    result = execute_query_compact(query)
    return json.dumps(result, indent=2)

connect_ai_tool = Tool(
    name="query_connect_ai",
    func=query_connect_ai,
    description="Execute SQL queries across 250+ data sources via Connect AI"
)

# Use in agent
from langchain.agents import initialize_agent
agent = initialize_agent([connect_ai_tool], llm, agent="zero-shot-react-description")
```

## Running Examples

```bash
# Set credentials
export CONNECT_AI_EMAIL="your-email@example.com"
export CONNECT_AI_TOKEN="your-token"

# Run examples
python examples/python_examples.py
```

## Best Practices

1. **Use compact queries for automation**: `execute_query_compact()` saves 58-65% tokens
2. **Cache metadata**: Call `get_catalogs()`, `get_schemas()`, `get_tables()` once, reuse results
3. **Fully qualify table names**: Always use `catalog.schema.table` format
4. **Start with LIMIT**: Test queries with `LIMIT 10` before running on full dataset
5. **Handle errors gracefully**: Wrap API calls in try/except blocks
6. **Secure credentials**: Never hardcode tokens - use environment variables

## License

Same as Connect AI skill package.
