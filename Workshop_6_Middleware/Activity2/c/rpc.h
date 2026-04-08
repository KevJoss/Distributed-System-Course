#ifndef RPC_H
#define RPC_H

#include <stdint.h>

#define RPC_VERSION 1

#ifdef __cplusplus
extern "C" {
#endif

int rpc_call(const char* host, int port, uint32_t call_id,
             const char* method, const int64_t* params, uint16_t param_count,
             int64_t* out_result, char* errbuf, int errbuf_len);

int rpc_start_server(int port);

#ifdef __cplusplus
}
#endif
#endif
