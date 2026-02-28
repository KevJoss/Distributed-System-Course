# Workshop 3: DNS and LDAP Implementation

This directory contains the implementation of **Workshop 3: DNS and LDAP** for the Distributed Systems course at **Yachay Tech**.

The project demonstrates how to interact with the Domain Name System (DNS) programmatically using Python and the `dnspython` library, covering basic and advanced record lookups, reverse resolution, and error handling.

## 📋 Project Overview

The objective of this section of the workshop is to understand how DNS name resolution works in practice.

### Key Features
*   **Basic DNS Queries:** Retrieval of IPv4 addresses (A records).
*   **Reverse Lookups:** Obtaining the domain name associated with a specific IP (PTR records).
*   **Zone Metadata:** Querying advanced records like Mail Exchange (MX), Name Servers (NS), and Start of Authority (SOA).
*   **CNAME Resolution:** Resolving Canonical Names (Aliases) for services.
*   **Custom Resolvers:** Directing queries to specific public DNS servers (e.g., Cloudflare `1.1.1.1`).
*   **Exception Handling:** Properly managing non-existent domains (`NXDOMAIN`) and timeout errors.

---

## 📂 Project Structure

```text
Workshop_3_DNS_LDAP/
│
└── DNS_lookup/                             # Python DNS scripts
    ├── dns_basic_lookup.py                 # Basic A record queries
    ├── dns_reverse_lookup.py               # PTR record queries (IP to domain)
    ├── dns_zone_metadata.py                # MX, NS, SOA record queries
    ├── dns_cname_alias.py                  # CNAME record queries
    ├── dns_custom_resolver.py              # Querying via Cloudflare DNS
    └── dns_debug_and_exceptions.py         # Response flags and exception handling
```

---

## 🚀 Usage Instructions

### Python Implementation

Ensure you have **Python 3.x** installed and the `dnspython` library.

**Installation:**
```bash
pip install dnspython
```

**Running the scripts:**
Navigate to the `DNS_lookup` directory and run any of the scripts:

```bash
cd DNS_lookup
python dns_basic_lookup.py
python dns_reverse_lookup.py
python dns_zone_metadata.py
python dns_cname_alias.py
python dns_custom_resolver.py
python dns_debug_and_exceptions.py
```

---

## 🧠 Technical Details

*   **dnspython library:** We use this library instead of the standard `socket` module because it provides a much deeper integration with the DNS protocol, allowing us to query specific types of records and inspect the response flags and TTLs.
*   **Error Handling:** DNS queries can fail for multiple reasons (network issues, nonexistent domains). Using `try-except` blocks and specific classes like `dns.resolver.NXDOMAIN` is vital for network robustness.

---

## 👤 Author
**Students:** Kevin Sánchez & Jhony Penaherrera

**Course:** Distributed Systems

**University:** Yachay Tech
