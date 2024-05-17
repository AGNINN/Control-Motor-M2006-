
import socket
import struct
import os
 
PF_CAN=29
SOCK_RAW=3
CAN_RAW=1

class CanPort:
    set_voltage=[0,0]
    voltage=[0,0]
    angle0=[0,0]
    angle1=[0,0]
    rotating_speed0=[0,0]
    rotating_speed1=[0,0]
    torque0=[0,0]
    torque1=[0,0]    
    temperature1=0
    frame0=b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    frame1=b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'

    def set_Brate(self):
        staut=os.system("echo root@233 | sudo ip link set can0 down")
        staut=os.system("echo root@233 | sudo ip link set can0 up type can bitrate 1000000")
        return True

    def initCanPort(self):
        try:
            #self.set_Brate() 
            self.fd0=socket.socket(PF_CAN, SOCK_RAW, CAN_RAW) 
            self.fd1=socket.socket(PF_CAN, SOCK_RAW, CAN_RAW) 
            self.fd0.bind(('can0',))
            self.fd1.bind(('can1',))
            return True
        except:
            print("init Error")
    
    def data_merge(self, rx_data):
        try:
            return (rx_data[1]<<8)|rx_data[0] 
        except:
            print("merge Error")

    def data_merge1(self, rx_data):
        try:
            return (rx_data[3]<<24)|(rx_data[2]<<16)|(rx_data[1]<<8)|rx_data[0] 
        except:
            print("merge Error")
    


    def receive(self):
        # try:

        rx_data0=self.fd0.recv(16)
        rx_data1=self.fd1.recv(16)

        # breakpoint()
        #print(rx_data)
        canid0=rx_data0[0:4]
        canid1=rx_data1[0:4]
        
        if rx_data0 and rx_data1 and self.data_merge1(canid0)==0x202 and self.data_merge1(canid1)==0x201:
       
            self.angle0[0]=rx_data0[8]
            self.angle0[1]=rx_data0[9]
            self.angle1[0]=rx_data1[8]
            self.angle1[1]=rx_data1[9]
            self.rotating_speed0[0]=rx_data0[10]
            self.rotating_speed0[1]=rx_data0[11]
            self.rotating_speed1[0]=rx_data1[10]
            self.rotating_speed1[1]=rx_data1[11]
            self.torque0[0]=rx_data0[12]
            self.torque0[1]=rx_data0[13]
            self.torque1[0]=rx_data1[12]
            self.torque1[1]=rx_data1[13]
            self.temperature1=rx_data1[14]
            
            print("M2006: now_angle={}, now_rotating_speed={}, now_torque={}".format(
                self.data_merge(self.angle0),self.data_merge(self.rotating_speed0), self.data_merge(self.torque0)
                ))
            print("M3508: now_angle={}, now_rotating_speed={}, now_torque={}, now_temperature={}".format(
                self.data_merge(self.angle1),self.data_merge(self.rotating_speed1), self.data_merge(self.torque1),self.temperature1
                ))
            return True
        else:
            print("recv Error")
            return False
        
  
        
    def data_split(self,set_num):
        tx_data=[0,0]
        tx_data[0]=set_num>>8 
        tx_data[1]=set_num&0xFF 
        return tx_data


        

    def send(self,set_voltage):
        try:
            self.voltage0=self.data_split(set_voltage[0])
            self.voltage1=self.data_split(set_voltage[1])

            self.can_id=0x200
            self.frame=struct.pack('<IB3x4B4x', self.can_id, len(self.voltage0), self.voltage0[0], self.voltage0[1],self.voltage1[0], self.voltage1[1])
            
            self.fd0.sendall(self.frame)
            self.fd1.sendall(self.frame)
        except Exception as e:
            print(self.frame)
            print("send Error frame\n",e)
            return False

    

if __name__=="__main__":
    canport=CanPort()
    #canport.initCanPort()
    if canport.initCanPort():
            while 1:
                canport.receive()
                canport.set_voltage=[450,100]
                
                canport.send(canport.set_voltage)
               
       
        


