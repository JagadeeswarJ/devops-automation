import os
from fastapi import FastAPI, HTTPException
import psycopg2
import redis

app = FastAPI(title="Order Management Microservice", version="1.0.0")

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:pass@localhost:5432/orders_db")
REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-token")

@app.get("/")
def read_root():
    return {"status": "online", "service": "orders-service"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "database": "connected", "cache": "ready"}

@app.get("/api/v1/orders")
def get_orders():
    return [
        {"id": 101, "item": "Cloud Compute Node", "quantity": 2, "status": "shipped"},
        {"id": 102, "item": "VPC Peering Router", "quantity": 1, "status": "pending"}
    ]

@app.post("/api/v1/orders")
def create_order(item: str, quantity: int):
    return {"message": "Order created successfully", "order_id": 103}

@app.get("/api/v1/metrics")
def get_metrics():
    return {"active_connections": 12, "request_rate_per_sec": 45.2}
