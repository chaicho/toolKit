import redis

try:
    redis_host = 'localhost'  # Or use the appropriate IP if running on Linux or Docker Toolbox
    redis_port = 6379
    redis_client = redis.StrictRedis(host=redis_host, port=redis_port, decode_responses=True)
    connection = redis_client.ping()
    # Test the connection by setting and retrieving a key-value pair
    # redis_client.set('my_key1', 'Hello, Redis!')
    # value = redis_client.get('my_key')
    # print(value)  # Output: Hello, Redis!

except Exception as e:
    print(f"An error occurred: {e}")
