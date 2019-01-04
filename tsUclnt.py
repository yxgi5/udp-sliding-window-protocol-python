#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import swp

#TGT_HOST = '127.0.0.1'
#TGT_HOST = '192.168.0.103'
TGT_HOST = '192.168.1.118'
'''
pc:192.168.0.102 ##
pi:192.168.0.103
'''
TGT_PORT = 21567
TGT_ADDR = (TGT_HOST, TGT_PORT)
LC_HOST = ''
LC_PORT = 21568
LC_ADDR = (LC_HOST, LC_PORT)

sendSock = swp.Transmitter(LC_HOST, LC_PORT)
while True:
    send_data = input('> ')
    if not send_data:
        break
    sendSock.send(send_data.encode(), TGT_HOST, TGT_PORT)


sendSock.close()
