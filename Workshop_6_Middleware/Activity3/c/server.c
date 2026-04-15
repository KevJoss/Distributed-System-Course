#define _POSIX_C_SOURCE 200112L
#include "json_rpc.h"

#include <arpa/inet.h>
#include <netinet/in.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <unistd.h>

// ---- Extracts the JSON value that follows "params": returns newly malloc'd string ----
static int extract_params_json(const char *req, char **out, size_t *out_len)
{
    const char *p = strstr(req, "\"params\"");
    if (!p)
        return -1;
    p = strchr(p, ':');
    if (!p)
        return -1;
    p++; // after ':'
    while (*p == ' ' || *p == '\t' || *p == '\n' || *p == '\r')
        p++;

    char open = *p, close;
    if (open == '[')
        close = ']';
    else if (open == '{')
        close = '}';
    else
    {
        // primitive (string/number/bool/null)
        if (open == '\"')
        {
            p++;
            const char *q = p;
            while (*q && *q != '\"')
                q++;
            if (!*q)
                return -1;
            const char *start = p - 1; // include the opening quote
            size_t full = (size_t)((q + 1) - start);
            *out = (char *)malloc(full + 1);
            if (!*out)
                return -1;
            memcpy(*out, start, full);
            (*out)[full] = '\0';
            if (out_len)
                *out_len = full;
            return 0;
        }
        else
        {
            const char *start = p, *q = p;
            while (*q && *q != ',' && *q != '}' && *q != ']' && *q != ' ' && *q != '\n' && *q != '\r' && *q != '\t')
                q++;
            if (q == start)
                return -1;
            size_t len = (size_t)(q - start);
            *out = (char *)malloc(len + 1);
            if (!*out)
                return -1;
            memcpy(*out, start, len);
            (*out)[len] = '\0';
            if (out_len)
                *out_len = len;
            return 0;
        }
    }

    // bracket/object matching
    const char *start = p, *q = p;
    int depth = 0;
    while (*q)
    {
        if (*q == open)
            depth++;
        else if (*q == close)
        {
            depth--;
            if (depth == 0)
            {
                size_t len = (size_t)((q + 1) - start);
                *out = (char *)malloc(len + 1);
                if (!*out)
                    return -1;
                memcpy(*out, start, len);
                (*out)[len] = '\0';
                if (out_len)
                    *out_len = len;
                return 0;
            }
        }
        q++;
    }
    return -1;
}

// ---- sum_list helpers (array of ints inside params) ----
static int parse_int_list_sum(const char *json)
{
    const char *p = strstr(json, "\"params\"");
    if (!p)
        return 0;
    p = strchr(p, '[');
    if (!p)
        return 0;
    const char *q = strchr(p, ']');
    if (!q)
        return 0;

    int sum = 0;
    const char *cur = p + 1;
    while (cur < q)
    {
        char *endptr = NULL;
        long v = strtol(cur, &endptr, 10);
        if (endptr == cur)
        {
            cur++;
            continue;
        }
        sum += (int)v;
        cur = endptr;
    }
    return sum;
}

// ---- add helpers: expect params object with fields "a" and "b" ----
static int parse_add_ab(const char *params_obj_json, double *a, double *b)
{
    // very small (non-robust) parser for {"a":X,"b":Y}
    const char *pa = strstr(params_obj_json, "\"a\"");
    const char *pb = strstr(params_obj_json, "\"b\"");
    if (!pa || !pb)
        return -1;

    const char *ca = strchr(pa, ':');
    if (!ca)
        return -1;
    ca++;
    const char *cb = strchr(pb, ':');
    if (!cb)
        return -1;
    cb++;

    // strtod handles ints/floats
    char *endA = NULL, *endB = NULL;
    double va = strtod(ca, &endA);
    double vb = strtod(cb, &endB);
    if (endA == ca || endB == cb)
        return -1;

    *a = va;
    *b = vb;
    return 0;
}

// ---- response builders ----
static void send_response_ok_raw(int cs, const char *raw_json_value)
{
    // Build {"status":"ok","result":<raw>}
    const char *prefix = "{\"status\":\"ok\",\"result\":";
    const char *suffix = "}";
    size_t n = strlen(prefix) + strlen(raw_json_value) + strlen(suffix);
    char *resp = (char *)malloc(n + 1);
    if (!resp)
        return;
    strcpy(resp, prefix);
    strcat(resp, raw_json_value);
    strcat(resp, suffix);

    uint32_t be = htonl((uint32_t)strlen(resp));
    if (send_all(cs, &be, 4) == 0)
        send_all(cs, resp, strlen(resp));
    free(resp);
}
static void send_response_ok_int(int cs, long long result)
{
    char buf[256];
    int n = snprintf(buf, sizeof(buf), "{\"status\":\"ok\",\"result\":%lld}", result);
    uint32_t be = htonl((uint32_t)n);
    send_all(cs, &be, 4);
    send_all(cs, buf, (size_t)n);
}
static void send_response_ok_double(int cs, double result)
{
    char buf[256];
    // prints as JSON number (no quotes)
    int n = snprintf(buf, sizeof(buf), "{\"status\":\"ok\",\"result\":%.17g}", result);
    uint32_t be = htonl((uint32_t)n);
    send_all(cs, &be, 4);
    send_all(cs, buf, (size_t)n);
}
static void send_response_err(int cs, const char *reason)
{
    char buf[256];
    int n = snprintf(buf, sizeof(buf), "{\"status\":\"error\",\"reason\":\"%s\"}", reason);
    uint32_t be = htonl((uint32_t)n);
    send_all(cs, &be, 4);
    send_all(cs, buf, (size_t)n);
}

