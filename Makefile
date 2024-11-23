# Wake up docker containers
up:
	docker-compose -f docker-compose.yml up -d

# Shut down docker containers
down:
	docker-compose -f docker-compose.yml down

# Start tests in container
test-user-check:
	docker-compose -f docker-compose.yml exec -e DEBUG=True test_auth sh -c "cd .. && pytest -vv -s tests/test_GRPCAsyncServerUserExisting.py"


# Show logs of each container
logs:
	docker-compose -f docker-compose.yml logs

# Restart all containers
restart: down up

# Build and up docker containers
build:
	docker-compose -f docker-compose.yml build --force-rm

# Build and up docker containers
rebuild:  build up

proto-auth:
	python3 -m grpc_tools.protoc -I=protobuf/ --python_out=src/clients/grpc/proto/auth --grpc_python_out=src/clients/grpc/proto/auth protobuf/auth.proto
	cd src/clients/grpc/proto/auth && sed -i '' 's/^\(import.*pb2\)/from . \1/g' *.py

proto-transaction:
	python3 -m grpc_tools.protoc -I=protobuf/ --python_out=src/clients/grpc/proto/transaction --grpc_python_out=src/clients/grpc/proto/transaction protobuf/transaction.proto
	cd src/clients/grpc/proto/transaction && sed -i '' 's/^\(import.*pb2\)/from . \1/g' *.py
