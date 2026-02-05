#include <stdio.h>
#include <winsock2.h>
#include <string.h>

int main () {
    WSADATA wsaData;
    if (WSAStartup(MAKEWORD(2,2), &wsaData) != 0) {
        printf("WSAStartup failed\n");
        return 1;
    }

    char option = 'Y';

    do {
        // 1. Create socket (NEW ONE for each request)
        SOCKET socketFD = socket(AF_INET, SOCK_STREAM, 0);
        if (socketFD == INVALID_SOCKET) {
            printf("Failed to create socket\n");
            break;
        }

        struct sockaddr_in address;
        address.sin_family = AF_INET;
        address.sin_port = htons(12000);
        address.sin_addr.s_addr = inet_addr("127.0.0.1");

        printf("\nConnecting to server...\n");
        int result = connect(socketFD, (struct sockaddr*)&address, sizeof(address));

        if (result == 0) {
            printf("Connection successful!\n");
            
            char sentence[100];
            printf("Input lowercase sentence: ");
            
            fflush(stdin); 
            fgets(sentence, sizeof(sentence), stdin);
            
            // Remove newline character
            sentence[strcspn(sentence, "\n")] = 0;

            // Send
            send(socketFD, sentence, strlen(sentence), 0);

            // Receive response
            char response[100];
            memset(response, 0, sizeof(response));
            recv(socketFD, response, sizeof(response) - 1, 0);
            
            printf("Response from Server was: %s\n", response);

        } else {
            printf("Connection failed. Error code: %d\n", WSAGetLastError());
        }

        // Close current socket
        closesocket(socketFD);

        // Ask to continue
        printf("Do you want to send another message? (N to exit): ");
        option = getchar(); 
        getchar();

    } while (option != 'N' && option != 'n');

    printf("Exiting client...\n");
    WSACleanup();

    return 0;
}