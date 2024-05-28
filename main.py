import network
import usocket as socket
import random
import struct
import time
from machine import UART, Pin, PWM
from micropython import const
import gc
gc.collect()
print(gc.mem_free())
ssid = "Felix_sein_großes_Ding"
password = "sugga_nigga_digg"
file = open("index.html", "r")
html = file.read()
file.close()
print(html)
def stop()
     pass
def hold()
def make_hotspot():
    ap = network.WLAN(network.AP_IF)
    ap.config(essid=ssid, password=password)
    ap.active(True)

    while ap.active() == False:
        pass
    print('AP Mode Is Active, You can Now Connect')
    print('IP Address To Connect to:: ' + ap.ifconfig()[0])

def start_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 80))
    s.listen(1)
    revalue = 0
    while True:
        conn, addr = s.accept()
        request = conn.recv(1024)
        if request:
            conn.sendall('HTTP/1.1 200 OK\n')
            conn.sendall('Content-Type: text/html\n')
            conn.sendall('Connection: close\n\n')
            conn.sendall(html)
            if b"stop" in request:
                stop()
            elif b"full" in request:
                run_motor(100)
            elif b"hold" in request:
                hold()
            elif b'value=' in request:
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
            print(h)          
        conn.close()
def main():
    make_hotspot()
    start_server()

if __name__ == "__main__":
    main()



