# Internet-Relay-Chat-IRC
Programa de IRC simples implementado para conclusão do Projeto 01 da matéria de Redes de Computadores - Universidade de Brasília (UnB).

O programa consiste em um arquivo cliente, e um arquivo servidor. Ambos possuem métodos que permitem a integração e conexão multithread.

Métodos Implementados:

Básicos:

nick - muda username (único, erro caso contrário)

user - especifica infos user 

quit - finaliza sessao no canal (anuncia para demais participantes)

Servidor:

join - entra no canal

part - sair de canal (tratamento de erros)

list - listar canais no servidor e users de cada canal

Avançados:

privmsg - manda msg para o canal ou user

who - nome do canal e os users
