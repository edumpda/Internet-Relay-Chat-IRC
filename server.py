import socket
from _thread import *

# Inicializacao do servidor e algumas variaveis
ServerSideSocket = socket.socket()
host = '127.0.0.1'
port = 2004
ThreadCount = 0
cond_parada = False
cond = True

'''
Estrutura dos dicionarios definidos
----------------------------------------------------------
Estrutura address
dic addresses -> chave address, valor: [nick, conn]
Estrutura cliente
dic clientes -> chave: nick, valor: [realname, host, port]
Estrutura canais
dic canais -> chave: nomecanal, valor: [nicks]
'''

# Inicializacao dos dics colocando alguns canais para teste
addressclientes = {}
clientes = {}
canais = {"CANAL1": [], "CANAL2": [], "CANAL3": []}

# Tenta associar host a porta
try:
    ServerSideSocket.bind((host, port))
except socket.error as e:
    print(str(e))
print('Socket is listening..')
ServerSideSocket.listen(5) # Quantidade de clientes possiveis

def nickClientHandler(address, nickname_novo, dicAddresses, dicClientes, dicCanais):  # NICK
    nickname_velho = dicAddresses[address][0]
    if nickname_novo == nickname_velho:
        return "Nick especificado ja e o seu"
    elif nickname_novo in dicClientes.keys():
        return "Nickname indisponivel"
    else:
        dicAddresses[address][0] = nickname_novo
        for canal in dicCanais.keys():
            if nickname_velho in dicCanais[canal]:
                ind = dicCanais[canal].index(nickname_velho)
                dicCanais[canal][ind] = nickname_novo
        info_nickname = dicClientes[nickname_velho]
        del dicClientes[nickname_velho]
        dicClientes[nickname_novo] = info_nickname
        return "Operacao concluida"


def nameClientHandler(address, name_novo, dicAddresses, dicClientes):  # NAME
    nickname = dicAddresses[address][0]
    dicClientes[nickname][0] = name_novo
    return "Operacao concluida"


def newClientHandler(address, dicAddresses, dicClientes):  # USER
    usuario = dicAddresses[address][0]
    if usuario in dicClientes.keys():
        return f'Nickname: {usuario}\nName: {dicClientes[usuario][0]}\nHost: {dicClientes[usuario][1]}\nPorta: {dicClientes[usuario][2]}'


def quitHandler(address, dicAddresses, dicClientes, dicCanais):  # QUIT
    usuario = dicAddresses[address][0]
    if usuario in dicClientes.keys():
        del dicAddresses[address]
        del dicClientes[usuario]
        for canal in dicCanais.keys():
            if usuario in dicCanais[canal]:
                dicCanais[canal].remove(usuario)
                break
        for user in dicCanais[canal]:
            msg = f'O user {user} saiu do canal {canal}'
            conn = conn_user(user, dicAddresses)
            conn.send(msg.encode())
        return "Desconectando..." # MUDADOOOOO


def subscribeChannelHandler(address, canal, dicAddresses, dicCanais):  # JOIN
    usuario = dicAddresses[address][0]
    if canal not in dicCanais.keys():
        return 'O canal nao existe'
    for channel in dicCanais.keys():
        if usuario in dicCanais[channel]:
            unsubscribeChannelHandler(address, channel, dicAddresses, dicCanais)
    dicCanais[canal].append(usuario)
    return f'{usuario} foi adicionado ao {canal}'


def unsubscribeChannelHandler(address, canal, dicAddresses, dicCanais):  # PART
    usuario = dicAddresses[address][0]
    if canal not in dicCanais.keys():
        return 'O canal nao existe'
    elif usuario not in dicCanais[canal]:
        return 'O cliente nao esta no canal'
    dicCanais[canal].remove(usuario)
    return f'{usuario} foi removido do {canal}'


def listChannelHandler(dicCanais):  # LIST
    retorno = ""
    for canal in dicCanais.keys():
        retorno += f'{canal}:\n'
        cont_client = 1
        if dicCanais[canal] != []:
            for clientes in dicCanais[canal]:
                retorno += f'{cont_client} - {clientes}\n'
                cont_client += 1
        else:
            retorno += 'Canal sem clientes vinculados.\n'
    return retorno


