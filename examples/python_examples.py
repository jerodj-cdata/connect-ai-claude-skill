"""
Connect AI Python Client - Usage Examples

Demonstrates how to use the Python client for Connect AI operations.
"""

import os
import sys
import json

# Add parent directory to path to import the client
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from connect_ai_client import (
    get_catalogs,
    get_schemas,
    get_tables,
    execute_query,
    execute_query_compact,
    format_query_results
)


def example_list_connections():
    """Example: List all available connections"""
    print("=" * 60)
    print("EXAMPLE: List Available Connections")
    print("=" * 60)

    catalogs = get_catalogs()
    print(f"\nFound {len(catalogs)} connections:")
    for catalog in catalogs:
        print(f"  - {catalog.catalogName}")

    return catalogs


def example_explore_schema(catalog_name):
    """Example: Explore schemas and tables in a catalog"""
    print("\n" + "=" * 60)
    print(f"EXAMPLE: Explore Schema - {catalog_name}")
    print("=" * 60)

    # Get schemas
    schemas = get_schemas(catalog_name)
    print(f"\nSchemas in {catalog_name}:")
    for schema in schemas:
        print(f"  - {schema.TABLE_SCHEMA}")

    # Get tables for first schema
    if schemas:
        schema_name = schemas[0].TABLE_SCHEMA
        tables = get_tables(catalog_name=catalog_name, schema_name=schema_name)

        print(f"\nFirst 10 tables in {catalog_name}.{schema_name}:")
        for table in tables[:10]:
            print(f"  - {table.TABLE_NAME} ({table.TABLE_TYPE})")


def example_simple_query(catalog_name, schema_name, table_name):
    """Example: Execute a simple query and format results"""
    print("\n" + "=" * 60)
    print(f"EXAMPLE: Simple Query")
    print("=" * 60)

    query = f"SELECT * FROM {catalog_name}.{schema_name}.{table_name} LIMIT 5"
    print(f"\nQuery: {query}\n")

    result = execute_query(query)
    print(format_query_results(result))


def example_cross_system_query():
    """Example: Cross-system query with optimized compact output"""
    print("\n" + "=" * 60)
    print(f"EXAMPLE: Cross-System Query (Salesforce + Zendesk)")
    print("=" * 60)

    query = """
        SELECT
            a.Name AS AccountName,
            a.AnnualRevenue,
            COUNT(t.Id) AS TotalTickets
        FROM Salesforce_Integraite.Salesforce.Account a
        LEFT JOIN Zendesk_Integraite.Zendesk.Tickets t
            ON a.Id = t.AccountId
        WHERE a.AnnualRevenue IS NOT NULL
        GROUP BY a.Name, a.AnnualRevenue
        ORDER BY a.AnnualRevenue DESC
        LIMIT 10
    """

    print(f"Query: {query}\n")

    # Use compact format for token efficiency
    result = execute_query_compact(query)
    print("Results (compact JSON):")
    print(json.dumps(result, indent=2))


def example_aggregation_query(catalog_name, schema_name):
    """Example: Aggregation query with formatted output"""
    print("\n" + "=" * 60)
    print(f"EXAMPLE: Aggregation Query")
    print("=" * 60)

    query = f"""
        SELECT
            Status,
            COUNT(*) as Count
        FROM {catalog_name}.{schema_name}.Tickets
        GROUP BY Status
        ORDER BY Count DESC
    """

    print(f"Query: {query}\n")

    result = execute_query(query)
    print("Results (formatted table):")
    print(format_query_results(result))


def main():
    """Run all examples"""

    # Set up credentials (if not already in environment)
    if not os.environ.get('CONNECT_AI_EMAIL'):
        print("Please set CONNECT_AI_EMAIL and CONNECT_AI_TOKEN environment variables")
        print("\nExample:")
        print('  export CONNECT_AI_EMAIL="your-email@example.com"')
        print('  export CONNECT_AI_TOKEN="your-token-here"')
        return

    try:
        # Example 1: List connections
        catalogs = example_list_connections()

        # Example 2: Explore schema
        if catalogs:
            example_explore_schema(catalogs[0].catalogName)

        # Example 3: Simple query (Salesforce Account)
        example_simple_query('Salesforce_Integraite', 'Salesforce', 'Account')

        # Example 4: Cross-system query
        example_cross_system_query()

        # Example 5: Aggregation query (Zendesk Tickets)
        example_aggregation_query('Zendesk_Integraite', 'Zendesk')

        print("\n" + "=" * 60)
        print("All examples completed successfully!")
        print("=" * 60)

    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
