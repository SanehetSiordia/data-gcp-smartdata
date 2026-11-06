import redis

# Conéctate a tu instancia de Redis en Memorystore
redis_host = '10.50.128.107'
redis_port = 6379  # El puerto predeterminado para Redis

try:
    r = redis.StrictRedis(host=redis_host, port=redis_port, decode_responses=True)

    # Agrega elementos a una lista
    lista_key = 'mis_tareas'

    # Obtiene todos los elementos de la lista
    elementos_lista = r.lrange(lista_key, 0, -1)
    print(f'Tareas pendientes: {elementos_lista}')

    # Agrega elementos a un conjunto
    conjunto_key = 'mis_amigos'

    # Obtiene todos los miembros del conjunto
    miembros_conjunto = r.smembers(conjunto_key)
    print(f'Mis amigos: {miembros_conjunto}')

    # Almacena información de usuario en un hash
    usuario_key = 'usuario:12345'

    # Obtiene información de usuario del hash
    nombre_usuario = r.hget(usuario_key, 'nombre')
    edad_usuario = r.hget(usuario_key, 'edad')
    correo_usuario = r.hget(usuario_key, 'correo')

    print(f'Nombre: {nombre_usuario}, Edad: {edad_usuario}, Correo: {correo_usuario}')

except Exception as e:
    print(f"Error: {e}")

