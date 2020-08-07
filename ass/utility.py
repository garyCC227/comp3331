import time
import sys
import errno
from random import randint
import datetime

# helper function for client to format receiving message after auth
def receive_messages(client_socket):
    try:
        time.sleep(0.5)
        # receive "header" containing user length, it's size is defined and constant
        user_header = client_socket.recv(20)

        # if we received no data, it might be server close the connection
        if not len(user_header):
            print('Connection closed by the server')
            sys.exit(1)

        # convert header to int value
        user_length = int(user_header.decode())
        time.sleep(0.5)
        # receive and decode message
        user = client_socket.recv(user_length).decode().split(',')[0]

        #Do the same thing to message as user data
        message_header = client_socket.recv(20)
        message_length = int(message_header.decode())
        message = client_socket.recv(message_length).decode()

        # Return a dict object -> {'header':userID, 'data':incoming message}
        return {'header': user, 'data': message}

    except IOError as e:
        if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
            print('Reading error: {} at current_client socket'.format(str(e)))
            sys.exit(1)
        return False

    except Exception as e:
        # Any other exception -> exit
        print('Reading error: {} from server'.format(str(e)))
        sys.exit(1)


def receive_message(client_socket):
    try:
        # Receive header containing message length, size=20
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


#generate 20 byte tempID
def random_with_N_digits(n):
    range_start = 10**(n-1)
    range_end = (10**n)-1
    return randint(range_start, range_end)

#update tempID.txt with the new userID, new tempID, new tempID start time, new tempID_end_time
def write_to_tempIDs(user):
  new_content = ''
  # read the whole tempIDs.txt, and update the line
  with open('tempIDs.txt', 'r') as f:
    line = f.readline()
    while line != '':
      #[0] -userID, [1]-tempID [2]:start time [3]:end-time
      fields = line.split()
      userID = user['data'].decode()
      #update tempIDs
      if fields[0] == userID:
        txt = "{} {} {} {}\n".format(userID, user['tempID'], user['tempID_start_time'], user['tempID_end_time'])
        new_content += txt
      else:
        new_content += line

      line = f.readline()
  
  with open('tempIDs.txt', 'w') as f:
    f.write(new_content)

#reading from contact log, and return its content
def read_from_contact_log():
  content = ''
  with open('z5163479_contactlog.txt', 'r') as f:
    line = f.readline()
    while line != '':
      
      content += line

      line = f.readline()
    
  # print(content)
  return content


#print out the contact log checking
def print_contact_log_checking(log):
  #split this message
  # 12345678901234567891 13/05/2020 17:54:06 13/05/2020 18:09:05
  infos = log.split()
  with open('tempIDs.txt','r') as f:
    #line: +61410777777 12345678901234567892 14/05/2020 17:45:06 14/05/2020 18:00:05
    line = f.readline()
    while line != '':
      fields = line.split()
      if infos[0] == fields[1]:
        print('{}, {} {}, {}'.format(fields[0], infos[1], infos[2], infos[0]))
        break
      
      line = f.readline()

#check if a tempID expiry after 15 mins
def tempID_expired(username, tempID, end_time):
  curr_time = datetime.datetime.now()
  if curr_time >= end_time:
    return True
  return False