import redis
import os
class RedisClient:
    def __init__(self):
        self.redis_url = os.getenv("REDIS_URL", "redis://redis:6379")
        self.redis_client = None
        
    def get_redis_client(self):
        if not self.redis_client:
            self.redis_client = redis.Redis.from_url(self.redis_url, decode_responses=True)
        return self.redis_client
    
    def publish_update(self, stream_name, payload):
        client = self.get_redis_client()
        return client.xadd(stream_name, payload)