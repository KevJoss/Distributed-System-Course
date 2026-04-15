#include "rpc.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static void usage(const char *p)
{
    fprintf(stderr, "Usage: %s host port method [args...]", p);
}

int main(int argc, char **argv)
{
    if (argc < 4)
    {
        usage(argv[0]);
        return 1;
    }
    const char *host = argv[1];
    int port = atoi(argv[2]);
    const char *method = argv[3];
    int n = argc - 4;
    if (n < 0)
        n = 0;
    int64_t *params = NULL;
    if (n > 0)
    {
        params = (int64_t *)malloc(sizeof(int64_t) * n);
        for (int i = 0; i < n; ++i)
            params[i] = strtoll(argv[4 + i], NULL, 10);
    }
    int64_t result = 0;
    char err[256];
    int rc = rpc_call(host, port, 1, method, params, (uint16_t)n, &result, err, sizeof(err));
    if (rc == 0)
        printf("[C ] result=%lld", (long long)result);
    else if (rc == 1)
        printf("[C ] error: %s", err);
    else
        printf("[C ] transport error");
    free(params);
    return 0;
}
