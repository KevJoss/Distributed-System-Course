import dns.resolver

domain = "yachaytech.edu.ec"
record_types = ['MX', 'NS', 'SOA']

for r_type in record_types:
    print(f"\n--- Querying {r_type} Records ---")
    try:
        answers = dns.resolver.resolve(domain, r_type)
        for rdata in answers:
            print(rdata.to_text())
    except Exception as e:
        print(f"Could not retrieve {r_type}: {e}")