#define _POSIX_C_SOURCE 200112L
#include "json_rpc.h"

#include <arpa/inet.h>
#include <errno.h>
#include <netdb.h>
#include <netinet/in.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <unistd.h>

// ---------------- low-level helpers ----------------
int send_all(int s, const void *buf, size_t len)
{
    const char *p = (const char *)buf;
    size_t off = 0;
    while (off < len)
    {
        ssize_t n = send(s, p + off, len - off, 0);
        if (n <= 0)
            return -1;
        off += (size_t)n;
    }
    return 0;
}

int recv_all(int s, void *buf, size_t len)
{
    char *p = (char *)buf;
    size_t off = 0;
    while (off < len)
    {
        ssize_t n = recv(s, p + off, len - off, 0);
        if (n <= 0)
            return -1;
        off += (size_t)n;
    }
    return 0;
}

int tcp_connect(const char *host, int port)
{
    char port_str[16];
    snprintf(port_str, sizeof(port_str), "%d", port);

    struct addrinfo hints, *res = NULL, *rp = NULL;
    memset(&hints, 0, sizeof(hints));
    hints.ai_family = AF_UNSPEC;
    hints.ai_socktype = SOCK_STREAM;

    if (getaddrinfo(host, port_str, &hints, &res) != 0)
        return -1;

    int s = -1;
    for (rp = res; rp; rp = rp->ai_next)
    {
        s = socket(rp->ai_family, rp->ai_socktype, rp->ai_protocol);
        if (s < 0)
            continue;
        if (connect(s, rp->ai_addr, rp->ai_addrlen) == 0)
        {
            break; // success
        }
        close(s);
        s = -1;
    }
    freeaddrinfo(res);
    return s; // -1 on failure
}

// ---------------- framing ----------------
int rpc_call_json(const char *host, int port,
                  const char *json_req,
                  char *json_resp, size_t json_resp_cap)
{
    int s = tcp_connect(host, port);
    if (s < 0)
        return -1;

    uint32_t len = (uint32_t)strlen(json_req);
    uint32_t be_len = htonl(len);

    if (send_all(s, &be_len, 4) < 0)
    {
        close(s);
        return -1;
    }
    if (send_all(s, json_req, len) < 0)
    {
        close(s);
        return -1;
    }

    uint32_t be_rlen = 0;
    if (recv_all(s, &be_rlen, 4) < 0)
    {
        close(s);
        return -1;
    }
    uint32_t rlen = ntohl(be_rlen);

    if (rlen + 1 > json_resp_cap)
    { // prevent overflow; read & truncate
        char *tmp = (char *)malloc(rlen);
        if (!tmp)
        {
            close(s);
            return -1;
        }
        if (recv_all(s, tmp, rlen) < 0)
        {
            free(tmp);
            close(s);
            return -1;
        }
        size_t copy = json_resp_cap ? json_resp_cap - 1 : 0;
        if (copy)
            memcpy(json_resp, tmp, copy);
        if (json_resp_cap)
            json_resp[json_resp_cap - 1] = '\0';
        free(tmp);
        close(s);
        return -1; // signal truncation as transport error
    }
    else
    {
        if (recv_all(s, json_resp, rlen) < 0)
        {
            close(s);
            return -1;
        }
        json_resp[rlen] = '\0';
    }

    close(s);
    return 0;
}

// ---------------- registry client ----------------
static int json_status_ok(const char *resp)
{
    const char *p = strstr(resp, "\"status\"");
    if (!p)
        return 0;
    p = strchr(p, ':');
    if (!p)
        return 0;
    p++;
    while (*p == ' ' || *p == '\t')
        p++;
    if (*p == '\"')
    {
        p++;
        return (strncmp(p, "ok", 2) == 0);
    }
    return 0;
}

int registry_register(const char *reg_host, int reg_port,
                      const char *service_name,
                      const char *service_host, int service_port)
{
    char req[512];
    snprintf(req, sizeof(req),
             "{\"op\":\"register\",\"name\":\"%s\",\"host\":\"%s\",\"port\":%d}",
             service_name, service_host, service_port);

    char resp[512];
    if (rpc_call_json(reg_host, reg_port, req, resp, sizeof(resp)) < 0)
        return -1;
    return json_status_ok(resp) ? 0 : -2;
}

int registry_lookup(const char *reg_host, int reg_port,
                    const char *service_name,
                    char *out_host, size_t out_host_len,
                    int *out_port)
{
    char req[256];
    snprintf(req, sizeof(req),
             "{\"op\":\"lookup\",\"name\":\"%s\"}", service_name);

    char resp[512];
    if (rpc_call_json(reg_host, reg_port, req, resp, sizeof(resp)) < 0)
        return -1;
    if (!json_status_ok(resp))
        return -2;

    // ---- robust host parse (fix) ----
    const char *hpos = strstr(resp, "\"host\"");
    if (!hpos)
        return -3;
    const char *colon = strchr(hpos, ':');
    if (!colon)
        return -3;
    const char *v = colon + 1;
    while (*v == ' ' || *v == '\t')
        v++;
    if (*v == '\"')
    {
        v++;
        const char *vend = strchr(v, '\"');
        if (!vend)
            return -3;
        size_t len = (size_t)(vend - v);
        if (len >= out_host_len)
            len = out_host_len - 1;
        memcpy(out_host, v, len);
        out_host[len] = '\0';
    }
    else
    {
        const char *vend = v;
        while (*vend && *vend != ',' && *vend != '}' && *vend != ' ')
            vend++;
        size_t len = (size_t)(vend - v);
        if (len >= out_host_len)
            len = out_host_len - 1;
        memcpy(out_host, v, len);
        out_host[len] = '\0';
    }

    const char *ppos = strstr(resp, "\"port\"");
    if (!ppos)
        return -3;
    const char *pcolon = strchr(ppos, ':');
    if (!pcolon)
        return -3;
    *out_port = atoi(pcolon + 1);

    return 0;
}
