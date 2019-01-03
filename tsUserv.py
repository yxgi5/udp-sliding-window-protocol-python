#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from socket import *
from time import ctime

#TGT_HOST = '127.0.0.1'
TGT_HOST = '192.168.0.102'
'''
pc:192.168.0.102
pi:192.168.0.103 ##
'''
TGT_PORT = 21568
BUFSIZ = 1024
TGT_ADDR = (TGT_HOST, TGT_PORT)
LC_HOST = ''
LC_PORT = 21567
LC_ADDR = (LC_HOST, LC_PORT)

udpSock = socket(AF_INET, SOCK_DGRAM)
udpSock.bind(LC_ADDR)

while True:
    print('waiting for message...')
    data, addr = udpSock.recvfrom(BUFSIZ)
    udpSock.sendto(('[%s] %s' % (ctime(), data.decode())).encode(), TGT_ADDR)
    print(data.decode(), 'received from and returned to:', TGT_ADDR)

udpSock.close()
