
dev-build:
	docker-compose -f dev-compose.yml build
dev-up:
	docker-compose -f dev-compose.yml up

prod-build:
	docker-compose  -f docker-compose.yml build

prod-up:
	docker-compose  -f docker-compose.yml up
