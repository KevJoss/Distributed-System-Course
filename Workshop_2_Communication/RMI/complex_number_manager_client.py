import xmlrpc.client

# Create a client proxy
proxy = xmlrpc.client.ServerProxy("http://localhost:12000/complex-manager")

print("Funciones disponibles:", proxy.system.listMethods())

# Call the remote method 'add'
result_add = proxy.add(5, 3, 1, 2)
print("(5, 3j) + (1, 2j) =", result_add)

result_sub = proxy.sub(5, 3, 1, 2)
print("(5, 3j) - (1, 2j) =", result_sub)


result_mul = proxy.prod(5, 3, 1, 2)
print("(5, 3j) * (1, 2j) =", result_mul)

result_div = proxy.div(5, 3, 0, 0)
if result_div == None:
    print("Sorry!, You are dividing by zero ")
else:
    print("(5, 3j)  (1, 2j) =", result_div)