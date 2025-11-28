// cliente.c
// Cliente TCP em C compatível com LAN
// Agora aceita IP do servidor via argumento:
//   cliente.exe <IP_DO_SERVIDOR> <Nome> <Turma> <Nota>
// Se o IP não for informado, usa SERVER_IP_PADRAO

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <winsock2.h>
#include <ws2tcpip.h>
#include <windows.h>

#pragma comment(lib, "Ws2_32.lib")

#define SERVER_IP_PADRAO "127.0.0.1"
#define SERVER_PORT 5050
#define CONNECT_TIMEOUT_MS 3000
#define IO_TIMEOUT_MS 3000

int connect_with_timeout(SOCKET s, const struct sockaddr *addr, int addrlen, int timeout_ms) {
    u_long mode = 1;
    if (ioctlsocket(s, FIONBIO, &mode) != 0)
        return -1;

    int res = connect(s, addr, addrlen);
    if (res == 0) {
        mode = 0;
        ioctlsocket(s, FIONBIO, &mode);
        return 0;
    }

    int last = WSAGetLastError();
    if (last != WSAEWOULDBLOCK && last != WSAEINPROGRESS)
        return -1;

    fd_set writefds;
    FD_ZERO(&writefds);
    FD_SET(s, &writefds);

    struct timeval tv;
    tv.tv_sec = timeout_ms / 1000;
    tv.tv_usec = (timeout_ms % 1000) * 1000;

    res = select(0, NULL, &writefds, NULL, &tv);
    if (res <= 0)
        return -1;

    int so_error = 0;
    int len = sizeof(so_error);
    if (getsockopt(s, SOL_SOCKET, SO_ERROR, (char*)&so_error, &len) == SOCKET_ERROR)
        return -1;

    if (so_error != 0)
        return -1;

    mode = 0;
    ioctlsocket(s, FIONBIO, &mode);
    return 0;
}

int main(int argc, char *argv[]) {
    if (argc < 4) {
        MessageBoxA(NULL,
            "Uso correto:\n\n"
            "cliente.exe <IP_DO_SERVIDOR> <Nome> <Turma> <Nota>\n\n"
            "OU\n"
            "cliente.exe <Nome> <Turma> <Nota>\n(usando IP padrão configurado no código)",
            "Erro na execução",
            MB_ICONERROR);
        return 1;
    }

    // Determina se o 1º argumento é IP ou nome
    char *server_ip;
    char *nome;
    char *turma;
    char *nota;

    if (argc == 5) {
        server_ip = argv[1];
        nome = argv[2];
        turma = argv[3];
        nota = argv[4];
    } else {
        server_ip = SERVER_IP_PADRAO;
        nome = argv[1];
        turma = argv[2];
        nota = argv[3];
    }

    // ---- LOGS ----
    char msg[256];
    sprintf(msg, "Conectando ao servidor %s:%d...", server_ip, SERVER_PORT);
    MessageBoxA(NULL, msg, "Cliente C", MB_OK);

    WSADATA wsa;
    SOCKET s = INVALID_SOCKET;
    struct sockaddr_in server;

    if (WSAStartup(MAKEWORD(2,2), &wsa) != 0) {
        MessageBoxA(NULL, "Falha ao iniciar Winsock.", "Erro", MB_ICONERROR);
        return 1;
    }

    s = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
    if (s == INVALID_SOCKET) {
        MessageBoxA(NULL, "Erro ao criar socket.", "Erro", MB_ICONERROR);
        WSACleanup();
        return 1;
    }

    server.sin_family = AF_INET;
    server.sin_port = htons(SERVER_PORT);
    inet_pton(AF_INET, server_ip, &server.sin_addr);

    if (connect_with_timeout(s, (struct sockaddr*)&server, sizeof(server), CONNECT_TIMEOUT_MS) != 0) {
        MessageBoxA(NULL, "Falha ao conectar (timeout). Servidor inacessível.", "Erro Cliente C", MB_ICONERROR);
        closesocket(s);
        WSACleanup();
        return 1;
    }

    // Define timeouts para envio/recebimento
    DWORD timeout = IO_TIMEOUT_MS;
    setsockopt(s, SOL_SOCKET, SO_RCVTIMEO, (char*)&timeout, sizeof(timeout));
    setsockopt(s, SOL_SOCKET, SO_SNDTIMEO, (char*)&timeout, sizeof(timeout));

    char dados[512];
    snprintf(dados, sizeof(dados), "%s;%s;%s", nome, turma, nota);

    // Envio dos dados
    send(s, dados, strlen(dados), 0);

    // Receber resposta
    char buffer[64];
    int r = recv(s, buffer, sizeof(buffer)-1, 0);
    if (r <= 0) {
        MessageBoxA(NULL, "Nenhuma resposta do servidor.", "Erro Cliente C", MB_ICONERROR);
    } else {
        buffer[r] = '\0';
        MessageBoxA(NULL, buffer, "Resposta do Servidor", MB_OK);
    }

    closesocket(s);
    WSACleanup();
    return 0;
}
