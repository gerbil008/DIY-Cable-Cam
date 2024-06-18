import network
import usocket as socket
import random
import struct
import time
from machine import UART, Pin, PWM
from micropython import const
import gc
import _thread
gc.collect()
print(gc.mem_free())
ssid = "Among_Sus"
password1 = "passwort123"
file = open("index1.html", "r")
html = file.read()
file.close()
i1 = PWM(Pin(19))
i2 = PWM(Pin(5))
i1.freq(20000)
i2.freq(20000)
pwm_l = Pin(18, Pin.OUT)
pwm_l.on()
pwm_r = Pin(17, Pin.OUT)
pwm_r.on()
full1 = 65069
led1 = Pin(23, Pin.OUT)
led2 = Pin(32, Pin.OUT)
led3 = Pin(22, Pin.OUT)
domains = ["cable.cam", "apple.shit", "windows.noob"]


def ip_to_bytes(ip):
    return bytes(map(int, ip.split('.')))

def dns_response(data, ip):
    transaction_id = data[:2]
    flags = b'\x81\x80'
    questions = data[4:6]
    answer_rrs = b'\x00\x01'
    authority_rrs = b'\x00\x00'
    additional_rrs = b'\x00\x00'
    query = data[12:]
    response = transaction_id + flags + questions + answer_rrs + authority_rrs + additional_rrs + query + b'\xc0\x0c'
    response += b'\x00\x01\x00\x01\x00\x00\x00\x3c\x00\x04'
    response += ip_to_bytes(ip)
    return response

def start_dns_server():
    dns_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    dns_socket.bind(('', 53))

    while True:
        try:
            data, addr = dns_socket.recvfrom(512)
            domain = b''
            state = 0
            length = 0
            for byte in data[12:]:
                if state == 1:
                    domain += bytes([byte])
                    length -= 1
                    if length == 0:
                        state = 2
                elif state == 2:
                    if byte == 0:
                        break
                    domain += b'.'
                    length = byte
                    state = 1
                else:
                    length = byte
                    state = 1

            domain = domain.decode('utf-8')
            if domain in domains:
                dns_socket.sendto(dns_response(data, ap.ifconfig()[0] ), addr)
        except:
            print("DNS Error")

def run_motor(pwm_num):
    led2.on()
    print(round(abs(full1*pwm_num*0.01)))
    print(pwm_num)
    if pwm_num < 0:
        i1.duty_u16(round(abs(full1*pwm_num*0.01)))
    elif pwm_num > 0:
        i2.duty_u16(round(abs(full1*pwm_num*0.01)))
    elif pwm_num == 0:
        i1.duty_u16(0)
        i2.duty_u16(0)
        led2.off()
def make_hotspot():
    global ap
    ap = network.WLAN(network.AP_IF)
    ap.config(essid=ssid, password=password1, authmode=network.AUTH_WPA_WPA2_PSK)
    ap.active(True)
    while ap.active() == False:
        pass
    print(ap.ifconfig()[0])
def start_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 80))
    s.listen(1)
    while True:
        conn, addr = s.accept()
        request = conn.recv(1024)
        if request:
            conn.sendall('HTTP/1.1 200 OK\n')
            conn.sendall('Content-Type: text/html\n')
            conn.sendall('Connection: close\n\n')
            conn.sendall(html)
            if b'value=' in request:
                index = request.find(b'value=')
                wert = request[index+6:index+9].decode()
                h = ""
                for stabe in wert:
                    if stabe != "-":
                        try:
                            int(stabe)
                            h += stabe
                        except:
                            pass
                    else:
                        h += "-"
                try:        
                    run_motor(int(h))
                    led3.off()
                except:
                    led3.on()
        conn.close()
def main():
    make_hotspot()
    _thread.start_new_thread(start_dns_server, ())
    start_server()

if __name__ == "__main__":
    main()




