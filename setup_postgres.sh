#!/bin/bash
# Quick setup script for PostgreSQL connection
# This sets up environment variables for local development

echo "Setting up PostgreSQL connection for Campus Resource Hub"
echo ""

# Set DATABASE_URL environment variable
export DATABASE_URL="postgresql://postgres:rpLvgOls4fFSUKb3@db.hjhqgmkltsfscgfehipf.supabase.co:5432/postgres"

echo "DATABASE_URL has been set to:"
echo "$DATABASE_URL"
echo ""
echo "To make this permanent, add it to your .env file:"
echo "DATABASE_URL=$DATABASE_URL"
echo ""
echo "You can now run the application with:"
echo "python application.py"
echo ""
echo "Or with gunicorn:"
echo "gunicorn -w 2 --threads 2 --bind 0.0.0.0:5000 application:application"

