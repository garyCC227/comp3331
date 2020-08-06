# Sample code for Multi-Threaded Server
#Python 3
# Usage: python3 UDPserver3.py
#coding: utf-8
from socket import *
from select import *
import threading
import time,sys
import datetime
from utility import *

#Server will run on this port
server_host = 'localhost'
server_port = int(sys.argv[1])
block_duration = int(sys.argv[2])

#IPv4, TCP
#set up server connection
server_socket = socket(AF_INET, SOCK_STREAM)
server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
server_socket.bind((server_host, server_port))
server_socket.listen()

sockets_list = [server_socket]

blocked_clients = {}

online_clients = {}

print(f'Listening for connections on {server_host}:{server_port}\n')

while(True):

  #incoming socket that we received data
  incoming_sockets, _, _ = select(sockets_list, [], [] ,1)

  for curr_socket in incoming_sockets:

    if curr_socket is server_socket:
      
      # ***Accept a new client connection ***
      client_socket, client_addr = server_socket.accept()
      print("client_socket: {}".format(client_socket.getsockname()))
      print("client_address: {}".format(client_addr))

      #login retry count
      count_retry = 0
      while(True):
        #{'header':header, 'data':data}
        user = receive_message(client_socket=client_socket)

        if user is False:
          break

        credential = user['data'].decode().split(',')
        # print(credential[0]) # username #TODO:DELETE
        # print(credential[1]) # password 

        # *** block duration ***
        #check block clients in blocked list
        for blocked in blocked_clients:
          if blocked_clients[blocked]['data'].decode() == credential[0]:
            username = blocked_clients[blocked]['data'].decode()

            #check block_duration
            curr_time = datetime.datetime.now()
            blocked_time = curr_time - datetime.timedelta(seconds=block_duration)

            if blocked_time > blocked_clients[blocked]['blocked-time'] or blocked_time == blocked_clients[blocked]['blocked-time']:
              #unblock this client
              #TODO: uncomment print
              print('unblock: {}'.format(username))
              if username == credential[0]:
                message = 'Your account have been unblocked. {}, {}!'.format(curr_time.strftime("%d/%m/%Y, %H:%M:%S.%f")[:-3], username).encode()
                message_header = f"{len(message):<{20}}".encode()
                client_socket.send(message_header + message)

                # remove unblocked socket from list of blocked clients
                del blocked_clients[blocked]
                break   
            
            #the account is blocked at the monment
            elif blocked_time < blocked_clients[blocked]['blocked-time']:
              if username == credential[0]:
                message = 'Your account is blocked {}. Please try again after {}s!'.format(username, block_duration).encode()
                message_header = f"{len(message):<{20}}".encode()
                client_socket.send(message_header + message)
                break
        

        # ***check duplicate login
        if check_user_exist_online(username=credential[0], online_clients=online_clients):
          #TODO uncomment print
          print(f'AUTHENTICATION :{credential[0]} is already online. FAILED!')
          message = f'{credential[0]} is already online!'.encode()
          message_header = f"{len(message):<{20}}".encode()
          client_socket.send(message_header + message)
          break

        # ***authentication start***
        result = authenticate(credential=credential)
        print(f'AUTHENTICATION for {credential[0]}: {result}')

        if 'Successful' in result:
          sockets_list.append(client_socket)

          #store online user info
          user['data'] = credential[0].encode()
          user['header'] = f"{len(user['data']):<{20}}".encode()

          #TODO: TempID...
          online_clients[client_socket] = user

          print('Accepted new connection from {}:{} ~> {}'.format(*client_addr, user['data'].decode()))

          #send welcome message
          message = 'Welcome back {}! BlueTrace Simulator '.format(user['data'].decode()).encode()
          message_header = f"{len(message):<{20}}".encode()
          client_socket.send(message_header + message)
          break

        #invalid password
        elif 'Password' in result:
          count_retry +=1
          if count_retry >=3:
            # print('BLOCKED: {}\'s account. Retry count :{}'.format(credentials[0], retry_count))
            
            user['data'] = credential[0].encode()
            user['blocked-time']=datetime.datetime.now()

            #add user to blocked list
            blocked_clients[client_socket] = user

            #response send back to client
            message = 'Invalid Password. Please try again later after {}. {}, Your account has been blocked!'.format(block_duration, credential[0]).encode()
            message_header = f"{len(message):<{20}}".encode()
            client_socket.send(message_header + message)
            
          else:
            result = result + ' retry count: {}'.format(count_retry)
            msg = result.encode()
            msg_header = f"{len(msg):<{20}}".encode()
            client_socket.send(msg_header + msg)
        
        #invalid username
        else:
          msg = result.encode()
          msg_header = f"{len(msg):<{20}}".encode()
          client_socket.send(msg_header + msg)

    #existing socket sending message
    #after authentication successful, server start communicate with client for certain commands
    elif curr_socket in online_clients:
      print("logiined print")
      #get user information
      user = online_clients[curr_socket]

      if user is False:
        continue
      
      #receive message from client
      message = receive_message(curr_socket)
      
      #if message false, mean, client close connection
      if message is False:
        print("I am here")
        print('Closed connection from: {}'.format(online_clients[curr_socket]['data'].decode()))

        #remove socket and client from the GLOBAL variables
        sockets_list.remove(curr_socket)
        del online_clients[curr_socket]
        continue
      
      # *** execute command ***
      command = message["data"].decode().strip().split(' ')[0]
      print("receive command:{}".format(command))

      # *** command: logout***
      if command == 'logout':
        print('Closed connection from: {}'.format(online_clients[curr_socket]['data'].decode()))
        sockets_list.remove(curr_socket)
        del online_clients[curr_socket]

        curr_time = datetime.datetime.now()
        message = 'Logged out successful at {} Bye!'.format(curr_time.strftime("%d/%m/%Y, %H:%M:%S.%f")[:-3]).encode()
        message_header = f"{len(message):<{20}}".encode()
        curr_socket.send(user['header'] + user['data'] + message_header + message)


