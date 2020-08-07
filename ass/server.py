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

# list of variable that support server
# sockets_list: store all the working socket
# blocked_clients: list that stores blocked account
# online_clinets: list that stores all online clients
sockets_list = [server_socket]
blocked_clients = {}
online_clients = {}

print(f'Server has and is listtening the connections on {server_host}:{server_port}\n')

while(True):

  #incoming socket that we received data
  incoming_sockets, _, _ = select(sockets_list, [], [] ,1)

  for curr_socket in incoming_sockets:

    # A new client connection comming
    if curr_socket is server_socket:
      
      # ***Accept a new client connection ***
      client_socket, client_addr = server_socket.accept()
      print("client_socket: {}".format(client_socket.getsockname()))
      print("client_address: {}".format(client_addr))

      #login retry count
      count_retry = 0
      while(True):
        #return the proccessed message ->{'header':header, 'data':data}
        user = receive_message(client_socket=client_socket)

        #something wrong with the receive message, it might be client close the connection
        if user is False:
          break

        credential = user['data'].decode().split(',')
        # print(credential[0])  #[0] is username, [1]:password
        # print(credential[1])

        # *** block duration ***
        #check block clients in blocked list
        for blocked in blocked_clients:
          #compare with username
          if blocked_clients[blocked]['data'].decode() == credential[0]:
            username = blocked_clients[blocked]['data'].decode()

            #check block_duration
            curr_time = datetime.datetime.now()
            blocked_time = curr_time - datetime.timedelta(seconds=block_duration)

            if blocked_time > blocked_clients[blocked]['blocked-time'] or blocked_time == blocked_clients[blocked]['blocked-time']:
              #unblock this client
              #TODO: uncomment print
              # print('unblock: {}'.format(username))
              if username == credential[0]:
                message = 'Your account have been unblocked, time:{}. User: {}!'.format(curr_time.strftime("%d/%m/%Y, %H:%M:%S.%f")[:-3], username).encode()
                message_header = f"{len(message):<{20}}".encode()
                client_socket.send(message_header + message)

                # remove unblocked socket from list of blocked clients
                del blocked_clients[blocked]
                break   
            
            #the account is blocked at the monment
            elif blocked_time < blocked_clients[blocked]['blocked-time']:
              if username == credential[0]:
                message = 'Your account is blocked {}. Try again after {}s!'.format(username, block_duration).encode()
                message_header = f"{len(message):<{20}}".encode()
                client_socket.send(message_header + message)
                break
        

        # ***check duplicate login
        if check_user_exist_online(username=credential[0], online_clients=online_clients):
          message = f'{credential[0]} is already online!'.encode()
          message_header = f"{len(message):<{20}}".encode()
          client_socket.send(message_header + message)
          break

        # ***authentication start***
        result = authenticate(credential=credential)
        print(f'Checking credentials for User ->{credential[0]}: {result}')

        if 'Successful' in result:
          sockets_list.append(client_socket)

          #store online user info
          # we will generate a tempID when a user register
          # store the tempID start_time and expired_time
          user['data'] = credential[0].encode()
          user['header'] = f"{len(user['data']):<{20}}".encode()
          user['tempID'] = random_with_N_digits(20)
          curr_time = datetime.datetime.now()
          user['tempID_start_time'] = curr_time
          user['tempID_end_time'] = curr_time + datetime.timedelta(minutes=15)

          #write into tempIDs.txt
          write_to_tempIDs(user)

          #register a new client_socket into online clients
          online_clients[client_socket] = user

          print('Accepted new connection from {}:{} -> {}'.format(*client_addr, user['data'].decode()))

          #send welcome message to client
          message = 'Welcome back {}! Here is BlueTrace Simulator '.format(user['data'].decode()).encode()
          message_header = f"{len(message):<{20}}".encode()
          client_socket.send(message_header + message)
          break

        #invalid password
        elif 'Password' in result:
          count_retry +=1
          if count_retry >=3:
        
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
        #send back this message: 'Invalid Username. Please try again!'
        else:
          msg = result.encode()
          msg_header = f"{len(msg):<{20}}".encode()
          client_socket.send(msg_header + msg)

    #existing socket sending message
    #after authentication successful, server start communicate with client for certain commands
    elif curr_socket in online_clients:
      #get user information
      user = online_clients[curr_socket]

      # some wrong with coming message. it might be client close the connection
      if user is False:
        continue
      
      #receive message from client
      message = receive_message(curr_socket)
      
      #if message false, mean, client close connection
      if message is False:
        print('Closed connection from: {}'.format(online_clients[curr_socket]['data'].decode()))

        #remove socket and client from the GLOBAL variables
        sockets_list.remove(curr_socket)
        del online_clients[curr_socket]
        continue
      
      # *** execute command ***
      command = message["data"].decode().strip().split(' ')[0]
      whole_message = message["data"].decode()
      print("Receive command:{}".format(command))

      # *** command: logout***
      if command == 'logout':
        print('Closed connection from: {}'.format(online_clients[curr_socket]['data'].decode()))
        sockets_list.remove(curr_socket)
        del online_clients[curr_socket]

        curr_time = datetime.datetime.now()
        message = 'Logged out successful at {} Bye!'.format(curr_time.strftime("%d/%m/%Y, %H:%M:%S.%f")[:-3]).encode()
        message_header = f"{len(message):<{20}}".encode()
        curr_socket.send(user['header'] + user['data'] + message_header + message)
      

      # *** command: Download_tempID ***
      elif command == 'Download_tempID':
        username = user['data']
        tempID = user['tempID']
        end_time = user['tempID_end_time']
        # end_time = datetime.datetime.now() - datetime.timedelta(minutes=15)

        # if tempID expired, generate a new one
        if tempID_expired(username, tempID, end_time):
          user['tempID'] = random_with_N_digits(20)
          curr_time = datetime.datetime.now()
          user['tempID_start_time'] = curr_time
          user['tempID_end_time'] = curr_time + datetime.timedelta(minutes=15)
          tempID = user['tempID']

          #update tempIDs.txt
          write_to_tempIDs(user)

        print('user: {}'.format(username.decode()))
        print('TempID: {}'.format(str(tempID)))

        message = 'TempID: {}'.format(str(tempID)).encode()
        message_header = f"{len(message):<{20}}".encode()
        curr_socket.send(user['header'] + user['data'] + message_header + message)
      
      #*** command: upload_contact_log
      # print the receive contact_log out, and print the contact_log checking result out
      # then send back a succesfully response to client
      elif 'Upload_contact_log' in whole_message:
        message = whole_message.split("::")
        logs = message[1].split('\n')

        username = user['data']
        print('from {}'.format(username.decode()))
        for log in logs:
          print(log)
        
        #contact log checking
        print("\n")
        print("Contact log checking")
        for log in logs:
          print_contact_log_checking(log)

        message = 'Upload contact log successfully'.encode()
        message_header = f"{len(message):<{20}}".encode()
        curr_socket.send(user['header'] + user['data'] + message_header + message)

