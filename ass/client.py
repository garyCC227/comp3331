# Python 3
# Usage: python3 UDPClient3.py localhost 12000
#coding: utf-8
from socket import *
from select import *
import sys
import time
from utility import *

# Server would be running on the same host as Client
server_name = sys.argv[1]
server_port = int(sys.argv[2])
udp_port = int(sys.argv[3])

#IPv4 and TCP
client_socket = socket(AF_INET, SOCK_STREAM)
client_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)

client_socket.connect((server_name, server_port))

# Set curr_socket to non-blocking state, so .recv() call won't block, just return some exceptions to handle
client_socket.setblocking(False)

#TODO: p2p

socket_list = [client_socket]

print(f'Connecting to server at {server_name} : {server_port}')
print(f'client_socket to receive from server: {client_socket.getsockname()[0]} : {client_socket.getsockname()[1]}')


# *** Authentication ***
username = input("Username: ").strip()
password = input("Password: ").strip()
credentials = username + ',' + password
print(f'Entered >> username:{username} and pwd: {password}')
credentials = credentials.encode()
user_header = f"{len(credentials):<{20}}".encode()
client_socket.send(user_header + credentials)

command = ''
logged_in = False

command_list = ['Download_tempID','Upload_contact_log', 'logout', 'Beacon']


while(True):
  #if logged in
  if logged_in:
    command = input("{}> ".format(username)).strip()
    if command is not '':
      commands = command.split(' ')

      #check if user enter valid command. from client side
      if commands[0] not in command_list:
        print("Error. Invalid command: {}! try again".format(commands[0]))
        continue
      else:
        #send command
        try:
          message = command.encode()
          message_header = f"{len(message):<{20}}".encode()
          client_socket.send(message_header + message)
          time.sleep(.5)
        except:
          continue
        #TODO: other command


  incoming_sockets, _, _ = select(socket_list, [], [], 1)

  for curr_socket in incoming_sockets:
    if curr_socket is client_socket and not logged_in:
      # *** authentication ***
      while not logged_in:
        msg = receive_message(client_socket = curr_socket)
        
        #something wrong with received message, retry again
        if msg is False:
          continue

        result = msg['data'].decode()
        print(result) #TODO:delete
        if 'Welcome' in result:
          logged_in = True
        elif 'unblock' in result:
          continue
        elif 'already online' in result or 'blocked' in result:
          #TODO:
          client_socket.shutdown(SHUT_RDWR)
          client_socket.close()
          sys.exit(1)
        elif 'Password' in result:
          password = input("Password: ").strip() # .replace(" ", "")
          credentials = username + ',' + password
          print(f'Entered >> username:{username} and pwd: {password}')
          credentials = credentials.encode()
          user_header = f"{len(credentials):<{20}}".encode()
          curr_socket.send(user_header + credentials)
        elif 'Username' in result:
          username = input("Username: ").strip() # .replace(" ", "")
          password = input("Password: ").strip() # .replace(" ", "")
          credentials = username + ',' + password
          print(f'Entered >> username:{username} and pwd: {password}')
          credentials = credentials.encode()
          user_header = f"{len(credentials):<{20}}".encode()
          curr_socket.send(user_header + credentials)
      # **** authentication end ###
    
    #receive message from server after auth
    elif curr_socket is client_socket and logged_in:
      
      while(1):
        msg = receive_messages(client_socket=curr_socket)

        if msg is False:
          continue

        user = str(msg['header'])
        message = msg['data']

        if 'Logged out successful' in message:
          print(message)
          curr_socket.shutdown(SHUT_RDWR)
          curr_socket.close()
          socket_list.remove(curr_socket)
          sys.exit(1)
          



client_socket.close()
# Close the socket
