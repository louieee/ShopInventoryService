import redis

# Connect to Redis server
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)



# Set a key-value pair
redis_client.set('mykey', 'Hello Redis!')

# Get the value for a key
value = redis_client.get('mykey')
print(value.decode())  # Output: Hello Redis!

# Increment a key's value
redis_client.incr('counter')

# Set a key with an expiration time
redis_client.setex('mykey', 10, 'Hello Redis!')

# Delete a key
redis_client.delete('mykey')
