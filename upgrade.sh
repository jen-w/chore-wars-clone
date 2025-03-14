docker build -t chore-wars:$(date +%s) -t chore-wars:latest .
docker stop chore-wars
source run.sh
