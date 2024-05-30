#!/bin/sh

if [ "$ENVIRONMENT" = "lambda" ]; then
  exec python -m awslambdaric main.handler
else
  exec uvicorn main:app --host 0.0.0.0 --port 8080
fi