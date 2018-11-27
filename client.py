import socket
import time

#inputing the target URL and method of DNS
#tgt_url = input("=>PLease enter the target URL (or [q] to quit): ")
tgt_url = 'test'
#if (tgt_url == 'Q') or (tgt_url == 'q'):
#    exit()

#DNS_mtd = input('=>PLease enter the DNS method (I/R): ')
DNS_mtd = 'I'
#while (DNS_mtd != 'I') and (DNS_mtd != 'R'):
#    DNS_mtd = input("=>Wrong format of DNS method name\n\
#    PLease enter the DNS method (I/R/[q]): ")
#    if (DNS_mtd == 'Q') or (DNS_mtd == 'q'):
#        exit()

#forming message to default DNS server
req_msg = '<'+tgt_url+','+DNS_mtd+'>'
print('=>Sending DNS request: <'+tgt_url+','+DNS_mtd+'>')

#send message to default DNS server
skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
'''--------------------------
    socket.AF_INET ==> ipv4
    socket.AF_INET6 ==> ipv6
--------------------------'''

conn_tuple = ('127.0.0.1', 10053)
'''--------------------------
tuple: (ip_adress, port_num)
real DNS port being 53 in many cases
use higher than 1024 ports to avoid root
--------------------------'''
skt.connect(conn_tuple)
skt.send(req_msg.encode('utf-8'))#expecting a 'byte' but ..??

#waiting and receiving reply from the default DNS server
'''
buffer = []
while True:
    skt_reply = skt.recv(1024)    #setting max receiving byte
    if skt_reply:
        buffer.append(skt_reply)
    else:
        break

receive = ''.join(buffer)
'''
receive = str(skt.recv(1024), encoding="utf-8")
print('=>Receive from DNS server:\n        '+str(receive))


while True:
    msg = input('=>Client now send: ')
    if msg == 'exit':
        skt.close()
        break
    else:
        skt.send(msg.encode('utf-8'))
    receive = str(skt.recv(1024), encoding="utf-8")
    print('=>Receive from DNS server:\n        ' + str(receive))
