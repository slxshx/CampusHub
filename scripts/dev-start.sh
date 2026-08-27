#!/bin/bash

echo "Starting PostgreSQL..."
brew services start postgresql@17

echo "Starting CampusHub..."
uv run uvicorn campushub.__main__:app --reload
