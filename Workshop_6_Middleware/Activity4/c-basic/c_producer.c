
/* c_producer.c */
#include <amqp.h>
#include <amqp_tcp_socket.h>
#include <amqp_framing.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int main(void) {
  const char *hostname = "localhost";
  int port = 5672;
  const char *exchange = "";
  const char *routingkey = "hello";
  const char *messagebody = "Hello from C!";

  amqp_connection_state_t conn = amqp_new_connection();
  amqp_socket_t *socket = amqp_tcp_socket_new(conn);
  if (!socket) { fprintf(stderr, "Socket error\n"); return 1; }
  if (amqp_socket_open(socket, hostname, port)) { fprintf(stderr, "Open socket error\n"); return 1; }

  amqp_login(conn, "/", 0, 131072, 0, AMQP_SASL_METHOD_PLAIN, "guest", "guest");
  amqp_channel_open(conn, 1);
  amqp_get_rpc_reply(conn);

  amqp_bytes_t message_bytes;
  message_bytes.len = strlen(messagebody);
  message_bytes.bytes = (void*)messagebody;

  amqp_basic_properties_t props;
  props._flags = AMQP_BASIC_DELIVERY_MODE_FLAG;
  props.delivery_mode = 2; // persistent

  amqp_basic_publish(conn, 1, amqp_cstring_bytes(exchange),
                     amqp_cstring_bytes(routingkey), 0, 0,
                     &props, message_bytes);

  amqp_channel_close(conn, 1, AMQP_REPLY_SUCCESS);
  amqp_connection_close(conn, AMQP_REPLY_SUCCESS);
  amqp_destroy_connection(conn);
  printf(" [x] Sent: %s\n", messagebody);
  return 0;
}
