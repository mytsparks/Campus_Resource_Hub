# AI Development Notes and Interaction Log

Log of all major AI (Copilot, Cursor, etc.) interactions, prompts, and code outcomes will go here.

## Model Context Protocol (MCP) Integration

### Overview

The Campus Resource Hub includes an MCP (Model Context Protocol) server that enables AI agents to safely query and inspect the SQLite database in read-only mode. This allows AI features such as:
- Intelligent search and resource summaries
- Data analysis and reporting
- Context-aware assistance based on actual database content

### MCP Server Implementation

**File:** `mcp_server.py`

The MCP server provides structured, read-only access to the database with the following security features:
- **Read-only mode:** Only SELECT queries are allowed
- **SQL injection prevention:** Parameterized queries required
- **Keyword blocking:** Dangerous SQL keywords (DROP, DELETE, UPDATE, etc.) are blocked
- **Connection safety:** Uses SQLite URI mode with read-only flag

### Available MCP Tools

1. **`query_database`**
   - Execute custom SELECT queries
   - Returns results as JSON
   - Parameters: `query` (string), `params` (array, optional)

2. **`get_table_schema`**
   - Get schema information for a specific table
   - Parameters: `table_name` (string)

3. **`list_tables`**
   - List all tables in the database
   - No parameters required

4. **`get_resource_summary`**
   - Get comprehensive summary of a resource including bookings and reviews
   - Parameters: `resource_id` (integer)

5. **`search_resources`**
   - Search resources by keyword, category, or location
   - Parameters: `keyword` (string, optional), `category` (string, optional), `location` (string, optional), `limit` (integer, default: 10)

### Available MCP Resources

- **`schema://database`**: Complete database schema documentation in JSON format

### Usage Example

To use the MCP server with an AI agent (e.g., Claude Desktop, Cursor):

1. **Configure MCP client** (example for Claude Desktop):
   ```json
   {
     "mcpServers": {
       "campus-resource-hub": {
         "command": "python",
         "args": ["/path/to/Campus_Resource_Hub/mcp_server.py"]
       }
     }
   }
   ```

2. **Query the database**:
   ```
   Use the query_database tool to get all published resources
   ```

3. **Get resource summary**:
   ```
   Use get_resource_summary to get details about resource ID 1
   ```

### Security Considerations

- All database access is **read-only** - no modifications possible
- SQL injection protection via parameterized queries
- Dangerous SQL keywords are blocked
- Database connection uses SQLite URI mode with `mode=ro` flag

### Database Location

The database file is located at: `instance/site.db`

The MCP server automatically detects the database path relative to the project root.

### Installation

The MCP server requires the `mcp` Python package:

```bash
# Install MCP dependencies
pip install -r requirements.txt

# Or install MCP directly
pip install mcp>=0.9.0
```

**Note:** If the `mcp` package is not available on PyPI, you may need to install it from the official MCP Python SDK repository:
```bash
pip install git+https://github.com/modelcontextprotocol/python-sdk.git
```

### Testing the MCP Server

To test the MCP server manually:

```bash
# Run the server (will use stdio for communication)
python mcp_server.py
```

The server communicates via stdio, so it's designed to be used with MCP-compatible clients. For testing, you can use an MCP client or test tool.

### Integration with AI Features

The MCP server enables:
- **Intelligent Search**: AI can query the database to understand resource availability and characteristics
- **Auto-summaries**: Generate summaries of resources, bookings, or user activity
- **Context-aware assistance**: AI can provide help based on actual database state
- **Data analysis**: Generate reports and insights from database content

### Future Enhancements

Potential improvements:
- Add caching for frequently accessed data
- Implement query result pagination
- Add more specialized query tools (e.g., booking analytics)
- Support for database views
- Query result formatting options