// ---- per-connection handler ----
static int handle_client(int cs)
{
    uint32_t be_len;
    if (recv_all(cs, &be_len, 4) < 0)
        return -1;
    uint32_t len = ntohl(be_len);
    if (len == 0 || len > (1u << 20))
        return -1;

    char *req = (char *)malloc(len + 1);
    if (!req)
        return -1;
    if (recv_all(cs, req, len) < 0)
    {
        free(req);
        return -1;
    }
    req[len] = '\0';

    // parse method
    const char *m = strstr(req, "\"method\"");
    if (!m)
    {
        send_response_err(cs, "no_method");
        free(req);
        return 0;
    }
    const char *colon = strchr(m, ':');
    const char *v = colon ? colon + 1 : "";
    while (*v == ' ' || *v == '\t')
        v++;
    char method[64] = {0};
    if (*v == '\"')
    {
        v++;
        const char *vend = strchr(v, '\"');
        if (vend && (size_t)(vend - v) < sizeof(method))
            memcpy(method, v, (size_t)(vend - v));
    }

    if (strcmp(method, "sum_list") == 0)
    {
        int sum = parse_int_list_sum(req);
        send_response_ok_int(cs, sum);
    }
    else if (strcmp(method, "echo") == 0)
    {
        char *params = NULL;
        size_t plen = 0;
        if (extract_params_json(req, &params, &plen) == 0 && params)
        {
            send_response_ok_raw(cs, params); // {"status":"ok","result":<params>}
            free(params);
        }
        else
        {
            send_response_err(cs, "bad_params");
        }
    }
    else if (strcmp(method, "add") == 0)
    {
        char *params = NULL;
        size_t plen = 0;
        if (extract_params_json(req, &params, &plen) == 0 && params)
        {
            double a = 0, b = 0;
            if (parse_add_ab(params, &a, &b) == 0)
            {
                double sum = a + b;
                // if it's an integer, return as integer; else as double
                long long as_int = (long long)sum;
                if ((double)as_int == sum)
                    send_response_ok_int(cs, as_int);
                else
                    send_response_ok_double(cs, sum);
            }
            else
            {
                send_response_err(cs, "bad_params_fields");
            }
            free(params);
        }
        else
        {
            send_response_err(cs, "bad_params");
        }
    }
    else
    {
        send_response_err(cs, "unknown_method");
    }

    free(req);
    return 0;
}

int main(int argc, char **argv)
{
    int port = 7000;
    const char *reg_host = NULL;
    int reg_port = 7001;
    const char *svc_name = "calc_service";
    const char *svc_host_for_registry = "127.0.0.1";

    for (int i = 1; i < argc; i++)
    {
        if (strcmp(argv[i], "--port") == 0 && i + 1 < argc)
            port = atoi(argv[++i]);
        else if (strcmp(argv[i], "--registry-host") == 0 && i + 1 < argc)
            reg_host = argv[++i];
        else if (strcmp(argv[i], "--registry-port") == 0 && i + 1 < argc)
            reg_port = atoi(argv[++i]);
        else if (strcmp(argv[i], "--name") == 0 && i + 1 < argc)
            svc_name = argv[++i];
        else if (strcmp(argv[i], "--advertise-host") == 0 && i + 1 < argc)
            svc_host_for_registry = argv[++i];
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

    printf("[S ] listening on 0.0.0.0:%d\n", port);

    if (reg_host)
    {
        int rc = registry_register(reg_host, reg_port, svc_name, svc_host_for_registry, port);
        if (rc == 0)
        {
            printf("[S ] Registered '%s' -> %s:%d at %s:%d\n",
                   svc_name, svc_host_for_registry, port, reg_host, reg_port);
        }
        else
        {
            fprintf(stderr, "[S ] registry register failed (rc=%d)\n", rc);
        }
    }

    while (1)
    {
        struct sockaddr_in cli;
        socklen_t clilen = sizeof(cli);
        int cs = accept(s, (struct sockaddr *)&cli, &clilen);
        if (cs < 0)
        {
            perror("accept");
            continue;
        }
        if (handle_client(cs) < 0)
        { /* ignore */
        }
        close(cs);
    }
    close(s);
    return 0;
}
