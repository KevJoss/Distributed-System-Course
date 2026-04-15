#define _POSIX_C_SOURCE 200112L
#include "rpc.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <netdb.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <netinet/in.h>

static uint64_t htonll(uint64_t v)
{
#if __BYTE_ORDER__ == __ORDER_LITTLE_ENDIAN__
    return ((uint64_t)htonl((uint32_t)(v & 0xffffffffULL)) << 32) | htonl((uint32_t)(v >> 32));
#else
    return v;
#endif
}
static uint64_t ntohll(uint64_t v)
{
#if __BYTE_ORDER__ == __ORDER_LITTLE_ENDIAN__
    return ((uint64_t)ntohl((uint32_t)(v & 0xffffffffULL)) << 32) | ntohl((uint32_t)(v >> 32));
#else
    return v;
#endif
}

static int send_all(int s, const void *buf, size_t len)
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
static int recv_all(int s, void *buf, size_t len)
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

static int connect_to(const char *host, int port)
{
    char portstr[16];
    snprintf(portstr, sizeof(portstr), "%d", port);
    struct addrinfo hints, *res, *it;
    memset(&hints, 0, sizeof(hints));
    hints.ai_family = AF_UNSPEC;
    hints.ai_socktype = SOCK_STREAM;
    if (getaddrinfo(host, portstr, &hints, &res) != 0)
        return -1;
    int sock = -1;
    for (it = res; it; it = it->ai_next)
    {
        sock = socket(it->ai_family, it->ai_socktype, it->ai_protocol);
        if (sock == -1)
            continue;
        if (connect(sock, it->ai_addr, it->ai_addrlen) == 0)
            break;
        close(sock);
        sock = -1;
    }
    freeaddrinfo(res);
    return sock;
}
static int listen_on(int port)
{
    int s = socket(AF_INET, SOCK_STREAM, 0);
    if (s < 0)
        return -1;
    int yes = 1;
    setsockopt(s, SOL_SOCKET, SO_REUSEADDR, &yes, sizeof(yes));
    struct sockaddr_in a;
    memset(&a, 0, sizeof(a));
    a.sin_family = AF_INET;
    a.sin_addr.s_addr = htonl(INADDR_ANY);
    a.sin_port = htons((uint16_t)port);
    if (bind(s, (struct sockaddr *)&a, sizeof(a)) < 0)
    {
        close(s);
        return -1;
    }
    if (listen(s, 32) < 0)
    {
        close(s);
        return -1;
    }
    return s;
}

static int send_request_frame(int sock, uint32_t call_id, const char *method, const int64_t *params, uint16_t argc)
{
    uint16_t mlen = (uint16_t)strlen(method);
    size_t body_len = 4 + 4 + 2 + 2 + mlen + (size_t)argc * 8;
    uint32_t n_frame_len = htonl((uint32_t)body_len);
    uint32_t n_ver = htonl(RPC_VERSION);
    uint32_t n_cid = htonl(call_id);
    uint16_t n_mlen = htons(mlen);
    uint16_t n_argc = htons(argc);
    if (send_all(sock, &n_frame_len, 4) < 0)
        return -1;
    if (send_all(sock, &n_ver, 4) < 0)
        return -1;
    if (send_all(sock, &n_cid, 4) < 0)
        return -1;
    if (send_all(sock, &n_mlen, 2) < 0)
        return -1;
    if (send_all(sock, &n_argc, 2) < 0)
        return -1;
    if (send_all(sock, method, mlen) < 0)
        return -1;
    for (uint16_t i = 0; i < argc; ++i)
    {
        uint64_t nv = htonll((uint64_t)params[i]);
        if (send_all(sock, &nv, 8) < 0)
            return -1;
    }
    return 0;
}
static int recv_response_frame(int sock, uint32_t *call_id, uint32_t *status, int64_t *result, char *errbuf, int errlen)
{
    uint32_t n_frame_len;
    if (recv_all(sock, &n_frame_len, 4) < 0)
        return -1;
    uint32_t frame_len = ntohl(n_frame_len);
    unsigned char *body = (unsigned char *)malloc(frame_len);
    if (!body)
        return -1;
    if (recv_all(sock, body, frame_len) < 0)
    {
        free(body);
        return -1;
    }
    const unsigned char *p = body;
    uint32_t ver = ntohl(*(uint32_t *)p);
    p += 4;
    (void)ver;
    *call_id = ntohl(*(uint32_t *)p);
    p += 4;
    *status = ntohl(*(uint32_t *)p);
    p += 4;
    uint64_t nv;
    memcpy(&nv, p, 8);
    p += 8;
    *result = (int64_t)ntohll(nv);
    uint16_t elen = ntohs(*(uint16_t *)p);
    p += 2;
    if (*status != 0 && errbuf && errlen > 0)
    {
        int n = (int)((elen < (uint16_t)(errlen - 1)) ? elen : (uint16_t)(errlen - 1));
        memcpy(errbuf, p, n);
        errbuf[n] = '\0';
    }
    else if (errbuf && errlen > 0)
    {
        errbuf[0] = '\0';
    }
    free(body);
    return 0;
}

