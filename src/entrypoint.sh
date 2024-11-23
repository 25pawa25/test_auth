#!/bin/sh

# Load .env
unamestr=$(uname)
if [ "$unamestr" = 'Linux' ]; then
  export $(grep -v '^#' .env | xargs -d '\r')
elif [ "$unamestr" = 'FreeBSD' ] || [ "$unamestr" = 'Darwin' ]; then
  export $(grep -v '^#' .env | xargs -0)
fi

# Check postgres connect
echo "Waiting for postgres..."

while ! nc -z ${DB_HOST} ${DB_PORT} 2>/dev/null; do
  sleep 0.1
done

echo "PostgreSQL started"

# Alembic migrate
echo "Start migrate"
alembic upgrade head

# Start server
COMMAND="$@"

echo "Command $COMMAND"

if [ "$COMMAND" ]; then
  exec $COMMAND
else
  echo "Command not found"
fi
