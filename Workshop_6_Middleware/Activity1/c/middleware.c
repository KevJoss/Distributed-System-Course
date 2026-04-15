#define _POSIX_C_SOURCE 200112L
#include "middleware.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <errno.h>
#include <time.h>
#include <arpa/inet.h>
#include <netdb.h>
#include <sys/types.h>
#include <sys/socket.h>
#include <sys/time.h>
#include <netinet/in.h>

// 64-bit ntoh/hton helpers
static uint64_t htonll(uint64_t val) {
#if __BYTE_ORDER__ == __ORDER_LITTLE_ENDIAN__
    return ((uint64_t)htonl((uint32_t)(val & 0xFFFFFFFFULL)) << 32) | htonl((uint32_t)(val >> 32));
#else
    return val;
#endif
}
static uint64_t ntohll(uint64_t val) {
#if __BYTE_ORDER__ == __ORDER_LITTLE_ENDIAN__
    return ((uint64_t)ntohl((uint32_t)(val & 0xFFFFFFFFULL)) << 32) | ntohl((uint32_t)(val >> 32));
#else
    return val;
#endif
}

// Header format (network byte order):
// uint32_t frame_len (len of header+payload following this field)
// uint32_t version
// uint32_t source_id
// uint64_t timestamp_ms
// uint32_t payload_len
// <payload bytes>
struct mw_header {
    uint32_t version;
    uint32_t source_id;
    uint64_t timestamp_ms;
    uint32_t payload_len;
};

static int connect_to_host(const char* host, int port) {
    char portstr[16];
    snprintf(portstr, sizeof(portstr), "%d", port);

    struct addrinfo hints, *res, *p;
    memset(&hints, 0, sizeof(hints));
    hints.ai_family = AF_UNSPEC;
    hints.ai_socktype = SOCK_STREAM;

    int rv = getaddrinfo(host, portstr, &hints, &res);
    if (rv != 0) {
        fprintf(stderr, "getaddrinfo: %s\n", gai_strerror(rv));
        return -1;
    }
    int sock = -1;
    for (p = res; p != NULL; p = p->ai_next) {
        sock = socket(p->ai_family, p->ai_socktype, p->ai_protocol);
        if (sock == -1) continue;
        if (connect(sock, p->ai_addr, p->ai_addrlen) == 0) break;
        close(sock); sock = -1;
    }
    freeaddrinfo(res);
    return sock;
}

static int bind_listen_any(int port) {
    int sock = socket(AF_INET, SOCK_STREAM, 0);
    if (sock < 0) return -1;
    int yes = 1;
    setsockopt(sock, SOL_SOCKET, SO_REUSEADDR, &yes, sizeof(yes));
    struct sockaddr_in addr;
    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = htonl(INADDR_ANY);
    addr.sin_port = htons((uint16_t)port);
    if (bind(sock, (struct sockaddr*)&addr, sizeof(addr)) < 0) {
        close(sock);
        return -1;
    }
    if (listen(sock, 8) < 0) {
        close(sock);
        return -1;
    }
    return sock;
}

static int send_all(int sock, const void* buf, size_t len) {
    const char* p = (const char*)buf;
    size_t total = 0;
    while (total < len) {
        ssize_t n = send(sock, p + total, len - total, 0);
        if (n <= 0) return -1;
        total += (size_t)n;
    }
    return 0;
}

static int recv_all(int sock, void* buf, size_t len) {
    char* p = (char*)buf;
    size_t total = 0;
    while (total < len) {
        ssize_t n = recv(sock, p + total, len - total, 0);
        if (n <= 0) return -1;
        total += (size_t)n;
    }
    return 0;
}

static uint64_t now_ms(void) {
    struct timespec ts;
    clock_gettime(CLOCK_REALTIME, &ts);
    return (uint64_t)ts.tv_sec * 1000ULL + ts.tv_nsec / 1000000ULL;
}

int mw_send_message(const char* host, int port, uint32_t source_id, const char* payload) {
    if (!host || !payload) return -1;
    size_t payload_len = strlen(payload);
    if (payload_len > (50 * 1024 * 1024)) { // 50MB limit
        fprintf(stderr, "payload too large\n");
        return -1;
    }

    int sock = connect_to_host(host, port);
    if (sock < 0) {
        perror("connect_to_host");
        return -1;
    }

    struct mw_header hdr;
    hdr.version = htonl(MW_VERSION);
    hdr.source_id = htonl(source_id);
    hdr.timestamp_ms = htonll(now_ms());
    hdr.payload_len = htonl((uint32_t)payload_len);

    uint32_t frame_len = htonl((uint32_t)(sizeof(hdr) + payload_len)); // length after this field

    // Send frame_len + header + payload
    if (send_all(sock, &frame_len, sizeof(frame_len)) < 0 ||
        send_all(sock, &hdr, sizeof(hdr)) < 0 ||
        send_all(sock, payload, payload_len) < 0) {
        perror("send_all");
        close(sock);
        return -1;
    }
    close(sock);
    return 0;
}

static int handle_client(int csock, struct sockaddr_in* caddr) {
    (void)caddr;
    uint32_t net_frame_len;
    if (recv_all(csock, &net_frame_len, sizeof(net_frame_len)) < 0) return -1;
    uint32_t frame_len = ntohl(net_frame_len);
    if (frame_len < sizeof(struct mw_header) || frame_len > (100 * 1024 * 1024)) {
        fprintf(stderr, "Invalid frame length: %u\n", frame_len);
        return -1;
    }

    struct mw_header hdr;
    if (recv_all(csock, &hdr, sizeof(hdr)) < 0) return -1;

    uint32_t version = ntohl(hdr.version);
    uint32_t source_id = ntohl(hdr.source_id);
    uint64_t timestamp_ms = ntohll(hdr.timestamp_ms);
    uint32_t payload_len = ntohl(hdr.payload_len);

    if (sizeof(hdr) + payload_len != frame_len) {
        fprintf(stderr, "Length mismatch\n");
        return -1;
    }

    char* payload = (char*)malloc(payload_len + 1);
    if (!payload) return -1;
    if (recv_all(csock, payload, payload_len) < 0) {
        free(payload);
        return -1;
    }
    payload[payload_len] = '\0';

    printf("[C ] Received:\n");
    printf("  version: %u\n", version);
    printf("  timestamp_ms: %llu\n", (unsigned long long)timestamp_ms);
    printf("  source_id: %u\n", source_id);
    printf("  payload: %s\n", payload);
    free(payload);
    return 0;
}

int mw_start_server(int port) {
    int lsock = bind_listen_any(port);
    if (lsock < 0) {
        perror("bind_listen_any");
        return -1;
    }
    printf("[C ] Middleware server listening on 0.0.0.0:%d\n", port);
    for (;;) {
        struct sockaddr_in caddr;
        socklen_t clen = sizeof(caddr);
        int csock = accept(lsock, (struct sockaddr*)&caddr, &clen);
        if (csock < 0) {
            perror("accept");
            continue;
        }
        if (handle_client(csock, &caddr) < 0) {
            // best-effort logging; continue accepting
        }
        close(csock);
    }
    close(lsock);
    return 0;
}
