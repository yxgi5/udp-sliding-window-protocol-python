#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import datetime
import socket
import struct
from threading import Thread, Lock
#from heapq import heappush, heappop, nsmallest

MAX_DATA_SIZE =1024
MAX_FRAME_SIZE= 1034
ACK_SIZE= 6
TIMEOUT = 20

def create_ack(seq_num, error):
    ack = []
    
    if error == True:
        ack.insert(0, 0x00)
    else:
        ack.insert(0, 0x01)
        
    net_seq_num = socket.htonl(seq_num)
    
    ack.insert(1, net_seq_num&0xff)
    ack.insert(2, (net_seq_num>>8)&0xff)
    ack.insert(3, (net_seq_num>>16)&0xff)
    ack.insert(4, (net_seq_num>>24)&0xff)
    
    ack.insert(5, checksum(struct.pack('B'*len(ack), *ack), ACK_SIZE-1))
    
    return struct.pack('B'*len(ack), *ack)

def create_frame(seq_num, frame, data, data_size, eot):
    if eot == True:
        frame.insert(0, 0x00)
    else:
        frame.insert(0, 0x01)
        
    net_seq_num = socket.htonl(seq_num)
    net_data_size = socket.htonl(data_size)
    
    frame.insert(1, net_seq_num&0xff)
    frame.insert(2, (net_seq_num>>8)&0xff)
    frame.insert(3, (net_seq_num>>16)&0xff)
    frame.insert(4, (net_seq_num>>24)&0xff)
    
    frame.insert(5, net_data_size&0xff)
    frame.insert(6, (net_data_size>>8)&0xff)
    frame.insert(7, (net_data_size>>16)&0xff)
    frame.insert(8, (net_data_size>>24)&0xff)
    
    frame[9:9+data_size]=data[0: data_size]
    
    frame.insert(data_size + 9, checksum(frame, data_size+9))
    
    return data_size + 10

def elapsed_time_ms(current_time, start_time):
    k=current_time-start_time
    return k.seconds*1000+round(k.microseconds/1000)
    pass

def checksum(frame, count):
    sum = 0
    frame1=struct.unpack('b'*count,frame[0:count])
    for index in range(count):
        sum = sum+frame1[index]
        if (sum & 0xFFFF0000)!=0:
        #if (sum >0xFFFF):
            sum = sum & 0xFFFF
            sum = sum+1
    return (sum & 0xFF)

def read_ack(ack):
    neg = True if(ack[0]==0x0) else False
    data1=ack[1:5]
    net_seq_num=struct.unpack('I',data1)[0]
    seq_num=socket.ntohl(net_seq_num)
    if(ack[5]==checksum(ack, ACK_SIZE-1)):
        chksum = False
    else:
        chksum = True
        
    return chksum, neg, seq_num

