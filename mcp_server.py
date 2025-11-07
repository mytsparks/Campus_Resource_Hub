#!/usr/bin/env python3
"""
MCP Server for Campus Resource Hub Database Access

This MCP server provides read-only access to the SQLite database for AI agents.
It enables structured, safe database queries for features such as:
- Intelligent search and summaries
- Data analysis and reporting
- Context-aware AI assistance

Security: All queries are read-only and use parameterized statements to prevent SQL injection.
"""

import asyncio
import json
import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, List, Optional

from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.server.stdio import stdio_server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
)


# Database configuration
DB_PATH = Path(__file__).parent / "instance" / "site.db"
SCHEMA_PATH = Path(__file__).parent / "docs" / "mcp_schema.json"


class ReadOnlyDatabase:
    """Read-only database connection manager with safety checks."""
    
    def __init__(self, db_path: Path):
        self.db_path = db_path
        if not db_path.exists():
            raise FileNotFoundError(f"Database not found at {db_path}")
    
    @contextmanager
    def get_connection(self):
        """Get a read-only database connection."""
        conn = sqlite3.connect(f"file:{self.db_path}?mode=ro", uri=True)
        conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        try:
            yield conn
        finally:
            conn.close()
    
    def execute_query(self, query: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """
        Execute a read-only SELECT query safely.
        
        Args:
            query: SQL SELECT query (must start with SELECT)
            params: Query parameters for safety
        
        Returns:
            List of dictionaries representing rows
        
        Raises:
            ValueError: If query is not a SELECT statement
        """
        # Security: Only allow SELECT queries
        query_upper = query.strip().upper()
        if not query_upper.startswith("SELECT"):
            raise ValueError("Only SELECT queries are allowed (read-only mode)")
        
        # Block dangerous SQL keywords
        dangerous_keywords = ["DROP", "DELETE", "UPDATE", "INSERT", "ALTER", "CREATE", "TRUNCATE"]
        for keyword in dangerous_keywords:
            if keyword in query_upper:
                raise ValueError(f"Query contains forbidden keyword: {keyword}")
        
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            columns = [description[0] for description in cursor.description]
            rows = cursor.fetchall()
            return [dict(zip(columns, row)) for row in rows]
    
    def get_table_schema(self, table_name: str) -> Dict[str, Any]:
        """Get schema information for a table."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            return {
                "table": table_name,
                "columns": [
                    {
                        "name": col[1],
                        "type": col[2],
                        "not_null": bool(col[3]),
                        "default": col[4],
                        "primary_key": bool(col[5])
                    }
                    for col in columns
                ]
            }
    
    def list_tables(self) -> List[str]:
        """List all tables in the database."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
            return [row[0] for row in cursor.fetchall()]


# Initialize database connection
db = ReadOnlyDatabase(DB_PATH)

# Initialize MCP server
server = Server("campus-resource-hub-db")


@server.list_tools()
async def list_tools() -> List[Tool]:
    """List available MCP tools for database queries."""
    return [
        Tool(
            name="query_database",
            description="Execute a read-only SELECT query on the database. Returns results as JSON.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "SQL SELECT query to execute. Must be a SELECT statement only."
                    },
                    "params": {
                        "type": "array",
                        "description": "Optional parameters for the query (for parameterized queries)",
                        "items": {"type": "string"},
                        "default": []
                    }
                },
                "required": ["query"]
            }
        ),
        Tool(
            name="get_table_schema",
            description="Get schema information for a specific database table.",
            inputSchema={
                "type": "object",
                "properties": {
                    "table_name": {
                        "type": "string",
                        "description": "Name of the table to inspect"
                    }
                },
                "required": ["table_name"]
            }
        ),
        Tool(
            name="list_tables",
            description="List all tables in the database.",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="get_resource_summary",
            description="Get a summary of a specific resource by ID, including bookings and reviews.",
            inputSchema={
                "type": "object",
                "properties": {
                    "resource_id": {
                        "type": "integer",
                        "description": "ID of the resource to summarize"
                    }
                },
                "required": ["resource_id"]
            }
        ),
        Tool(
            name="search_resources",
            description="Search resources by keyword, category, or location. Returns matching resources with basic info.",
            inputSchema={
                "type": "object",
                "properties": {
                    "keyword": {
                        "type": "string",
                        "description": "Search keyword (searches title and description)"
                    },
                    "category": {
                        "type": "string",
                        "description": "Filter by category (optional)"
                    },
                    "location": {
                        "type": "string",
                        "description": "Filter by location (optional)"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of results (default: 10)",
                        "default": 10
                    }
                }
            }
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool calls."""
    
    if name == "query_database":
        query = arguments.get("query")
        params = tuple(arguments.get("params", []))
        
        try:
            results = db.execute_query(query, params)
            return [
                TextContent(
                    type="text",
                    text=json.dumps(results, indent=2, default=str)
                )
            ]
        except Exception as e:
            return [
                TextContent(
                    type="text",
                    text=f"Error executing query: {str(e)}"
                )
            ]
    
    elif name == "get_table_schema":
        table_name = arguments.get("table_name")
        try:
            schema = db.get_table_schema(table_name)
            return [
                TextContent(
                    type="text",
                    text=json.dumps(schema, indent=2)
                )
            ]
        except Exception as e:
            return [
                TextContent(
                    type="text",
                    text=f"Error getting schema: {str(e)}"
                )
            ]
    
    elif name == "list_tables":
        try:
            tables = db.list_tables()
            return [
                TextContent(
                    type="text",
                    text=json.dumps({"tables": tables}, indent=2)
                )
            ]
        except Exception as e:
            return [
                TextContent(
                    type="text",
                    text=f"Error listing tables: {str(e)}"
                )
            ]
    
    elif name == "get_resource_summary":
        resource_id = arguments.get("resource_id")
        try:
            # Get resource details
            resource_query = """
                SELECT r.*, u.name as owner_name, u.email as owner_email
                FROM resources r
                LEFT JOIN users u ON r.owner_id = u.user_id
                WHERE r.resource_id = ?
            """
            resources = db.execute_query(resource_query, (resource_id,))
            
            if not resources:
                return [TextContent(type="text", text=f"Resource {resource_id} not found")]
            
            resource = resources[0]
            
            # Get booking count
            booking_query = "SELECT COUNT(*) as count FROM bookings WHERE resource_id = ?"
            booking_count = db.execute_query(booking_query, (resource_id,))[0]["count"]
            
            # Get review stats
            review_query = """
                SELECT 
                    COUNT(*) as total_reviews,
                    AVG(rating) as avg_rating
                FROM reviews
                WHERE resource_id = ?
            """
            review_stats = db.execute_query(review_query, (resource_id,))[0]
            
            summary = {
                "resource": resource,
                "statistics": {
                    "total_bookings": booking_count,
                    "total_reviews": review_stats["total_reviews"] or 0,
                    "average_rating": round(review_stats["avg_rating"] or 0, 2)
                }
            }
            
            return [
                TextContent(
                    type="text",
                    text=json.dumps(summary, indent=2, default=str)
                )
            ]
        except Exception as e:
            return [
                TextContent(
                    type="text",
                    text=f"Error getting resource summary: {str(e)}"
                )
            ]
    
    elif name == "search_resources":
        keyword = arguments.get("keyword", "")
        category = arguments.get("category")
        location = arguments.get("location")
        limit = arguments.get("limit", 10)
        
        try:
            query = """
                SELECT 
                    resource_id,
                    title,
                    description,
                    category,
                    location,
                    capacity,
                    status,
                    created_at
                FROM resources
                WHERE status = 'published'
            """
            params = []
            
            if keyword:
                query += " AND (title LIKE ? OR description LIKE ?)"
                keyword_param = f"%{keyword}%"
                params.extend([keyword_param, keyword_param])
            
            if category:
                query += " AND category = ?"
                params.append(category)
            
            if location:
                query += " AND location = ?"
                params.append(location)
            
            query += " ORDER BY created_at DESC LIMIT ?"
            params.append(limit)
            
            results = db.execute_query(query, tuple(params))
            
            return [
                TextContent(
                    type="text",
                    text=json.dumps({"results": results, "count": len(results)}, indent=2, default=str)
                )
            ]
        except Exception as e:
            return [
                TextContent(
                    type="text",
                    text=f"Error searching resources: {str(e)}"
                )
            ]
    
    else:
        return [
            TextContent(
                type="text",
                text=f"Unknown tool: {name}"
            )
        ]


@server.list_resources()
async def list_resources() -> List[Resource]:
    """List available resources (database schema documentation)."""
    return [
        Resource(
            uri="schema://database",
            name="Database Schema",
            description="Complete database schema documentation",
            mimeType="application/json"
        )
    ]


@server.get_resource()
async def get_resource(uri: str) -> List[TextContent]:
    """Get resource content (database schema)."""
    if uri == "schema://database":
        try:
            tables = db.list_tables()
            schema = {}
            for table in tables:
                schema[table] = db.get_table_schema(table)
            
            return [
                TextContent(
                    type="text",
                    text=json.dumps({"database_schema": schema}, indent=2)
                )
            ]
        except Exception as e:
            return [
                TextContent(
                    type="text",
                    text=f"Error getting schema: {str(e)}"
                )
            ]
    else:
        return [
            TextContent(
                type="text",
                text=f"Unknown resource: {uri}"
            )
        ]


async def main():
    """Run the MCP server."""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="campus-resource-hub-db",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=None,
                    experimental_capabilities=None,
                ),
            ),
        )


if __name__ == "__main__":
    asyncio.run(main())

