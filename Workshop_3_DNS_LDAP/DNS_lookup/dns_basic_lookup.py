import dns.resolver

domain = "yachaytech.edu.ec"
try:
    result = dns.resolver.resolve(domain, 'A')
    for ipval in result:
        print(f"IP address of {domain}: {ipval.to_text()}")
except Exception as e:
    print(f"Error: {e}")