def read_frame(frame):
    if(frame[0]==0x0):
        eot = True
    else:
        eot = False
        
    data1=frame[1:5]
    net_seq_num = struct.unpack('I',data1)[0]
    seq_num = socket.ntohl(net_seq_num)
    
    data1=frame[5:9]
    net_data_size = struct.unpack('I',data1)[0]
    data_size = socket.ntohl(net_data_size)
    
    data = frame[9:9+data_size]
    if(frame[9+data_size]==checksum(frame, 9+data_size)):
        chksum = False
    else:
        chksum = True
    return chksum, seq_num, data, data_size, eot

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
        self.buffer_num = 0
        self.lc_addr = (lc_host, lc_port)
        self.udpSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udpSock.bind(self.lc_addr)
    
    def recv(self, window_len, recv_buffer_size):        
        #self.remote_addr=(remote_host, remote_port)
        self.max_buffer_size = MAX_DATA_SIZE*recv_buffer_size
        self.window_len = window_len

        self.buffer_size = self.max_buffer_size
        self.buffer = bytearray(self.buffer_size)
        self.recv_seq_count = self.max_buffer_size//MAX_DATA_SIZE
        self.window_recv_mask = [False] * self.window_len
        self.lfr = -1 # 一个大buffer中，窗口前一包的下标, 初始化为-1
        self.laf = self.lfr + self.window_len # 窗口末尾包的下标
        
        while(True):
            frame, client_addr = self.udpSock.recvfrom(MAX_FRAME_SIZE)
            #if(client_addr != self.remote_addr):
                #continue
            frame_error, recv_seq_num, data, data_size, eot = read_frame(frame)
            ack = create_ack(recv_seq_num, frame_error)
            #print("%d, %d, %d"%(recv_seq_num,self.lfr,self.laf))
            #self.udpSock.sendto(ack, client_addr)
            tmp=True
            for i in range(window_len):
                if (self.window_recv_mask[i]==False):
                    tmp=False
                    break
                else:
                    tmp=tmp and self.window_recv_mask[i]
            if(tmp==True):
                self.lfr = self.lfr +window_len
                self.laf = self.lfr + window_len
                self.window_recv_mask = [False] * self.window_len
                print('*')
               
            if (recv_seq_num <= self.laf):
                if (frame_error == False):
                    buffer_shift = recv_seq_num * MAX_DATA_SIZE
                    if (recv_seq_num == self.lfr + 1):
                        self.buffer[buffer_shift:buffer_shift+data_size]=data[0:data_size]
                        #print(recv_seq_num,self.lfr,self.laf,self.window_recv_mask)
                        shift = 1
                        for i in range(window_len):
                            if (self.window_recv_mask[i]==False):
                                break
                            shift = shift + 1
                        for i in range(self.window_len-shift):
                            self.window_recv_mask[i] = self.window_recv_mask[i + shift]
                        for i in range(self.window_len-shift, self.window_len):
                            self.window_recv_mask[i] = False
                        self.lfr = self.lfr +shift
                        self.laf = self.lfr + window_len
                    elif(recv_seq_num > self.lfr + 1):
                        if (self.window_recv_mask[recv_seq_num - (self.lfr + 1)] == False):
                            self.buffer[buffer_shift:buffer_shift+data_size]=data[0:data_size]
                            #print(recv_seq_num,self.lfr,self.laf,self.window_recv_mask)
                            self.window_recv_mask[recv_seq_num - (self.lfr + 1)] = True # here
                    if (eot==True):
                        self.buffer_size = buffer_shift + data_size
                        self.recv_seq_count = recv_seq_num + 1
                        pass
                pass
            elif(self.lfr==-1):
                pass
            else:
                print(self.window_recv_mask)
                raise Exception("Recv  err")
            self.udpSock.sendto(ack, client_addr)
            if (self.lfr >= self.recv_seq_count - 1):
                #self.buffer_num=self.buffer_num+1
                #print(self.buffer_num)
                break
        return eot, self.buffer[0:self.buffer_size]
        
    def close(self):
        self.udpSock.close()
    
