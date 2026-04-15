#ifndef JSON_RPC_H
#define JSON_RPC_H

#include <stddef.h>

// ---------- Transport ----------
int tcp_connect(const char *host, int port);      // returns socket fd or -1
int send_all(int s, const void *buf, size_t len); // 0 on ok, -1 on error
int recv_all(int s, void *buf, size_t len);       // 0 on ok, -1 on error

// JSON-RPC framing: 4-byte big-endian length + payload (UTF-8)
int rpc_call_json(const char *host, int port,
                  const char *json_req,
                  char *json_resp, size_t json_resp_cap);

// ---------- Registry client ----------
int registry_register(const char *reg_host, int reg_port,
                      const char *service_name,
                      const char *service_host, int service_port); // 0 ok

int registry_lookup(const char *reg_host, int reg_port,
                    const char *service_name,
                    char *out_host, size_t out_host_len,
                    int *out_port); // 0 ok, -1 transport, -2 proto, -3 parse

#endif // JSON_RPC_H
