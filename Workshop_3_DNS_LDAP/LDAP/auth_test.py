import ldap

ldap_server = "ldap://localhost"
ldap_username = "uid=francisco,ou=People,dc=ShonyALV,dc=com"
ldap_password = "password"

try:
    conn = ldap.initialize(ldap_server)
    conn.simple_bind_s(ldap_username, ldap_password)
    print("Authentication successful!")
except ldap.INVALID_CREDENTIALS:
    print("Authentication failed!")
except Exception as e:
    print(f"Error: {e}")
finally:
    conn.unbind_s()
