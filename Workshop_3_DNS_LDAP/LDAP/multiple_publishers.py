import zmq, time, random, ldap
import ldap.modlist as modlist

# --- 1. REGISTRO EN LDAP ---
ldap_server = "ldap://localhost"
admin_dn = "cn=admin,dc=ShonyALV,dc=com"
admin_pw = "a"
service_dn = "cn=Servicio_PubSub,ou=Groups,dc=ShonyALV,dc=com"

HOST = 'localhost'
PORT = '15000'
connection_string = f"tcp://{HOST}:{PORT}"

try:
    print("Conectando a LDAP para registrar el servicio...")
    conn = ldap.initialize(ldap_server)
    conn.simple_bind_s(admin_dn, admin_pw)

    # Definimos los atributos del servicio
    attrs = {}
    attrs['objectClass'] = [b'top', b'device']
    attrs['cn'] = [b'Servicio_PubSub']
    attrs['description'] = [connection_string.encode('utf-8')]

    # Formateamos para ldapadd
    ldif = modlist.addModlist(attrs)
    
    try:
        conn.add_s(service_dn, ldif)
        print("¡Servicio registrado exitosamente en LDAP!")
    except ldap.ALREADY_EXISTS:
        # Si ya existe de una ejecución anterior, simplemente lo actualizamos
        modify_modlist = [(ldap.MOD_REPLACE, 'description', [connection_string.encode('utf-8')])]
        conn.modify_s(service_dn, modify_modlist)
        print("¡Servicio actualizado en LDAP!")
        
    conn.unbind_s()
except Exception as e:
    print(f"Error con LDAP: {e}")
    exit(1)

# --- 2. LÓGICA DE ZEROMQ ---
context = zmq.Context()
publisher = context.socket(zmq.PUB)
publisher.bind(connection_string)
print(f"Publicador enviando datos en {connection_string}...")

while True:
    time.sleep(1)

    # Publisher for SysAdmin
    cpu = random.randint(0,100)
    ram = random.randint(8,32)
    publisher.send_string(f"SYSADMIN CPU usage: {cpu}%")
    publisher.send_string(f"SYSADMIN RAM usage: {ram}%")

    # Publisher for finance
    market_shares = random.uniform(150.0, 200.0)
    publisher.send_string(f"STOCK Amazon stock market shares today: {market_shares:.2f}")