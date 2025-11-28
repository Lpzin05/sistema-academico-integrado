// gravar_dados.c
#include <stdio.h>
#include <stdlib.h>

#ifdef _WIN32
  #include <direct.h> // _mkdir
  #define MKDIR(path) _mkdir(path)
#else
  #include <sys/stat.h> // mkdir
  #include <sys/types.h>
  #define MKDIR(path) mkdir(path, 0755)
#endif

/*
 * Programa simples que recebe 3 argumentos:
 * argv[1] = nome
 * argv[2] = turma
 * argv[3] = nota
 *
 * Garante que a pasta ./data exista e grava em ./data/dados_c.txt
 */

int main(int argc, char *argv[]) {
    if (argc < 4) {
        fprintf(stderr, "Uso: %s <nome> <turma> <nota>\n", argv[0]);
        return 1;
    }

    char *nome = argv[1];
    char *turma = argv[2];
    char *nota = argv[3];

    // tenta abrir o arquivo; se falhar, cria a pasta ./data e tenta de novo
    FILE *arquivo = fopen("./data/dados_c.txt", "a");
    if (arquivo == NULL) {
        // cria pasta data
        if (MKDIR("data") != 0) {
            // se der erro criando a pasta, ainda assim vamos tentar abrir e mostrar erro
            perror("Erro ao criar pasta 'data' (pode já existir)");
        }
        arquivo = fopen("./data/dados_c.txt", "a");
        if (arquivo == NULL) {
            perror("Erro ao abrir './data/dados_c.txt' para escrita");
            return 2;
        }
    }

    if (fprintf(arquivo, "Nome: %s | Turma: %s | Nota: %s\n", nome, turma, nota) < 0) {
        perror("Erro ao escrever no arquivo");
        fclose(arquivo);
        return 3;
    }

    fclose(arquivo);
    printf("Dados gravados com sucesso pelo módulo C!\n");
    return 0;
}
