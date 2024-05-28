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
i1 = Pin(16, Pin.OUT)
i2 = Pin(17, Pin.OUT)
speed = PWM(Pin(18))
speed.freq(1000)
full = 65000
led1 = Pin(5, Pin.OUT)
led2 = Pin(12, Pin.OUT)
led = Pin("LED", Pin.OUT)
led.on()
def run_motor(pwm_num):
    led2.on()
    #print(round(abs(full*pwm_num*0.01)))
    speed.duty_u16(round(abs(full*pwm_num*0.01)))
    if pwm_num < 0:
        i1.on()
        i2.off()
    elif pwm_num > 0:
        i2.on()
        i1.off()
    elif pwm_num == 0:
        i2.off()
        i1.off()
        led2.off()
def pr1():
        run_motor(100)
def stop():
        i1.off()
        i2.off()
        led2.off()
def pr3():
        k = 0
        run_motor(100)
        time.sleep(0.3)
        for i in range(5):
            k += 20
            run_motor(k)
            time.sleep(0.9)
def pr4():
        run_motor(100)
        time.sleep(0.3)
        stop()
        time.sleep(0.3)
        run_motor(100)
        time.sleep(0.3)
        stop()
        time.sleep(0.3)
        run_motor(100)
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
                if revalue != wert:
                    run_motor(wert)
                revalue = wert 
        conn.close()
def main():
    make_hotspot()
    start_server()

if __name__ == "__main__":
    main()


