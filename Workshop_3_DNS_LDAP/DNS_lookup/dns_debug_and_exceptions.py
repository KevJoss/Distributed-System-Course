import dns.resolver

def test_dns(domain_name):
    try:
        answer = dns.resolver.resolve(domain_name, 'A')
        
        print(f"DEBUG info for {domain_name}:")
        print(f"Response Flags: {dns.flags.to_text(answer.response.flags)}")
        print(f"TTL: {answer.rrset.ttl}")
        
    except dns.resolver.NXDOMAIN:
        print(f"ERROR: The domain '{domain_name}' does not exist (NXDOMAIN).")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

test_dns("yachaytech.edu.ec")

print("-" * 30)

test_dns("nonexistdomain12345.com")