"""
Connect AI API Client

Direct API integration for Connect AI metadata discovery and query execution.
Optimized for token efficiency by using REST API instead of MCP.
"""

import os
import json
import base64
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
import requests


BASE_URL = 'https://cloud.cdata.com/api'


@dataclass
class Catalog:
    catalogName: str


@dataclass
class Schema:
    TABLE_CATALOG: str
    TABLE_SCHEMA: str


@dataclass
class Table:
    TABLE_CATALOG: str
    TABLE_SCHEMA: str
    TABLE_NAME: str
    TABLE_TYPE: str
    REMARKS: Optional[str] = None


@dataclass
class ColumnSchema:
    columnName: str
    dataTypeName: str
    nullable: Optional[bool] = None


@dataclass
class QueryResult:
    schema: List[ColumnSchema]
    rows: List[List[Any]]
    affectedRows: Optional[int] = None


def get_auth_credentials() -> tuple[str, str]:
    """Gets authentication credentials from environment variables"""
    email = os.environ.get('CONNECT_AI_EMAIL')
    token = os.environ.get('CONNECT_AI_TOKEN')

    if not email or not token:
        raise ValueError(
            'CONNECT_AI_EMAIL and CONNECT_AI_TOKEN environment variables must be set'
        )

    return email, token


def make_request(endpoint: str, method: str = 'GET', body: Optional[Dict] = None) -> Dict:
    """Makes an authenticated API request using Basic Auth"""
    email, token = get_auth_credentials()

    # Create Basic Auth header: base64(email:token)
    credentials = base64.b64encode(f'{email}:{token}'.encode()).decode()

    headers = {
        'Authorization': f'Basic {credentials}',
        'Content-Type': 'application/json'
    }

    url = f'{BASE_URL}{endpoint}'

    if method == 'GET':
        response = requests.get(url, headers=headers)
    elif method == 'POST':
        response = requests.post(url, headers=headers, json=body)
    else:
        raise ValueError(f'Unsupported HTTP method: {method}')

    if not response.ok:
        raise Exception(
            f'Connect AI API error ({response.status_code}): {response.text}'
        )

    return response.json()


def get_catalogs() -> List[Catalog]:
    """Retrieves all available catalogs (data sources)"""
    response = make_request('/catalogs')

    return [
        Catalog(catalogName=row[0])
        for row in response['results'][0]['rows']
    ]


def get_schemas(catalog_name: Optional[str] = None,
                schema_name: Optional[str] = None) -> List[Schema]:
    """Retrieves schemas, optionally filtered by catalog and/or schema name"""
    params = []
    if catalog_name:
        params.append(f'catalogName={catalog_name}')
    if schema_name:
        params.append(f'schemaName={schema_name}')

    query_string = '&'.join(params)
    endpoint = f'/schemas{"?" + query_string if query_string else ""}'

    response = make_request(endpoint)

    return [
        Schema(TABLE_CATALOG=row[0], TABLE_SCHEMA=row[1])
        for row in response['results'][0]['rows']
    ]


def get_tables(catalog_name: Optional[str] = None,
               schema_name: Optional[str] = None,
               table_name: Optional[str] = None,
               table_type: Optional[str] = None) -> List[Table]:
    """Retrieves tables with optional filtering"""
    params = []
    if catalog_name:
        params.append(f'catalogName={catalog_name}')
    if schema_name:
        params.append(f'schemaName={schema_name}')
    if table_name:
        params.append(f'tableName={table_name}')
    if table_type:
        params.append(f'tableType={table_type}')

    query_string = '&'.join(params)
    endpoint = f'/tables{"?" + query_string if query_string else ""}'

    response = make_request(endpoint)

    return [
        Table(
            TABLE_CATALOG=row[0],
            TABLE_SCHEMA=row[1],
            TABLE_NAME=row[2],
            TABLE_TYPE=row[3],
            REMARKS=row[4] if len(row) > 4 else None
        )
        for row in response['results'][0]['rows']
    ]


def execute_query(query: str,
                 default_schema: Optional[str] = None,
                 schema_only: bool = False,
                 parameters: Optional[Dict[str, Any]] = None) -> QueryResult:
    """Executes a SQL query and returns results"""
    body = {
        'query': query,
        'defaultSchema': default_schema,
        'schemaOnly': schema_only,
        'parameters': parameters or {}
    }

    response = make_request('/query', method='POST', body=body)

    if not response.get('results') or len(response['results']) == 0:
        raise Exception(f'No results returned from query: {json.dumps(response)}')

    result = response['results'][0]

    schema = [
        ColumnSchema(
            columnName=col['columnName'],
            dataTypeName=col['dataTypeName'],
            nullable=col.get('nullable')
        )
        for col in (result.get('schema') or [])
    ]

    return QueryResult(
        schema=schema,
        rows=result.get('rows', []),
        affectedRows=result.get('affectedRows')
    )


def format_query_results(result: QueryResult, compact: bool = False) -> str:
    """Helper function to format query results as a table"""
    if not result.rows or len(result.rows) == 0:
        return 'No results found.'

    # Compact mode: Return minimal JSON array format
    if compact:
        headers = [col.columnName for col in result.schema]
        data = [
            dict(zip(headers, row))
            for row in result.rows
        ]
        return json.dumps(data, indent=2)

    headers = [col.columnName for col in result.schema]

    # Calculate column widths
    column_widths = []
    for i, header in enumerate(headers):
        max_data_width = max(
            len(str(row[i] if i < len(row) else ''))
            for row in result.rows
        )
        column_widths.append(max(len(header), max_data_width))

    # Header row
    header_row = ' | '.join(
        header.ljust(column_widths[i])
        for i, header in enumerate(headers)
    )

    # Separator
    separator = '-+-'.join('-' * width for width in column_widths)

    # Data rows
    data_rows = []
    for row in result.rows:
        formatted_row = ' | '.join(
            str(row[i] if i < len(row) else '').ljust(column_widths[i])
            for i in range(len(headers))
        )
        data_rows.append(formatted_row)

    return '\n'.join([header_row, separator] + data_rows)


def get_table_columns(catalog_name: str,
                     schema_name: str,
                     table_name: str) -> QueryResult:
    """Helper to get column details for a specific table"""
    return execute_query(
        query=f'SELECT * FROM {catalog_name}.{schema_name}.{table_name}',
        schema_only=True
    )


def execute_query_compact(query: str) -> List[Dict[str, Any]]:
    """
    Optimized query execution that returns only essential data.
    Use this for better token efficiency when you don't need full schema metadata.
    """
    result = execute_query(query)
    headers = [col.columnName for col in result.schema]
    return [
        dict(zip(headers, row))
        for row in result.rows
    ]


# Example usage
if __name__ == '__main__':
    # Example: Get catalogs
    catalogs = get_catalogs()
    print('Catalogs:', [c.catalogName for c in catalogs])

    # Example: Get schemas for a catalog
    if catalogs:
        schemas = get_schemas(catalogs[0].catalogName)
        print(f'Schemas in {catalogs[0].catalogName}:',
              [s.TABLE_SCHEMA for s in schemas])

        # Example: Get tables
        if schemas:
            tables = get_tables(
                catalog_name=catalogs[0].catalogName,
                schema_name=schemas[0].TABLE_SCHEMA
            )
            print(f'First 10 tables:',
                  [t.TABLE_NAME for t in tables[:10]])
