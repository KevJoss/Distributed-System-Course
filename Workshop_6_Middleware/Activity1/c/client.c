#include "middleware.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(int argc, char** argv) {
    const char* host = "127.0.0.1";
    int port = 5000;
    unsigned long sid = 1;
    const char* payload = "hello from C client";

    if (argc >= 2) host = argv[1];
    if (argc >= 3) port = atoi(argv[2]);
    if (argc >= 4) sid = strtoul(argv[3], NULL, 10);
    if (argc >= 5) payload = argv[4];

    if (mw_send_message(host, port, (uint32_t)sid, payload) < 0) {
        fprintf(stderr, "Send failed\n");
        return 1;
    }
    printf("[C ] Message sent.\n");
    return 0;
}
