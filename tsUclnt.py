#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from socket import *

#TGT_HOST = '127.0.0.1'
TGT_HOST = '192.168.0.103'
'''
pc:192.168.0.102 ##
pi:192.168.0.103
'''
TGT_PORT = 21567
BUFSIZ = 1024
TGT_ADDR = (TGT_HOST, TGT_PORT)
LC_HOST = ''
LC_PORT = 21568
LC_ADDR = (LC_HOST, LC_PORT)

udpSock = socket(AF_INET, SOCK_DGRAM)
udpSock.bind(LC_ADDR)
while True:
    send_data = input('> ')
    if not send_data:
        break
    udpSock.sendto(send_data.encode(), TGT_ADDR)
    rcv_data, RCV_ADDR = udpSock.recvfrom(BUFSIZ)
    if not rcv_data:
        break
    print(rcv_data.decode())

udpSock.close()
