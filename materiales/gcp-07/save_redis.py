import redis

# Conéctate a tu instancia de Redis en Memorystore
redis_host = '10.50.128.107'
redis_port = 6379  # El puerto predeterminado para Redis

try:
    r = redis.StrictRedis(host=redis_host, port=redis_port, decode_responses=True)

    # Agrega elementos a una lista
    lista_key = 'mis_tareas'
    r.lpush(lista_key, 'Hacer compras de comestibles')
    r.lpush(lista_key, 'Revisar el correo electrónico')
    r.lpush(lista_key, 'Preparar una presentación')

    # Agrega elementos a un conjunto
    conjunto_key = 'mis_amigos'
    r.sadd(conjunto_key, 'Juan')
    r.sadd(conjunto_key, 'Ana')
    r.sadd(conjunto_key, 'Carlos')

    # Almacena información de usuario en un hash
    usuario_key = 'usuario:12345'
    r.hset(usuario_key, 'nombre', 'John Doe')
    r.hset(usuario_key, 'edad', 30)
    r.hset(usuario_key, 'correo', 'john@example.com')

    print('Claves/valores agregados a redis')

except Exception as e:
    print(f"Error: {e}")

