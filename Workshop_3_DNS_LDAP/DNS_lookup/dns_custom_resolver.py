import dns.resolver

custom_resolver = dns.resolver.Resolver()
custom_resolver.nameservers = ['1.1.1.1'] # Cloudflare DNS

domain = "hpc.cedia.edu.ec"
try:
    result = custom_resolver.resolve(domain, 'A')
    for ipval in result:
        print(f"IP (via 1.1.1.1): {ipval.to_text()}")
except Exception as e:
    print(f"Error: {e}")