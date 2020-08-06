import time
import sys
import errno

# helper function for client to format receiving message after auth
def receive_messages(client_socket):
    try:
        time.sleep(0.5)
        # receive "header" containing user length, it's size is defined and constant
        user_header = client_socket.recv(20)

        # if we received no data, server gracefully closed a connection, for example using socket.close() or socket.shutdown(socket.SHUT_RDWR)
        if not len(user_header):
            print('Connection closed by the server')
            sys.exit(1)

        # convert header to int value
        user_length = int(user_header.decode())
        time.sleep(0.5)
        # receive and decode message
        user = client_socket.recv(user_length).decode().split(',')[0]

        # now do the same for message (as we received username, 
        # we received whole message, there's no need to check if it has any length)
        message_header = client_socket.recv(20)
        message_length = int(message_header.decode())
        message = client_socket.recv(message_length).decode()

        # Return a dict object of message header and message data
        return {'header': user, 'data': message}

    # except:
    #     # If we are here, client closed connection violently, for example by pressing ctrl+c on his script
    #     # or just lost his connection
    #     # socket.close() also invokes socket.shutdown(socket.SHUT_RDWR) what sends information about closing the socket (shutdown read/write)
    #     # and that's also a cause when we receive an empty message
    #     return False
    except IOError as e:
        # This is normal on non blocking connections - when there are no incoming data error is going to be raised
        # Some operating systems will indicate that using AGAIN, and some using WOULDBLOCK error code
        # We are going to check for both - if one of them - that's expected, means no incoming data, continue as normal
        # If we got different error code - something happened
        # print("i am here")
        if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
            print('Reading error: {} at notified_socket is client_socket and Logged_in'.format(str(e)))
            sys.exit(1)
        # We just did not receive anything
        return False

    except Exception as e:
        # Any other exception - something happened, exit
        print('Reading error: Message FAIL: {} from server'.format(str(e)))
        sys.exit(1)


def receive_message(client_socket):
    try:
        # Receive header containing message length, it's size is defined as 20
        message_header = client_socket.recv(20)

        # If we received no data, client  closed a connection
        if not len(message_header):
            return False

        # Convert header to int value
        message_length = int(message_header.decode())

        # Return a dict object of message header and message data
        return {'header': message_header, 'data': client_socket.recv(message_length)}

    except:
        # something wrong we cannot receive a correct format message
        return False

# server helper function
# check credentials
def authenticate(credential):
    if len(credential) < 2 or len(credential) > 2:
        return 'Invalid Username. Please try again!'
    credentials = 'credentials.txt'
    with open(credentials, 'r') as f:
        line = f.readline()
        while line != '':  # EOF
            check = line.split()
            # print(check[0]) # username
            # print(check[1]) # password
            if credential == check:
                # login
                return 'Login Successful'
            if credential[0] == check[0] and credential[1] != check[0]:
                return 'Invalid Password. Please try again!'
            line = f.readline()
        return 'Invalid Username. Please try again!'

# if user already logged in


def check_user_exist_online(username, online_clients):
    if username is '' or username is None or len(list(online_clients)) == 0:
        return False
    for sockets in online_clients:
        if username in online_clients[sockets]['data'].decode():
            return True
    return False
