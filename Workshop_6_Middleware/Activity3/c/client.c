#include "json_rpc.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static void usage(const char *prog)
{
    fprintf(stderr,
            "Usage (direct):\n"
            "  %s --host HOST --port PORT --method sum_list --params-json '[10,20,30]'\n"
            "Usage (via registry):\n"
            "  %s --registry-host HOST --registry-port PORT --service-name NAME \\\n"
            "     --method sum_list --params-json '[10,20,30]'\n",
            prog, prog);
}

int main(int argc, char **argv)
{
    const char *host = NULL;
    int port = -1;

    const char *reg_host = NULL;
    int reg_port = 7001;
    const char *svc_name = NULL;

    const char *method = NULL;
    const char *params_json = "[]";

    for (int i = 1; i < argc; i++)
    {
        if (strcmp(argv[i], "--host") == 0 && i + 1 < argc)
            host = argv[++i];
        else if (strcmp(argv[i], "--port") == 0 && i + 1 < argc)
            port = atoi(argv[++i]);
        else if (strcmp(argv[i], "--registry-host") == 0 && i + 1 < argc)
            reg_host = argv[++i];
        else if (strcmp(argv[i], "--registry-port") == 0 && i + 1 < argc)
            reg_port = atoi(argv[++i]);
        else if (strcmp(argv[i], "--service-name") == 0 && i + 1 < argc)
            svc_name = argv[++i];
        else if (strcmp(argv[i], "--method") == 0 && i + 1 < argc)
            method = argv[++i];
        else if (strcmp(argv[i], "--params-json") == 0 && i + 1 < argc)
            params_json = argv[++i];
        else if (strcmp(argv[i], "--help") == 0)
        {
            usage(argv[0]);
            return 0;
        }
    }

    if (!method)
    {
        usage(argv[0]);
        return 1;
    }

    char svc_host[128] = {0};
    int svc_port = -1;

    if (reg_host)
    {
        if (!svc_name)
        {
            usage(argv[0]);
            return 1;
        }
        int rc = registry_lookup(reg_host, reg_port, svc_name, svc_host, sizeof(svc_host), &svc_port);
        if (rc != 0)
        {
            fprintf(stderr, "[C ] registry lookup failed (rc=%d)\n", rc);
            return 2;
        }
        printf("[C ] Resolved %s -> %s:%d\n", svc_name, svc_host, svc_port);
        host = svc_host;
        port = svc_port;
    }

    if (!host || port <= 0)
    {
        fprintf(stderr, "[C ] missing host/port (direct) or registry params\n");
        return 1;
    }

    // Build request JSON (pass params_json through verbatim)
    char req[512];
    snprintf(req, sizeof(req), "{\"method\":\"%s\",\"params\":%s}", method, params_json);

    char resp[1024];
    int rc = rpc_call_json(host, port, req, resp, sizeof(resp));
    if (rc < 0)
    {
        fprintf(stderr, "[C ] transport error\n");
        return 3;
    }

    puts(resp);
    return 0;
}