class Transmitter:
    '''
        This class represents the transmitter.
    '''  
    #def __init__(self):
        
        #self.lc_addr = (lc_host, lc_port)
        #self.udpSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        #self.udpSock.bind(self.lc_addr)
        #self.mutex = Lock()
        #pass

    def __init__(self, lc_host, lc_port, send_data, tgt_host, tgt_port, window_len, read_done):
        self.lc_addr = (lc_host, lc_port)
        self.udpSock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udpSock.bind(self.lc_addr)
        self.mutex = Lock()
        
        # 最后一个buffer?
        self.read_done = read_done

        # 本次发送的数据
        self.buffer=send_data
        self.buffer_size = len(self.buffer)

        #窗口大小
        self.window_len = window_len
        
        # 用于存储窗口包是否收到ACK
        self.window_ack_mask=[False] * window_len
        
        # 用于存储窗口包是否已经发送过
        self.window_sent_mask=[False] * window_len
        
        # 记录发送的时间，用于超时计算
        self.window_sent_time=[datetime.datetime.now()]*window_len
        
        # frame包，包括了eot，包序列号，data
        self.frame = bytearray(MAX_FRAME_SIZE)
        
        # data部分就是要传递的有效数据
        self.data = bytearray(MAX_DATA_SIZE)
        
        # target address
        self.tgt_addr=(tgt_host, tgt_port)
        #self.udpSock.sendto(send_data, self.tgt_addr)
        
        # Creating a thread to keep sending packages.
        #send_thread = Thread(target = self.send_thread, args=(content,))
        send_data_thread = Thread(target = self.send_data_thread)
        
        # Creating another thread to keep receiving the ACKs
        recv_ack_thread = Thread(target = self.recv_ack_thread)
    
        send_data_thread.start()
        recv_ack_thread.start()
        
        send_data_thread.join()
        
        try:
            self.udpSock.shutdown(socket.SHUT_RDWR)
        except OSError as ret:
            #print(ret)
            pass
            
        recv_ack_thread.join()
        self.close()
        
    def send_data_thread(self):
        '''
            Function that keep sending data to the receiver;
            It's executed on a separated thread.
        '''
        self.mutex.acquire()
        
        self.seq_count=int(self.buffer_size//MAX_DATA_SIZE+(0 if (self.buffer_size % MAX_DATA_SIZE) == 0 else 1))
        
        # 用于存储窗口包是否收到ACK
        self.window_ack_mask=[False] * self.window_len
        
        # 用于存储窗口包是否已经发送过
        self.window_sent_mask=[False] * self.window_len
        
        # 一个大buffer中，窗口前一包的下标, 初始化为-1
        self.lar = -1
        
        # 窗口末尾包的下标
        self.lfs = self.lar + self.window_len
            
        self.mutex.release()
            
        self.send_done = False
        while (self.send_done is False):
            self.mutex.acquire()
            
            #如果窗口的第一个包收到了ACK
            if (self.window_ack_mask[0] is True):
                shift = 1 #// 偏移一个包
                
                #找到窗口里第一个没有收到ACK的包
                for i in range(1, self.window_len):
                    if (self.window_ack_mask[i] is False):
                        break
                    shift=shift+ 1 #如果没有找到就继续偏移一个包
                
                #从 第一个没有收到ACK的包 开始，放到窗口的开头开始的位置
                for i in range(self.window_len - shift):
                    self.window_sent_mask[i] = self.window_sent_mask[i + shift]
                    self.window_ack_mask[i] = self.window_ack_mask[i + shift]
                    self.window_sent_time[i] = self.window_sent_time[i + shift]
                    
                # 窗口尾部空出的标志位初始化
                for i in range(self.window_len-shift, self.window_len):
                    self.window_sent_mask[i] = False
                    self.window_ack_mask[i] = False
                self.lar=self.lar+shift
                self.lfs = self.lar + self.window_len
            
            self.mutex.release()
            
            for i in range(self.window_len):
                self.seq_num = self.lar + i + 1
                if (self.seq_num < self.seq_count):
                        self.mutex.acquire()
                        if((self.window_sent_mask[i] is False) or ((self.window_ack_mask[i] is False) and (elapsed_time_ms(datetime.datetime.now(), self.window_sent_time[i])>TIMEOUT))):
                            # 当前包 在buffer中的偏移量
                            buffer_shift = self.seq_num * MAX_DATA_SIZE
                            data_size = (self.buffer_size - buffer_shift) if (self.buffer_size - buffer_shift < MAX_DATA_SIZE) else MAX_DATA_SIZE
                            self.data[0:data_size]=self.buffer[buffer_shift:buffer_shift+data_size]
                            #最后一个buffer的最后一包才置位eot
                            eot = (self.seq_num == (self.seq_count - 1)) and (self.read_done)
                            frame_size = create_frame(self.seq_num, self.frame, self.data, data_size, eot)
                            self.udpSock.sendto(self.frame[0:frame_size], self.tgt_addr)
                            self.window_sent_mask[i] =True
                            self.window_sent_time[i] = datetime.datetime.now()
                        self.mutex.release()
                if (self.lar >= self.seq_count - 1):
                    self.send_done = True
        pass
    
    def recv_ack_thread(self):
        '''
            Function that receives the acks and updates the window's limits.
        '''
        while True:
            try:
                ack, client_addr = self.udpSock.recvfrom(ACK_SIZE)
            #except:
            #    break
            except Exception as ret:
                #print(ret);
                break
            
            if (client_addr != self.tgt_addr):
                break
        
            ack_error, ack_neg, ack_seq_num = read_ack(ack)
            
            self.mutex.acquire()
            if ((ack_error is False) and (ack_seq_num > self.lar) and (ack_seq_num <= self.lfs)):
                if (ack_neg is False):
                    self.window_ack_mask[ack_seq_num - (self.lar + 1)] = True
                else:
                    self.window_sent_time[ack_seq_num - (self.lar + 1)]=datetime.datetime.now()
            self.mutex.release()
            
    def close(self):
        self.udpSock.close()
