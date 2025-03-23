#!/bin/sh -e

# Check if the 'env' directory exists
if [ ! -d "env" ]; then
    echo "You need to initalize your python venv first. It should be called env"
    exit 1
fi

if [ ! -d "instance" ]; then
    echo "You need to initalize database first. It should be called ./instance/database.db"
    exit 1
fi

source env/bin/activate
flask run --debug
