import dns.reversename
import dns.resolver

ip_address = "8.8.8.8"
try:
    addr = dns.reversename.from_address(ip_address)
    result = dns.resolver.resolve(addr, 'PTR')
    for data in result:
        print(f"Domain for {ip_address}: {data.to_text()}")
except Exception as e:
    print(f"Error: {e}")