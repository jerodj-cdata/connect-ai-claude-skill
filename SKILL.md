---
name: connect-ai
description: Use this skill when querying data across multiple systems (Salesforce, Zendesk, databases, APIs) with optimized token efficiency. Provides 34-65% token savings vs MCP for metadata discovery and cross-system SQL queries. Best for recurring queries, automation, and data analysis workflows.
allowed-tools: Bash
---

# Connect AI Skill

Execute SQL queries across 250+ data sources (Salesforce, Zendesk, databases, APIs) using Python with 34-65% token savings vs MCP.

## When to Use This Skill

✅ **Use this skill when:**
- User asks to query or analyze data from Connect AI data sources
- Need to join data across multiple systems (e.g., Salesforce + Zendesk)
- Running recurring queries (automation, reports, dashboards)
- Discovering what data is available (catalogs, schemas, tables)
- User mentions: "data sources", "query", "Salesforce", "database", "analytics"

❌ **Don't use when:**
- User wants to configure Connect AI connections (use web UI)
- Pure conversational questions without data queries
- First-time exploration is better served by MCP (use skill for follow-ups)

## Token Efficiency Strategy

**First Discovery (MCP or Skill)**: Explore what data exists
- Token cost: ~2,000-3,000 tokens
- Learn schema, tables, relationships

**Recurring Queries (Always use Skill)**: Execute known patterns
- Token cost: ~900-1,000 tokens (58-65% savings)
- Use `execute_query_compact()` for maximum efficiency

## Workflow Pattern

### Step 1: Discover Available Data
Use Python to explore Connect AI catalogs:
```bash
python3 -c "from connect_ai_client import get_catalogs; print(get_catalogs())"
```

### Step 2: Construct SQL Query
Based on discovered metadata, construct fully-qualified SQL:
```sql
SELECT a.Name, COUNT(t.Id) as Tickets
FROM Salesforce_Integraite.Salesforce.Account a
LEFT JOIN Zendesk_Integraite.Zendesk.Tickets t ON a.Id = t.AccountId
GROUP BY a.Name
```

### Step 3: Execute with Compact Output
Use `execute_query_compact()` for token efficiency:
```bash
python3 -c "from connect_ai_client import execute_query_compact; ..."
```

### Step 4: Analyze Results
Process JSON output and provide insights to user.

## API Configuration

Base URL: `https://cloud.cdata.com/api`

Authentication: Uses Basic Authentication with credentials from environment variables:
- `CONNECT_AI_EMAIL` - Your Connect AI account email address
- `CONNECT_AI_TOKEN` - Your Personal Access Token (PAT)

The credentials are automatically encoded as `base64(email:token)` and sent in the Authorization header.

## Available Functions

### Metadata Operations

#### Get Catalogs
```python
def get_catalogs() -> List[Catalog]
```
Retrieves all available catalogs (data sources).

**Example:**
```python
from connect_ai_client import get_catalogs

catalogs = get_catalogs()
# Returns: [Catalog(catalogName="Salesforce1"), ...]
```

#### Get Schemas
```python
def get_schemas(catalog_name: Optional[str] = None,
                schema_name: Optional[str] = None) -> List[Schema]
```
Retrieves available schemas, optionally filtered by catalog and/or schema name.

**Parameters:**
- `catalog_name` (optional): Filter by specific catalog
- `schema_name` (optional): Filter by specific schema

**Example:**
```python
from connect_ai_client import get_schemas

schemas = get_schemas("Salesforce_Integraite")
# Returns: [Schema(TABLE_CATALOG="Salesforce_Integraite", TABLE_SCHEMA="Salesforce"), ...]
```

#### Get Tables
```python
def get_tables(catalog_name: Optional[str] = None,
               schema_name: Optional[str] = None,
               table_name: Optional[str] = None,
               table_type: Optional[str] = None) -> List[Table]
```
Retrieves table metadata, optionally filtered by catalog, schema, table name, or type.

**Parameters:**
- `catalog_name` (optional): Filter by specific catalog
- `schema_name` (optional): Filter by specific schema
- `table_name` (optional): Filter by specific table
- `table_type` (optional): Filter by table type

**Example:**
```python
from connect_ai_client import get_tables

tables = get_tables(
    catalog_name="Salesforce_Integraite",
    schema_name="Salesforce"
)
# Returns: [Table(TABLE_CATALOG="Salesforce_Integraite", TABLE_NAME="Account", ...), ...]
```

### Query Operations

#### Execute Query
```python
def execute_query(query: str,
                  default_schema: Optional[str] = None,
                  schema_only: bool = False,
                  parameters: Optional[Dict[str, Any]] = None) -> QueryResult
```
Executes a SQL query and returns full results with schema metadata.

