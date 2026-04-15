#include "rpc.h"
#include <stdio.h>
#include <stdlib.h>

int main(int argc, char **argv)
{
    int port = 6000;
    if (argc >= 2)
        port = atoi(argv[1]);
    if (rpc_start_server(port) < 0)
    {
        fprintf(stderr, "server failed");
        return 1;
    }
    return 0;
}
