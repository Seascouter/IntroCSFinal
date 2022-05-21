import socket
import select
import errno
import sys

HEADER_LENGTH = 10
IP = '192.168.7.64'
PORT = 44421

my_username = input('Username: ')
my_password = input('Password: ')

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((IP, PORT))

client_socket.setblocking(False)

login = f"un,{my_username}|pw,{my_password}".encode()
loginHeader = f"{len(login):<{HEADER_LENGTH}}".encode()
client_socket.send(loginHeader+login)


while True:
    message = input(f'{my_username} >  ')

    if message:
        message = message.encode()
        message_header = f"{len(message):<{HEADER_LENGTH}}".encode()
        client_socket.send(message_header + message)
        try:
            while True:
                username_header = client_socket.recv(HEADER_LENGTH)
                if not len(username_header):
                    print("Connection closed by the server")
                    sys.exit()
                username_length = int(username_header.decode().strip())
                username = client_socket.recv(username_length).decode()

                message_header = client_socket.recv(HEADER_LENGTH)
                message_length = int(message_header.decode().strip())
                message = client_socket.recv(message_length).decode()

                print(f'{username} >  {message}')
        except IOError as e:
            if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                print('Reading error: {}'.format(str(e)))
                sys.exit()

            continue
        except Exception as e:
            print('Reading error: {}'.format(str(e)))
            sys.exit()
