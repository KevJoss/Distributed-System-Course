CC ?= gcc
CFLAGS ?= -O2 -Wall -Wextra -std=c11

BINARIES := server client registry

all: $(BINARIES)

json_rpc.o: json_rpc.c json_rpc.h
	$(CC) $(CFLAGS) -c json_rpc.c -o json_rpc.o

server: server.c json_rpc.o json_rpc.h
	$(CC) $(CFLAGS) server.c json_rpc.o -o server

client: client.c json_rpc.o json_rpc.h
	$(CC) $(CFLAGS) client.c json_rpc.o -o client

registry: registry.c
	$(CC) $(CFLAGS) registry.c -o registry

clean:
	rm -f *.o $(BINARIES)
