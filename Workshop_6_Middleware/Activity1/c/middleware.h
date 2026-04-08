#ifndef MIDDLEWARE_H
#define MIDDLEWARE_H

#include <stdint.h>

#ifdef __cplusplus
extern "C" {
#endif

#define MW_VERSION 1

// Send a message (binary framed) to host:port with metadata and payload.
int mw_send_message(const char* host, int port, uint32_t source_id, const char* payload);

// Start a blocking server that prints received messages; returns -1 on error (never returns on success).
int mw_start_server(int port);

#ifdef __cplusplus
}
#endif

#endif // MIDDLEWARE_H
