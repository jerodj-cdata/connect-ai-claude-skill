# Connect AI Skill

Python-based skill for efficient interaction with Connect AI's REST API, optimized for token efficiency.

## Overview

This skill enables LLMs to discover and query data across 250+ data sources through Connect AI, with **34-65% token savings** compared to MCP.

## Key Features

- 🚀 **Token Optimized**: 34-65% savings vs MCP
- 🔍 **Metadata Discovery**: Explore catalogs, schemas, and tables
- 💾 **Cross-System Queries**: Join Salesforce, Zendesk, databases in single SQL
- 🐍 **Python Native**: Clean API with type hints and dataclasses
- 📊 **Data Science Ready**: Pandas, NumPy, Jupyter integration
- 🤖 **LLM Friendly**: Works with Claude, GPT-4, LangChain, etc.

## Quick Start

```bash
# Install dependencies
pip install requests

# Set credentials
export CONNECT_AI_EMAIL="your-email@example.com"
export CONNECT_AI_TOKEN="your-token"

# Run example
python3 examples/python_examples.py
```

## Token Efficiency

Benchmarked savings vs MCP:

| Operation | MCP Tokens | Skill Tokens | Savings |
|-----------|------------|--------------|---------|
| List 10 tables | 10,912 | 3,842 | **65%** |
| Query top accounts | 1,513 | 1,006 | **34%** |
| Cross-system join | 2,069 | 871 | **58%** |

## Simple Example

```python
from connect_ai_client import execute_query_compact
import json

# Cross-system analytics in one query
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

## Documentation

- **[SKILL.md](SKILL.md)** - Complete skill documentation and API reference
- **[scripts/README.md](scripts/README.md)** - Detailed Python client guide
- **[examples/python_examples.py](examples/python_examples.py)** - Working code examples

## Structure

```
connect-ai/
├── SKILL.md                    # Skill documentation (for Claude)
├── README.md                   # This file
├── requirements.txt            # Python dependencies
├── scripts/
│   ├── README.md              # Python client guide
│   └── connect_ai_client.py   # Main implementation
└── examples/
    └── python_examples.py     # Usage examples
```

## Use Cases

### 1. Interactive Data Exploration (with LLM)
```python
# Claude helps discover and query data
"Show me top accounts with open tickets"
→ Claude uses skill to explore schemas
→ Constructs optimal SQL query
→ Returns insights
```

### 2. Automated Reporting (no LLM needed)
```python
#!/usr/bin/env python3
# daily_report.py - scheduled via cron
from connect_ai_client import execute_query_compact

def daily_sales():
    data = execute_query_compact("SELECT ...")
    # Send email, update dashboard, etc.
```

### 3. Data Science Workflows
```python
import pandas as pd
from connect_ai_client import execute_query_compact

df = pd.DataFrame(execute_query_compact("SELECT ..."))
analysis = df.groupby('Category')['Revenue'].sum()
```

### 4. LLM Agent Integration
```python
from langchain.tools import Tool
from connect_ai_client import execute_query_compact

tool = Tool(
    name="query_data",
    func=execute_query_compact,
    description="Query 250+ data sources via SQL"
)
```

## Authentication

Two environment variables required:
- `CONNECT_AI_EMAIL` - Your Connect AI account email
- `CONNECT_AI_TOKEN` - Your Personal Access Token

Get your token from Connect AI dashboard.

## Requirements

- Python 3.10+ (for modern type hints)
- `requests` library
- Connect AI account with API access

## Best Practices

1. **Use `execute_query_compact()` for automation** - 58-65% token savings
2. **Cache metadata** - Discover once, query many times
3. **Fully qualify table names** - `catalog.schema.table`
4. **Test with LIMIT first** - Avoid large result sets
5. **Handle errors gracefully** - Network issues, auth failures, etc.

## Token Optimization Strategy

### Discovery Phase (First Time)
Use MCP or skill to explore data:
```python
catalogs = get_catalogs()
tables = get_tables(catalog_name="Salesforce_Integraite", schema_name="Salesforce")
```

### Execution Phase (Recurring)
Use `execute_query_compact()` for maximum efficiency:
```python
result = execute_query_compact("SELECT ...")  # 58% token savings
```

### Automation Phase (No LLM)
Call skill directly from scripts, cron, CI/CD - zero LLM tokens!

## Contributing

This is a public, unofficial skill. For issues or feature requests, contact the author.

## License

See Connect AI skill package license.

---

**Ready to start?** See [examples/python_examples.py](examples/python_examples.py) for working code.
