import zmq, random, ldap

# --- 1. CONSULTA A LDAP (Service Discovery) ---
ldap_server = "ldap://localhost"
search_base = "ou=Groups,dc=ShonyALV,dc=com"
search_filter = "(cn=Servicio_PubSub)"

print("Buscando el servicio en LDAP...")
try:
    conn = ldap.initialize(ldap_server)
    # Hacemos bind como administrador (o podrías usar a uid=francisco)
    conn.simple_bind_s("cn=admin,dc=ShonyALV,dc=com", "a") 
    
    # Buscamos el servicio
    result = conn.search_s(search_base, ldap.SCOPE_SUBTREE, search_filter)
    
    if not result:
        print("¡Error: Servicio no encontrado en el directorio LDAP!")
        exit(1)
        
    # Extraemos la IP y el puerto de la descripción
    dn, attrs = result[0]
    connection_string = attrs['description'][0].decode('utf-8')
    print(f"¡Servicio encontrado! Dirección: {connection_string}")
    
    conn.unbind_s()
except Exception as e:
    print(f"Error consultando LDAP: {e}")
    exit(1)


# --- 2. LÓGICA DE ZEROMQ ---
context = zmq.Context()
s = context.socket(zmq.SUB)

# Nos conectamos usando la dirección obtenida de LDAP
s.connect(connection_string)

# Suscribirse a tópicos aleatorios
services = ['SYSADMIN CPU','SYSADMIN RAM','STOCK']
request_services = random.sample(services, k=2)
print("Solicitando tópicos: ", request_services)

s.setsockopt_string(zmq.SUBSCRIBE, request_services[0])
s.setsockopt_string(zmq.SUBSCRIBE, request_services[1])

# Esperamos y recibimos los datos
first_response_service = s.recv().decode("utf-8")
second_response_service = s.recv().decode("utf-8")

print("\n--- Datos Recibidos ---")
print(first_response_service)
print(second_response_service)