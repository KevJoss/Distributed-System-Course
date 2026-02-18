from xmlrpc.server import SimpleXMLRPCServer
from xmlrpc.server import SimpleXMLRPCRequestHandler

# Restrict to a particular path.
class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/complex-manager',)

# Create server
with SimpleXMLRPCServer(('localhost', 12000),
                         requestHandler=RequestHandler,
                         allow_none=True) as server:
    server.register_introspection_functions()

    # Register a function under a different name
    def add(a,b,c,d):
        """
        A function that defines a sum between two complex numbers.
        """
        x = complex(a,b)
        y = complex(c,d)
        print(x)
        print(y)
        res = x + y
        return [res.real, res.imag]

    def sub(a,b,c,d):
        """
        A function that defines a subtraction between two complex numbers.
        """
        x = complex(a,b)
        y = complex(c,d)
        res = x - y
        return [res.real, res.imag]
    
    def prod(a,b,c,d):
        """
        A function that defines a product between two complex numbers.
        """
        x = complex(a,b)
        y = complex(c,d)
        res = x * y
        return [res.real, res.imag]
    
    def div(a,b,c,d):
        """
        A function that defines a division between two complex numbers.
        """
        x = complex(a,b)
        y = complex(c,d)
        try:
            res = x / y
        except ZeroDivisionError:
            return None
        return [res.real, res.imag]
    

    server.register_function(add,'add')
    server.register_function(sub,'sub')
    server.register_function(prod,'prod')
    server.register_function(div,'div')

    # Run the server's main loop
    print("Server is listening on port 12000...")
    server.serve_forever()