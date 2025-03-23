#!/bin/sh -e

docker run --name chore-wars --rm -d -p 80:5000 -v /var/chore-wars-db-instance:/app/instance chore-wars:latest 
