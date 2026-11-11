import memcache

# Conéctate al servidor Memcached
memcached_host = '10.103.0.4:11211'  # Reemplaza con la dirección IP y puerto de tu servidor Memcached
client = memcache.Client([memcached_host])

# Carga datos en Memcached
data = {
    'nombre': 'Juan',
    'edad': 30,
    'ciudad': 'Lima',
}

# Almacena los datos en Memcached con una clave específica
if client.set('datos_usuario', data, time=3600):  # Duración de 1 hora en segundos
    print('Valores agregados con éxito a Memcached')
else:
    print('Error al agregar valores a Memcached')

# Cierra la conexión con Memcached
client.disconnect_all()
