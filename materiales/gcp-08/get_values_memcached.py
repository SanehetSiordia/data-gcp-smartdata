import memcache

# Conéctate al servidor Memcached
memcached_host = '10.113.176.4:11211'  # Reemplaza con la dirección IP y puerto de tu servidor Memcached
client = memcache.Client([memcached_host])

# Recupera datos de Memcached
data = client.get('datos_usuario')

if data:
    print('Datos del usuario:')
    print(f'Nombre: {data["nombre"]}')
    print(f'Edad: {data["edad"]}')
    print(f'Ciudad: {data["ciudad"]}')
else:
    print('No se encontraron datos del usuario en Memcached.')

# Cierra la conexión con Memcached
client.disconnect_all()
