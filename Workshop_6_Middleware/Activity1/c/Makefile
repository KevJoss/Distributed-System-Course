CC = gcc
CFLAGS ?= -O2 -Wall -Wextra -std=c11

all: server client

middleware.o: middleware.c middleware.h
	$(CC) $(CFLAGS) -c middleware.c -o middleware.o

server: server.c middleware.o
	$(CC) $(CFLAGS) server.c middleware.o -o server

client: client.c middleware.o
	$(CC) $(CFLAGS) client.c middleware.o -o client

clean:
	rm -f *.o server client
