#define _POSIX_C_SOURCE 200112L
#include <arpa/inet.h>
#include <errno.h>
#include <netinet/in.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <unistd.h>

static int send_all(int s, const void *buf, size_t len)
{
    const char *p = buf;
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
    char *p = buf;
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

typedef struct Entry
{
    char name[128];
    char host[128];
    int port;
    struct Entry *next;
} Entry;

static Entry *head = NULL;

static Entry *find_entry(const char *name)
{
    for (Entry *e = head; e; e = e->next)
    {
        if (strcmp(e->name, name) == 0)
            return e;
    }
    return NULL;
}
static void upsert_entry(const char *name, const char *host, int port)
{
    Entry *e = find_entry(name);
    if (!e)
    {
        e = (Entry *)calloc(1, sizeof(Entry));
        snprintf(e->name, sizeof(e->name), "%s", name);
        e->next = head;
        head = e;
    }
    snprintf(e->host, sizeof(e->host), "%s", host);
    e->port = port;
}

static int handle_client(int cs)
{
    uint32_t be_len;
    if (recv_all(cs, &be_len, 4) < 0)
        return -1;
    uint32_t len = ntohl(be_len);
    if (len == 0 || len > 4096)
        return -1;

    char *json = (char *)malloc(len + 1);
    if (!json)
        return -1;
    if (recv_all(cs, json, len) < 0)
    {
        free(json);
        return -1;
    }
    json[len] = '\0';

    char op[32] = {0}, name[128] = {0}, host[128] = {0};
    int port = 0;

    // Parse "op"
    char *p = strstr(json, "\"op\"");
    if (p)
    {
        p = strchr(p, ':');
        if (p)
        {
            p++;
            while (*p == ' ' || *p == '\"')
                p++;
            char *q = p;
            while (*q && *q != '\"' && *q != ',' && *q != '}')
                q++;
            size_t n = (size_t)(q - p);
            if (n < sizeof(op))
            {
                memcpy(op, p, n);
                op[n] = 0;
            }
        }
    }
    // Parse "name"
    p = strstr(json, "\"name\"");
    if (p)
    {
        p = strchr(p, ':');
        if (p)
        {
            p++;
            while (*p == ' ' || *p == '\"')
                p++;
            char *q = p;
            while (*q && *q != '\"' && *q != ',' && *q != '}')
                q++;
            size_t n = (size_t)(q - p);
            if (n < sizeof(name))
            {
                memcpy(name, p, n);
                name[n] = 0;
            }
        }
    }
    // Parse "host"
    p = strstr(json, "\"host\"");
    if (p)
    {
        p = strchr(p, ':');
        if (p)
        {
            p++;
            while (*p == ' ' || *p == '\"')
                p++;
            char *q = p;
            while (*q && *q != '\"' && *q != ',' && *q != '}')
                q++;
            size_t n = (size_t)(q - p);
            if (n < sizeof(host))
            {
                memcpy(host, p, n);
                host[n] = 0;
            }
        }
    }
    // Parse "port"
    p = strstr(json, "\"port\"");
    if (p)
    {
        p = strchr(p, ':');
        if (p)
        {
            p++;
            port = atoi(p);
        }
    }

    char resp[512];

    if (strcmp(op, "register") == 0)
    {
        if (name[0] && host[0] && port > 0)
        {
            upsert_entry(name, host, port);
            snprintf(resp, sizeof(resp), "{\"status\":\"ok\"}");
        }
        else
        {
            snprintf(resp, sizeof(resp), "{\"status\":\"error\",\"reason\":\"bad_register\"}");
        }
    }
    else if (strcmp(op, "lookup") == 0)
    {
        Entry *e = find_entry(name);
        if (e)
        {
            snprintf(resp, sizeof(resp), "{\"status\":\"ok\",\"host\":\"%s\",\"port\":%d}", e->host, e->port);
        }
        else
        {
            snprintf(resp, sizeof(resp), "{\"status\":\"error\",\"reason\":\"not_found\"}");
        }
    }
    else
    {
        snprintf(resp, sizeof(resp), "{\"status\":\"error\",\"reason\":\"bad_op\"}");
    }

    uint32_t rlen = (uint32_t)strlen(resp);
    uint32_t rbe = htonl(rlen);
    send_all(cs, &rbe, 4);
    send_all(cs, resp, rlen);

    free(json);
    return 0;
}

int main(int argc, char **argv)
{
    int port = 7001;
    for (int i = 1; i < argc; i++)
    {
        if (strcmp(argv[i], "--port") == 0 && i + 1 < argc)
            port = atoi(argv[++i]);
    }

    int s = socket(AF_INET, SOCK_STREAM, 0);
    if (s < 0)
    {
        perror("socket");
        return 1;
    }
    int yes = 1;
    setsockopt(s, SOL_SOCKET, SO_REUSEADDR, &yes, sizeof(yes));
    struct sockaddr_in addr = {0};
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = htonl(INADDR_ANY);
    addr.sin_port = htons(port);
    if (bind(s, (struct sockaddr *)&addr, sizeof(addr)) < 0)
    {
        perror("bind");
        return 1;
    }
    if (listen(s, 64) < 0)
    {
        perror("listen");
        return 1;
    }

    printf("[registry] listening on 0.0.0.0:%d\n", port);

    while (1)
    {
        struct sockaddr_in cli;
        socklen_t clilen = sizeof(cli);
        int cs = accept(s, (struct sockaddr *)&cli, &clilen);
        if (cs < 0)
        {
            if (errno == EINTR)
                continue;
            perror("accept");
            break;
        }
        handle_client(cs);
        close(cs);
    }

    close(s);
    return 0;
}
