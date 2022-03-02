#!/bin/bash
## Initiate the project .env files

ENV_EXAMPLE_FILE=".env.example"
ENV_TEST=".env.test"
cp "$ENV_TEST" .env
cp docker/db/"$ENV_EXAMPLE_FILE" docker/db/.env
cp docker-compose.override.example.yml docker-compose.override.yml