# #TODO: delete
# t_lock=threading.Condition()
# #will store clients info in this list
# clients=[]
# # would communicate with clients after every second
# UPDATE_INTERVAL= 1
# timeout=False


# def recv_handler():
#     global t_lock
#     global clients
#     global clientSocket
#     global serverSocket
#     print('Server is ready for service')
#     while(1):
        
#         message, clientAddress = serverSocket.recvfrom(2048)
#         #received data from the client, now we know who we are talking with
#         message = message.decode()
#         #get lock as we might me accessing some shared data structures
#         with t_lock:
#             currtime = dt.datetime.now()
#             date_time = currtime.strftime("%d/%m/%Y, %H:%M:%S")
#             print('Received request from', clientAddress[0], 'listening at', clientAddress[1], ':', message, 'at time ', date_time)
#             if(message == 'Subscribe'):
#                 #store client information (IP and Port No) in list
#                 clients.append(clientAddress)
#                 serverMessage="Subscription successfull"
#             elif(message=='Unsubscribe'):
#                 #check if client already subscribed or not
#                 if(clientAddress in clients):
#                     clients.remove(clientAddress)
#                     serverMessage="Subscription removed"
#                 else:
#                     serverMessage="You are not currently subscribed"
#             else:
#                 serverMessage="Unknown command, send Subscribe or Unsubscribe only"
#             #send message to the client
#             serverSocket.sendto(serverMessage.encode(), clientAddress)
#             #notify the thread waiting
#             t_lock.notify()


# def send_handler():
#     global t_lock
#     global clients
#     global clientSocket
#     global serverSocket
#     global timeout
#     #go through the list of the subscribed clients and send them the current time after every 1 second
#     while(1):
#         #get lock
#         with t_lock:
#             for i in clients:
#                 currtime =dt.datetime.now()
#                 date_time = currtime.strftime("%d/%m/%Y, %H:%M:%S")
#                 message='Current time is ' + date_time
#                 clientSocket.sendto(message.encode(), i)
#                 print('Sending time to', i[0], 'listening at', i[1], 'at time ', date_time)
#             #notify other thread
#             t_lock.notify()
#         #sleep for UPDATE_INTERVAL
#         time.sleep(UPDATE_INTERVAL)

# #we will use two sockets, one for sending and one for receiving
# clientSocket = socket(AF_INET, SOCK_DGRAM)
# serverSocket = socket(AF_INET, SOCK_DGRAM)
# serverSocket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
# serverSocket.bind(('localhost', serverPort))

# recv_thread=threading.Thread(name="RecvHandler", target=recv_handler)
# recv_thread.daemon=True
# recv_thread.start()

# send_thread=threading.Thread(name="SendHandler",target=send_handler)
# send_thread.daemon=True
# send_thread.start()
# #this is the main thread
# while True:
#     time.sleep(0.1)

