#include <stdio.h>
#include <winsock2.h>
#include <string.h>
#include <ctype.h>
#include <windows.h>

DWORD WINAPI HandleClient(LPVOID clientSocketParam) {
    SOCKET clientSocketFD = (SOCKET)clientSocketParam;
    
    char sentence[1024];
    memset(sentence, 0, sizeof(sentence));

    int bytesReceived = recv(clientSocketFD, sentence, sizeof(sentence) - 1, 0);
    
    if (bytesReceived > 0) {
        printf("[Thread %lu] Received: %s\n", GetCurrentThreadId(), sentence);
        Sleep(3000); 

        for(int i = 0; i < strlen(sentence); i++) {
            sentence[i] = toupper(sentence[i]);
        }

        send(clientSocketFD, sentence, strlen(sentence), 0);
    }
    closesocket(clientSocketFD);
    printf("[Thread %lu] Client disconnected.\n", GetCurrentThreadId());
    return 0;
}

int main() {
    WSADATA wsaData;
    if (WSAStartup(MAKEWORD(2,2), &wsaData) != 0) {
        printf("WSAStartup failed\n");
        return 1;
    }

    SOCKET serverSocket = socket(AF_INET, SOCK_STREAM, 0);
    if (serverSocket == INVALID_SOCKET) {
        printf("Socket creation failed\n");
        return 1;
    }

    struct sockaddr_in serverAddr;
    serverAddr.sin_family = AF_INET;
    serverAddr.sin_port = htons(12000);
    serverAddr.sin_addr.s_addr = INADDR_ANY;

    if (bind(serverSocket, (struct sockaddr*)&serverAddr, sizeof(serverAddr)) == SOCKET_ERROR) {
        printf("Bind failed. Port usage error.\n");
        return 1;
    }

    listen(serverSocket, 5);

    struct sockaddr_in clientAddress;
    int clientAddressLen = sizeof(clientAddress);

    while(1) {
        printf("Waiting for new client...\n");
        SOCKET clientSocketFD = accept(serverSocket, (struct sockaddr*)&clientAddress, &clientAddressLen);

        if (clientSocketFD == INVALID_SOCKET) {
            printf("Failed to accept client\n");
            continue;
        }

        char* ipHuman = inet_ntoa(clientAddress.sin_addr);
        int portHuman = ntohs(clientAddress.sin_port);
        printf("Client connected from %s:%d\n", ipHuman, portHuman);

        // CreateThread(Security, StackSize, FunctionToRun, Argument, Flags, ID)
        HANDLE hThread = CreateThread(NULL, 0, HandleClient, (LPVOID)clientSocketFD, 0, NULL);
        
        if (hThread == NULL) {
            printf("Error creating thread\n");
        } else {
            CloseHandle(hThread); 
        }
    }

    closesocket(serverSocket);
    WSACleanup();
    return 0;
}