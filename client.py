import socket
ClientMultiSocket = socket.socket() # inicializa o socket do cliente
host = '127.0.0.1'
port = 2004

# Avisa tentativa de conexao e alerta erro da biblioteca caso n efetivada
print('Waiting for connection response')
try:
    ClientMultiSocket.connect((host, port))
except socket.error as e:
    print(str(e))

entrada = ClientMultiSocket.recv(1024).decode() # Recebe confirmacao do server
print(entrada)

# Loop de entrada do cliente para enviar ao server os comandos e ter processamentos
while entrada != "QUIT":
    entrada = input('>> ')
    ClientMultiSocket.send(str.encode(entrada)) # Envia comando ao server
    resposta = ClientMultiSocket.recv(1024).decode() # Recebe processamento do servidor
    print('Response from server:\n' + resposta)

# Processa QUIT (necessario para remover cliente das estruturas)
ClientMultiSocket.send(str.encode(entrada)) # Envia comando QUIT ao server
resposta = ClientMultiSocket.recv(1024).decode() # Recebe resposta
print('Response from server:\n' + resposta)

# Finaliza socket do cliente
ClientMultiSocket.close()