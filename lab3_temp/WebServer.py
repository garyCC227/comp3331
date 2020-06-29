#Python 3.7

from socket import *
import sys, os
import re
import mimetypes

def main():
  if(len(sys.argv) < 2):
    print("Error!! Usage: Python WebServer.py port\n")
    return

  port = int(sys.argv[1])

  server_socket = socket(AF_INET, SOCK_STREAM)
  server_socket.bind(('127.0.0.1', port))

  server_socket.listen(1)


  while True:
    connection_socket, addr = server_socket.accept()
    data = connection_socket.recv(1024)


    if data:
      response_line, extra_headers, response_body = handle_request(data)
      connection_socket.send(response_line.encode())
      connection_socket.send(extra_headers.encode())
      connection_socket.send(response_body)

    connection_socket.close()

def handle_request(data):
  data = data.decode()
  lines = data.split('\r\n')
  request = lines[0]

  file = re.search('GET /(.+) HTTP/1.1', request).group(1)
  
  if os.path.exists(file):
    response_line = "HTTP/1.1 {} {}\r\n".format(200,'OK')
    content_type = mimetypes.guess_type(file)[0] or 'text/html'
    extra_headers = "Content-Type: {}\r\n\r\n".format(content_type)

    with open(file, 'rb') as f:
      response_body = f.read()
  else:
    response_line = "HTTP/1.1 {} {}\r\n".format(404,'Not Found')
    extra_headers = "Content-Type: text/html\r\n\r\n"
    response_body = "<h1>404 Not Found</h1>".encode()

  return response_line, extra_headers, response_body

if __name__ == "__main__":
    main()