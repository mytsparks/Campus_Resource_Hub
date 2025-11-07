# MCP Server Setup Guide

## Overview

The Campus Resource Hub includes a Model Context Protocol (MCP) server that provides read-only database access for AI agents. This enables intelligent features like auto-summaries, context-aware search, and data analysis.

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

If the `mcp` package is not available on PyPI, install from the official repository:

```bash
pip install git+https://github.com/modelcontextprotocol/python-sdk.git
```

### 2. Verify Database Exists

The MCP server expects the database at `instance/site.db`. If it doesn't exist, run the Flask app once to create it:

```bash
python app.py
```

### 3. Configure MCP Client

#### For Claude Desktop

Edit your Claude Desktop configuration file (location varies by OS):

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`  
**Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

Add the MCP server configuration:

```json
{
  "mcpServers": {
    "campus-resource-hub": {
      "command": "python",
      "args": ["C:\\Users\\sirgl\\Documents\\AiDD_Team_7_Final\\Campus_Resource_Hub\\mcp_server.py"]
    }
  }
}
```

**Important:** Use the absolute path to `mcp_server.py`.

#### For Other MCP Clients

The MCP server uses stdio for communication, so it's compatible with any MCP client. Configure according to your client's documentation.

## Available Tools

### 1. `query_database`
Execute custom SELECT queries on the database.

**Parameters:**
- `query` (string, required): SQL SELECT query
- `params` (array, optional): Query parameters for safety

**Example:**
```json
{
  "query": "SELECT * FROM resources WHERE status = ? LIMIT 10",
  "params": ["published"]
}
```

### 2. `get_table_schema`
Get schema information for a specific table.

**Parameters:**
- `table_name` (string, required): Name of the table

**Example:**
```json
{
  "table_name": "resources"
}
```

### 3. `list_tables`
List all tables in the database.

**Parameters:** None

### 4. `get_resource_summary`
Get comprehensive summary of a resource including bookings and reviews.

**Parameters:**
- `resource_id` (integer, required): ID of the resource

**Example:**
```json
{
  "resource_id": 1
}
```

### 5. `search_resources`
Search resources by keyword, category, or location.

**Parameters:**
- `keyword` (string, optional): Search keyword
- `category` (string, optional): Filter by category
- `location` (string, optional): Filter by location
- `limit` (integer, optional): Maximum results (default: 10)

**Example:**
```json
{
  "keyword": "study room",
  "category": "Study Room",
  "limit": 5
}
```

## Available Resources

### `schema://database`
Complete database schema documentation in JSON format. Use this to understand the database structure before querying.

## Security Features

- **Read-only access**: Only SELECT queries are allowed
- **SQL injection protection**: Parameterized queries required
- **Keyword blocking**: Dangerous SQL keywords (DROP, DELETE, UPDATE, INSERT, ALTER, CREATE, TRUNCATE) are blocked
- **Connection safety**: Uses SQLite URI mode with read-only flag (`mode=ro`)

## Troubleshooting

### Database Not Found Error

If you see `Database not found at instance/site.db`:

1. Ensure the Flask app has been run at least once to create the database
2. Check that the database file exists at `instance/site.db`
3. Verify the MCP server is running from the project root directory

### Import Errors

If you see import errors for `mcp`:

1. Verify MCP is installed: `pip list | grep mcp`
2. Try installing from GitHub: `pip install git+https://github.com/modelcontextprotocol/python-sdk.git`
3. Check Python version (requires Python 3.10+)

### Connection Issues

If the MCP client can't connect:

1. Verify the absolute path to `mcp_server.py` is correct
2. Ensure Python is in your PATH
3. Test the server manually: `python mcp_server.py` (should start without errors)
4. Check client logs for detailed error messages

## Example Use Cases

### Generate Resource Summary

Ask your AI agent:
```
Use get_resource_summary to get details about resource ID 1 and create a summary
```

### Search for Resources

Ask your AI agent:
```
Use search_resources to find all study rooms in Building A
```

### Analyze Database

Ask your AI agent:
```
Use query_database to get all pending bookings and summarize them
```

## Development

To modify the MCP server:

1. Edit `mcp_server.py`
2. Add new tools in the `list_tools()` function
3. Implement tool handlers in `call_tool()`
4. Test with your MCP client
5. Update documentation in `.prompt/dev_notes.md` and `README.md`

## References

- [Model Context Protocol Documentation](https://modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- See `.prompt/dev_notes.md` for detailed technical documentation

