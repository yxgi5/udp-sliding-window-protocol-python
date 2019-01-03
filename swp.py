#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import socket
from threading import Thread, Lock
from heapq import heappush, heappop, nsmallest

MAX_FRAME_SIZE= 1034

def ReceiverOpen(lc_host, lc_port):
    '''
        Returns: A Receiver object.
    '''

    ret = Receiver(lc_host, lc_port)
    return ret



def TransmitterOpen(lc_host, lc_port):
    '''
        Returns: A transmitter object and the client address.
    '''
  
    ret = Transmitter(lc_host, lc_port)
    return ret
    
class Receiver:
    '''
        This class represents the receiver of the file sent by the transmitter.
    '''    
    def __init__(self, lc_host, lc_port):
        
        self.lc_addr = (lc_host, lc_port)
        self.udpSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udpSock.bind(self.lc_addr)
    
    def recv(self):
        data, addr=self.udpSock.recvfrom(MAX_FRAME_SIZE)
        return data, addr
        
    def close(self):
        self.udpSock.close()
    
class Transmitter:
    '''
        This class represents the transmitter.
    '''  
    def __init__(self, lc_host, lc_port):
        
        self.lc_addr = (lc_host, lc_port)
        self.udpSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udpSock.bind(self.lc_addr)
        
    def send(self, send_data, tgt_host, tgt_port):
        self.tgt_addr=(tgt_host, tgt_port)
        self.udpSock.sendto(send_data, self.tgt_addr)
        
    def close(self):
        self.udpSock.close()
