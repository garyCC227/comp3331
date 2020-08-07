from utility import *
import datetime

def read_from_contact_log():
  content = ''
  with open('z5163479_contactlog.txt', 'r') as f:
    line = f.readline()
    while line != '':
      
      content += line

      line = f.readline()
    
  print(content)
  return content

if __name__ == "__main__":
    read_from_contact_log()