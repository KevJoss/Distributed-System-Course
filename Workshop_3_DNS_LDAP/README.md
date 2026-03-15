# Workshop 3: DNS and LDAP Implementation

This directory contains the implementation of **Workshop 3: DNS and LDAP** for the Distributed Systems course at **Yachay Tech**.

The project covers two main pillars of service discovery and directory services:
1.  **DNS (Domain Name System):** Programmatic name resolution using `dnspython`.
2.  **LDAP (Lightweight Directory Access Protocol):** Authentication and directory management.

---

## 📋 DNS Implementation

Understanding how name resolution works in practice through various record types.

### Key Features
*   **Basic DNS Queries:** Retrieval of IPv4 addresses (A records).
*   **Reverse Lookups:** Obtaining the domain name associated with a specific IP (PTR records).
*   **Zone Metadata:** Querying advanced records like Mail Exchange (MX), Name Servers (NS), and Start of Authority (SOA).
*   **CNAME Resolution:** Resolving Canonical Names (Aliases) for services.
*   **Custom Resolvers:** Directing queries to specific public DNS servers (e.g., Cloudflare `1.1.1.1`).

---

## 📂 Project Structure

```text
Workshop_3_DNS_LDAP/
│
├── DNS_lookup/                             # Python DNS scripts
│   ├── dns_basic_lookup.py
│   ├── dns_reverse_lookup.py
│   ├── dns_zone_metadata.py
│   ├── dns_cname_alias.py
│   ├── dns_custom_resolver.py
│   └── dns_debug_and_exceptions.py
│
└── LDAP/                                   # LDAP Directory Services
    ├── auth_test.py                        # Authentication logic
    ├── base.ldif                           # Domain hierarchy definitions
    ├── user.ldif                           # User entry definitions
    ├── multiple_publishers.py              # Advanced data population
    └── multiple_subscriber.py              # Directory querying
```

---

## 🚀 Usage Instructions

### DNS
Ensure you have the `dnspython` library:
```bash
pip install dnspython
cd DNS_lookup
python dns_basic_lookup.py
```

### LDAP
Standard `ldif` files are provided for directory structure definition. Python scripts demonstrate programmatic interaction with LDAP servers.
```bash
cd LDAP
python auth_test.py
```

---

## 🧠 Technical Details
*   **DNS Robustness:** Using `dnspython` for detailed inspection of message flags, TTLs, and custom resolvers.
*   **Directory Services:** LDAP provides a structured, hierarchical database optimized for read-heavy authentication and attribute retrieval workloads.

---

## 👤 Author
**Students:** Kevin Sánchez & Jhony Penaherrera
**University:** Yachay Tech
