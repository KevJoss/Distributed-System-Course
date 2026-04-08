CC ?= gcc
CFLAGS ?= -O2 -Wall -Wextra -std=c11

all: server client

rpc.o: rpc.c rpc.h
	$(CC) $(CFLAGS) -c rpc.c -o rpc.o

server: server.c rpc.o
	$(CC) $(CFLAGS) server.c rpc.o -o server

client: client.c rpc.o
	$(CC) $(CFLAGS) client.c rpc.o -o client

clean:
	rm -f *.o server client
