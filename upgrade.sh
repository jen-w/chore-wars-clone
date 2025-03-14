#!/bin/bash -e
docker build -t chore-wars:$(date +%s) -t chore-wars:latest .
docker ps --filter "name=chore-wars" --quiet | grep -q . && docker stop chore-wars
source run.sh
