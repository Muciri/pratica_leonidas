#!/usr/bin/env python3
import os
import socket

TAM_MSG = 1024         # Tamanho do bloco de mensagem
HOST = '0.0.0.0'       # IP de alguma interface do Servidor
PORT = 40000           # Porta que o Servidor escuta

def processa_msg_cliente(msg, con, cliente):
    msg = msg.decode()
    print('Cliente', cliente, 'enviou', msg)
    msg = msg.split()
    if msg[0].upper() == 'GET':
        nome_arq = " ".join(msg[1:])
        print('Arquivo solicitado:', nome_arq)
        try:
            status_arq = os.stat(nome_arq)
            con.send(str.encode('+OK {}\n'.format(status_arq.st_size)))
            arq = open(nome_arq, "rb")
            while True:
                dados = arq.read(TAM_MSG)
                if not dados: break
                con.send(dados)
        except Exception as e:
            con.send(str.encode('-ERR {}\n'.format(e)))
    elif msg[0].upper() == 'LIST':
        lista_arq = os.listdir('.')
        con.send(str.encode('+OK {}\n'.format(len(lista_arq))))
        for nome_arq in lista_arq:
            if os.path.isfile(nome_arq):
                status_arq = os.stat(nome_arq)
                con.send(str.encode('arq: {} - {:.1f}KB\n'.
                format(nome_arq, status_arq.st_size/1024)))
            elif os.path.isdir(nome_arq):
                con.send(str.encode('dir: {}\n'.format(nome_arq)))
            else:
                con.send(str.encode('esp: {}\n'.format(nome_arq)))
    elif msg[0].upper() == 'QUIT':
        con.send(str.encode('+OK\n'))
        return False
    elif msg[0].upper() == 'CWD':
        try:
            nome_dir = " ".join(msg[1:])
            os.chdir(nome_dir)
            con.send(str.encode('+OK'))
        except Exception as e:
            con.send(str.encode(f'-ERR {e}\n')) 
    else:
        con.send(str.encode('-ERR Invalid command\n'))
    return True

def processa_cliente(con, cliente):
    print('Cliente conectado', cliente)
    while True:
        msg = con.recv(TAM_MSG)
        if not msg or not processa_msg_cliente(msg, con, cliente): break
    con.close()
    print('Cliente desconectado', cliente)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serv = (HOST, PORT)
sock.bind(serv)
sock.listen(50)
while True:
    try:
        con, cliente = sock.accept()
    except: break
    processa_cliente(con, cliente)
sock.close()