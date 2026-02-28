import dns.resolver

target = "www.microsoft.com"
try:
    answers = dns.resolver.resolve(target, 'CNAME')
    for rdata in answers:
        print(f"CNAME for {target}: {rdata.target}")
except dns.resolver.NoAnswer:
    print(f"No CNAME record found for {target}")