def conn_user(user, dicAddresses):
    for address in dicAddresses.keys():
        if dicAddresses[address][0] == user:
            return dicAddresses[address][1]


def address_conn(conn, dicAddresses):
    for adress in dicAddresses.keys():
        if dicAddresses[adress][1] == conn:
            return adress


def privMsgChannelHandler(address, entrada, msg, dicAddresses, dicClientes, dicCanais):  # PRIVMSG
    user_origem = dicAddresses[address][0]
    if entrada in dicCanais.keys():
        msg = f'Mensagem recebida pelo {user_origem} para o canal {entrada} -> ' + msg
        users_canal = dicCanais[entrada]
        for user in users_canal:
            if user != user_origem:
                conn = conn_user(user, dicAddresses)
                conn.send(msg.encode())
        return f'Mensagem enviada para o canal {entrada}.'
    elif entrada in dicClientes.keys():
        msg = f'Mensagem recebida pelo {user_origem} -> ' + msg
        conn = conn_user(entrada, dicAddresses)
        conn.send(msg.encode())
        return f'Mensagem enviada para o user {entrada}.'
    return "O user ou canal digitado n existe"


def whoChannelHandler(canal, dicCanais):  # WHO
    retorno = ""
    if canal in dicCanais.keys():
        retorno += f'Usuarios do {canal}:\n'
        cont_client = 1
        temalguem = False
        for cliente in dicCanais[canal]:
            temalguem = True
            retorno += f'{cont_client} - {cliente}\n'
            cont_client += 1
        if not temalguem:
            retorno += "Nao ha users nesse canal"
        return retorno
    return "Canal n existente"


def multi_threaded_client(connection):
    connection.send(str.encode("Server funcionando...")) # Avisa ao cliente que conexao foi confirmada
    while True:
        data = connection.recv(2048).decode() # Recebe solicitacao de processamento
        address = address_conn(connection, addressclientes) # Pega address usando a conexao

        # Verifica qual comando foi solicitado
        if data.split()[0] == "NICK":
            data = nickClientHandler(address, data.split()[1], addressclientes, clientes, canais)
        elif data.split()[0] == "NAME":  # Comando pra alterar nome real, n presente no guia
            data = nameClientHandler(address, " ".join(data.split()[1:]), addressclientes, clientes)
        elif data.split()[0] == "USER":
            data = newClientHandler(address, addressclientes, clientes)
        elif data.split()[0] == "QUIT":
            data = quitHandler(address, addressclientes, clientes, canais)
        elif data.split()[0] == "JOIN":
            data = subscribeChannelHandler(address, " ".join(data.split()[1:]), addressclientes, canais)
        elif data.split()[0] == "PART":
            data = unsubscribeChannelHandler(address, " ".join(data.split()[1:]), addressclientes, canais)
        elif data.split()[0] == "LIST":
            data = listChannelHandler(canais)
        elif data.split()[0] == "PRIVMSG":
            data = privMsgChannelHandler(address,
                                                data.split()[1],
                                                " ".join(data.split()[2:]),
                                                addressclientes, clientes, canais)
        elif data.split()[0] == "WHO":
            data = whoChannelHandler(data.split()[1], canais)

        # Demais casos, comando invalido ou tentativa de mensagem
        else:
            if data[0] == "VISUALIZAR":
                continue
            else:
                data = "Comando invalido"

        # Testes para visualizar comando mudando estruturas definidas
        print(addressclientes)
        print(clientes)
        print(canais)

        connection.send(data.encode()) # Envia processamento de volta ao cliente

while True:
    Client, address = ServerSideSocket.accept() # Aceita conexao

    # Inicializa cliente com nicks arbitrarios e os adiciona nos dics
    if cond:
        nome_temp = 0
        cond = False
    addressclientes[address] = [str(nome_temp), Client]
    clientes[str(nome_temp)] = ["realnameinicial", '127.0.0.1', 2004]
    nome_temp += 1

    # Confirmacao de conexao do cliente no server
    print('Connected to: ' + address[0] + ':' + str(address[1]))
    start_new_thread(multi_threaded_client, (Client, ))
    ThreadCount += 1
    print('Thread Number: ' + str(ThreadCount))

# ServerSideSocket.close()



