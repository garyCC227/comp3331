import sys
import socket
import time

def main():
  # get server host and port
  if(len(sys.argv) < 3):
    print("Error!! Usage: Python PingClient.py host port\n")
    return

  server = sys.argv[1]
  port = int(sys.argv[2])
  # create client socket
  client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
  client_socket.settimeout(0.6)

  #check valid host name
  try:
    (hostname, aliaslist, ipaddrlist) = socket.gethostbyaddr(server)
    # print(hostname, aliaslist, ipaddrlist)
    addr = (ipaddrlist[0], port)
  except socket.gaierror:
    print("Invalid host name")
    return

  #number of message will send
  N = 15
  i = 1
  
  rtt_list = []
  while i <= N:
    # send message to server
    t1 = int(round(time.time() * 1000))
    message = "PING " + str(3331 + i-1) + " "+ str(time.ctime()) + " /r/n"
    client_socket.sendto(message.encode(), addr)

    #try to receive from server
    try:
      modified_mess, server_addr = client_socket.recvfrom(2048)

      #print output
      t2 = int(round(time.time() * 1000))
      t = t2 - t1
      output = "ping to " + addr[0] + ", seq = " + str(i) + ", rtt = " + str(t) + " ms"
      print(output)
      rtt_list.append(t)
    except socket.timeout:
      output = "ping to " + addr[0] + ", seq = " + str(i) + ", timeout"
      print(output)

    i+=1
    #delete this line if need
    time.sleep(1)
  
  client_socket.close()

  #calculate min, max, average rrt
  average_rtt, min_rtt, max_rtt = sum(rtt_list)/len(rtt_list), min(rtt_list), max(rtt_list)
  print("average RTT: {} ms, min RTT: {} ms, max RTT: {} ms".format(average_rtt, min_rtt, max_rtt))


if __name__ == "__main__":
    main()