int rpc_call(const char *host, int port, uint32_t call_id,
             const char *method, const int64_t *params, uint16_t param_count,
             int64_t *out_result, char *errbuf, int errbuf_len)
{
    int sock = connect_to(host, port);
    if (sock < 0)
        return -1;
    if (send_request_frame(sock, call_id, method, params, param_count) < 0)
    {
        close(sock);
        return -1;
    }

    uint32_t cid, status;
    int64_t result;
    if (recv_response_frame(sock, &cid, &status, &result, errbuf, errbuf_len) < 0)
    {
        close(sock);
        return -1;
    }
    close(sock);
    if (status == 0)
    {
        if (out_result)
            *out_result = result;
        return 0;
    }
    return 1;
}

// ---- server side ----
static int handle_client(int csock)
{
    uint32_t nlen;
    if (recv_all(csock, &nlen, 4) < 0)
        return -1;
    uint32_t frame_len = ntohl(nlen);
    unsigned char *body = (unsigned char *)malloc(frame_len);
    if (!body)
        return -1;
    if (recv_all(csock, body, frame_len) < 0)
    {
        free(body);
        return -1;
    }
    const unsigned char *p = body;
    uint32_t ver = ntohl(*(uint32_t *)p);
    p += 4;
    uint32_t call_id = ntohl(*(uint32_t *)p);
    p += 4;
    uint16_t mlen = ntohs(*(uint16_t *)p);
    p += 2;
    uint16_t argc = ntohs(*(uint16_t *)p);
    p += 2;
    char *method = (char *)malloc(mlen + 1);
    memcpy(method, p, mlen);
    method[mlen] = '\0';
    p += mlen;
    int64_t *args = (int64_t *)malloc(sizeof(int64_t) * argc);
    for (uint16_t i = 0; i < argc; ++i)
    {
        uint64_t nv;
        memcpy(&nv, p, 8);
        p += 8;
        args[i] = (int64_t)ntohll(nv);
    }

    int status = 0;
    int64_t result = 0;
    char err[256];
    err[0] = '\0';
    if (ver != RPC_VERSION)
    {
        status = 1;
        snprintf(err, sizeof(err), "version mismatch");
    }
    else if (strcmp(method, "add") == 0)
    {
        if (argc != 2)
        {
            status = 1;
            snprintf(err, sizeof(err), "add expects 2 args");
        }
        else
            result = args[0] + args[1];
    }
    else if (strcmp(method, "multiply") == 0)
    {
        if (argc != 2)
        {
            status = 1;
            snprintf(err, sizeof(err), "multiply expects 2 args");
        }
        else
            result = args[0] * args[1];
    }
    else if (strcmp(method, "fib") == 0)
    {
        if (argc != 1 || args[0] < 0)
        {
            status = 1;
            snprintf(err, sizeof(err), "fib expects n>=0");
        }
        else
        {
            int64_t a = 0, b = 1;
            for (int64_t i = 0; i < args[0]; ++i)
            {
                int64_t t = a + b;
                a = b;
                b = t;
            }
            result = a;
        }
    }
    else if (strcmp(method, "pow") == 0)
    {
        if (argc != 2 || args[1] < 0)
        {
            status = 1;
            snprintf(err, sizeof(err), "pow expects (a,b>=0)");
        }
        else
        {
            int64_t a = args[0], b = args[1], r = 1;
            while (b > 0)
            {
                if (b & 1)
                    r *= a;
                a *= a;
                b >>= 1;
            }
            result = r;
        }
    }
    else
    {
        status = 1;
        snprintf(err, sizeof(err), "unknown method '%s'", method);
    }

    free(args);
    free(method);
    free(body);

    uint32_t nver = htonl(RPC_VERSION), ncall = htonl(call_id), nstatus = htonl((uint32_t)status);
    uint64_t nres = htonll((uint64_t)result);
    uint16_t elen = (uint16_t)strlen(err), nelen = htons(elen);
    uint32_t out_len = htonl(4 + 4 + 4 + 8 + 2 + elen);
    if (send_all(csock, &out_len, 4) < 0)
        return -1;
    if (send_all(csock, &nver, 4) < 0)
        return -1;
    if (send_all(csock, &ncall, 4) < 0)
        return -1;
    if (send_all(csock, &nstatus, 4) < 0)
        return -1;
    if (send_all(csock, &nres, 8) < 0)
        return -1;
    if (send_all(csock, &nelen, 2) < 0)
        return -1;
    if (elen > 0 && send_all(csock, err, elen) < 0)
        return -1;
    return 0;
}

int rpc_start_server(int port)
{
    int lsock = listen_on(port);
    if (lsock < 0)
    {
        perror("listen_on");
        return -1;
    }
    printf("[C ] RPC server listening on 0.0.0.0:%d\n", port);
    for (;;)
    {
        int csock = accept(lsock, NULL, NULL);
        if (csock < 0)
        {
            perror("accept");
            continue;
        }
        (void)handle_client(csock);
        close(csock);
    }
    close(lsock);
    return 0;
}
