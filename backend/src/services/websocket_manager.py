import json
import asyncio
from typing import Dict, Set, Any
from fastapi import WebSocket

class ConnectionManager:
    """Manages WebSocket connections and Redis Pub/Sub subscriptions"""
    
    def __init__(self):
        # Track active connections by vehicle_id
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        # Track Redis pubsub subscriptions
        self.pubsubs: Dict[str, Any] = {}
        # Background tasks for pubsub listeners
        self.pubsub_tasks: Dict[str, asyncio.Task] = {}
    
    async def connect(self, websocket: WebSocket, vehicle_id: str):
        """Accept a WebSocket connection"""
        await websocket.accept()
        if vehicle_id not in self.active_connections:
            self.active_connections[vehicle_id] = set()
        self.active_connections[vehicle_id].add(websocket)
    
    def disconnect(self, websocket: WebSocket, vehicle_id: str):
        """Remove a WebSocket connection"""
        if vehicle_id in self.active_connections:
            self.active_connections[vehicle_id].discard(websocket)
            if not self.active_connections[vehicle_id]:
                del self.active_connections[vehicle_id]
                # Clean up pubsub if no more connections
                if vehicle_id in self.pubsub_tasks:
                    self.pubsub_tasks[vehicle_id].cancel()
                    del self.pubsub_tasks[vehicle_id]
                if vehicle_id in self.pubsubs:
                    try:
                        self.pubsubs[vehicle_id].close()
                    except:
                        pass
                    del self.pubsubs[vehicle_id]
    
    def set_redis(self, redis_client):
        """Set Redis client (called from main.py lifespan)."""
        self._redis_client = redis_client

    def _redis(self):
        """Get Redis client; must be set via set_redis() in lifespan."""
        return getattr(self, '_redis_client', None)

    async def update_vehicle_location(
        self,
        vehicle_id: str,
        latitude: float,
        longitude: float,
        speed: float = None,
        heading: float = None,
        accuracy: float = None,
        timestamp: str = None
    ):
        """Update vehicle location in Redis and publish to Pub/Sub"""
        redis_client = self._redis()
        if redis_client is None:
            raise RuntimeError("Redis not set on WebSocket manager; ensure lifespan runs first")
        
        location_data = {
            "latitude": latitude,
            "longitude": longitude,
            "timestamp": timestamp
        }
        if speed is not None:
            location_data["speed"] = speed
        if heading is not None:
            location_data["heading"] = heading
        if accuracy is not None:
            location_data["accuracy"] = accuracy
        
        # Store in Redis
        location_key = f"vehicle:{vehicle_id}:location"
        redis_client.set(location_key, json.dumps(location_data), ex=3600)  # Expire after 1 hour
        
        # Publish to Redis channel
        channel = f"vehicle:{vehicle_id}:updates"
        redis_client.publish(channel, json.dumps(location_data))
    
    async def broadcast_to_vehicle(self, vehicle_id: str, message: dict):
        """Broadcast a message to all WebSocket connections for a vehicle"""
        if vehicle_id in self.active_connections:
            disconnected = set()
            for connection in self.active_connections[vehicle_id]:
                try:
                    await connection.send_json(message)
                except Exception:
                    disconnected.add(connection)
            
            # Remove disconnected connections
            for conn in disconnected:
                self.active_connections[vehicle_id].discard(conn)
    
    async def subscribe_to_vehicle(self, vehicle_id: str):
        """Subscribe to Redis Pub/Sub channel for a vehicle and broadcast updates"""
        if vehicle_id in self.pubsub_tasks:
            # Already subscribed
            return
        
        redis_client = self._redis()
        if redis_client is None:
            raise RuntimeError("Redis not set on WebSocket manager; ensure lifespan runs first")
        channel = f"vehicle:{vehicle_id}:updates"
        pubsub = redis_client.pubsub()
        pubsub.subscribe(channel)
        self.pubsubs[vehicle_id] = pubsub
        
        async def listen_and_broadcast():
            """Listen to Redis messages and broadcast to WebSocket clients"""
            try:
                while True:
                    # Use get_message with timeout in a loop
                    message = pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
                    if message and message.get('type') == 'message':
                        try:
                            data = json.loads(message['data'])
                            await self.broadcast_to_vehicle(vehicle_id, data)
                        except (json.JSONDecodeError, KeyError):
                            continue
                    # Small sleep to prevent busy waiting
                    await asyncio.sleep(0.1)
            except asyncio.CancelledError:
                try:
                    pubsub.unsubscribe(channel)
                    pubsub.close()
                except Exception:
                    pass
            except Exception:
                pass
        
        task = asyncio.create_task(listen_and_broadcast())
        self.pubsub_tasks[vehicle_id] = task


# Global connection manager instance
manager = ConnectionManager()
