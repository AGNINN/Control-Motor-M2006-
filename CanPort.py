
import socket
import struct
import system
 
PF_CAN=29
SOCK_RAW=3
CAN_RAW=1

class CanPort:
    set_voltage=None
    voltage=None
    angle=None
    rotating_speed=None
    current=None
    temperature=None
    

    def set_Brate(self):
        staut=system("echo root@233 | sudo ip link set can0 down")
        staut=system("echo root@233 | sudo ip link set can0 up type can bitrate 1000000")
        return True

    def initCanPort(self):
        #self.set_Brate() 
        self.fd=socket.socket(PF_CAN, SOCK_RAW, CAN_RAW) 
        self.fd.bind(('can0',))
        return True
    
    def data_merge(self, rx_data):
        return struct.unpack('<H', rx_data)[0] #解析二进制

    def receive(self):
        try:
            rx_bytes=self.fd.recv(8)
            if rx_bytes and rx_bytes[0]==0x200:
                self.angle[0]=rx_bytes[1]
                self.angle[1]=rx_bytes[2]
                self.rotating_speed[0]=rx_bytes[3]
                self.rotating_speed[1]=rx_bytes[4]
                self.current[0]=rx_bytes[5]
                self.current[1]=rx_bytes[6]
                self.temperature=rx_bytes[7]
                print("now_angle={}, now_rotating_speed={}, now_current={}, now_tempreture={}".format(
                    self.data_merge(self.angle), self.data_merge(self.rotating_speed), self.data_merge(self.current), self.temperature 
                    #temp为啥不用解析
                ))
                return True
            else:
                return False
        except:
            return False
        
    def data_split(self, tx_data, set_num):
        tx_data[0]=set_num>>8 
        tx_data[1]=set_num&0xFF 
        return True

    def send(self):
        try:
            self.data_split(self.voltage, self.set_voltage)
            can_id=0x200
            frame=struct.pack('<IB3x2B', can_id, len(self.voltage), self.voltage[0], self.voltage[1])
            self.fd.send(frame)
            return True
        except:
            print("send Error frame\n")
            return False

    

if __name__=="__main__":
    canport=CanPort()
    canport.initCanPort()

    if canport.initCanPort():
            while 1:
                canport.receive()
                canport.set_voltage=150
                canport.send()
       
        


