
dev-build:
	docker-compose -f dev-compose.yml build
dev-up:
	docker-compose -f dev-compose.yml up

prod-build:
	docker-compose  -f prod-compose.yml build

prod-build:
	docker-compose  -f prod-compose.yml up
