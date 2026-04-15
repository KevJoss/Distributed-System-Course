#include "middleware.h"
#include <stdio.h>
#include <stdlib.h>

int main(int argc, char** argv) {
    int port = 5000;
    if (argc >= 2) port = atoi(argv[1]);
    if (mw_start_server(port) < 0) {
        fprintf(stderr, "Server failed\n");
        return 1;
    }
    return 0;
}
