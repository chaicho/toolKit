import redis

r = redis.Redis(host='127.0.0.1', port=6379)

# Replaces execQuerySQL
def is_downloaded(project_name, version):
    return r.hexists('projects', project_name + ':' + version)

# Replaces execInsertSQL
def mark_downloaded(project_name, version):
    r.hset('projects', project_name + ':' + version, 1) 


if __name__ == '__main__':
    print(is_downloaded('a', '1'))
    mark_downloaded('a', '1')
    print(is_downloaded('a', '1'))
    print(is_downloaded('a', '2'))