**Parameters:**
- `query` (required): SQL statement (SELECT, INSERT, UPDATE, DELETE)
- `default_schema` (optional): Default schema context
- `schema_only` (optional): Return only column metadata without data
- `parameters` (optional): Query parameters for parameterized queries

**Example:**
```python
from connect_ai_client import execute_query

result = execute_query(
    query="SELECT Id, Name FROM Salesforce_Integraite.Salesforce.Account LIMIT 5"
)
# Returns: QueryResult(schema=[...], rows=[...])
```

#### Execute Query Compact (Optimized)
```python
def execute_query_compact(query: str) -> List[Dict[str, Any]]
```
**Token-optimized query execution** - returns minimal JSON format without schema metadata.

**Use this for maximum token efficiency** (58-65% savings vs standard execution).

**Example:**
```python
from connect_ai_client import execute_query_compact
import json

result = execute_query_compact(
    "SELECT Name, AnnualRevenue FROM Salesforce_Integraite.Salesforce.Account LIMIT 10"
)
print(json.dumps(result, indent=2))
# Returns: [{'Name': 'Acme Corp', 'AnnualRevenue': 1000000}, ...]
```

## Usage Guidelines

### When to Use This Skill

Use this skill when users need to:
- Explore available data sources and their structure
- Discover tables and columns in databases
- Execute SQL queries against Connect AI data sources
- Analyze query results

### Efficient Metadata Discovery

1. Start broad with `getCatalogs()` to see available data sources
2. Narrow down with `getSchemas(catalogName)` to explore specific catalog
3. Get detailed table info with `getTables({ catalogName, schemaName })`
4. Use the metadata to construct accurate SQL queries

### Query Best Practices

1. Always use fully qualified table names: `catalog.schema.table`
2. Start with LIMIT clauses to avoid large result sets
3. Use `schemaOnly: true` when you only need column information
4. For complex queries, validate schema first

### Error Handling

- Check for authentication errors (missing/invalid token)
- Handle API rate limits gracefully
- Validate SQL syntax before execution
- Provide clear error messages to users

## Example Conversation Flow

**User:** "What tables are available in my Salesforce connection?"

**Claude:**
1. Calls `get_catalogs()` to find "Salesforce_Integraite"
2. Calls `get_schemas("Salesforce_Integraite")` to find "Salesforce" schema
3. Calls `get_tables(catalog_name="Salesforce_Integraite", schema_name="Salesforce")`
4. Presents formatted list of tables

**User:** "Show me the top 10 accounts by revenue"

**Claude:**
1. Uses previously discovered metadata to know Account table exists
2. Calls `execute_query_compact("SELECT Name, AnnualRevenue FROM Salesforce_Integraite.Salesforce.Account WHERE AnnualRevenue IS NOT NULL ORDER BY AnnualRevenue DESC LIMIT 10")`
3. Formats and presents results efficiently (using compact mode for token savings)

**Example Usage in Python:**

```python
from connect_ai_client import execute_query_compact
import json

# Cross-system analytics
result = execute_query_compact("""
    SELECT
        a.Name,
        a.AnnualRevenue,
        COUNT(t.Id) AS TotalTickets
    FROM Salesforce_Integraite.Salesforce.Account a
    LEFT JOIN Zendesk_Integraite.Zendesk.Tickets t
        ON a.Id = t.AccountId
    WHERE a.AnnualRevenue IS NOT NULL
    GROUP BY a.Name, a.AnnualRevenue
    ORDER BY a.AnnualRevenue DESC
    LIMIT 10
""")

print(json.dumps(result, indent=2))
```

## Implementation Notes

- **Language**: Python 3.10+ (uses modern type hints)
- **Base URL**: `https://cloud.cdata.com/api`
- **Authentication**: Basic Auth via `CONNECT_AI_EMAIL` and `CONNECT_AI_TOKEN` environment variables
- **Dependencies**: `requests` library (install with `pip install requests`)
- **Location**: `scripts/connect_ai_client.py`

## Token Efficiency

This skill is optimized to reduce token usage by **34-65%** compared to MCP:

**Proven Savings:**
- **65% savings** on table discovery operations
- **34% savings** on simple query execution
- **58% savings** on cross-system join queries

**Optimization Techniques:**
- `execute_query_compact()` returns minimal JSON without schema metadata
- Direct API calls bypass MCP protocol overhead
- Targeted metadata fetching (optional filters)
- Schema-only queries available when you don't need data

**Best Practice**: Use `execute_query_compact()` for all recurring queries and automation to maximize token savings.

## Quick Start

```bash
# Install dependencies
pip install requests

# Set credentials
export CONNECT_AI_EMAIL="your-email@example.com"
export CONNECT_AI_TOKEN="your-token"

# Test the skill
python3 -c "
from connect_ai_client import get_catalogs
catalogs = get_catalogs()
print([c.catalogName for c in catalogs])
"
```

For detailed examples, see `scripts/README.md` and `examples/python_examples.py`.
