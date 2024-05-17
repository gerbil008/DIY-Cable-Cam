import bluetooth
import random
import struct
import time
from machine import Pin
from ble_advertising import advertising_payload
from machine import UART
from machine import PWM
from micropython import const

_IRQ_CENTRAL_CONNECT = const(1)
_IRQ_CENTRAL_DISCONNECT = const(2)
_IRQ_GATTS_WRITE = const(3)

_FLAG_READ = const(0x0002)
_FLAG_WRITE_NO_RESPONSE = const(0x0004)
_FLAG_WRITE = const(0x0008)
_FLAG_NOTIFY = const(0x0010)

_UART_UUID = bluetooth.UUID("6E400001-B5A3-F393-E0A9-E50E24DCCA9E")
_UART_TX = (
    bluetooth.UUID("6E400003-B5A3-F393-E0A9-E50E24DCCA9E"),
    _FLAG_READ | _FLAG_NOTIFY,
)
_UART_RX = (
    bluetooth.UUID("6E400002-B5A3-F393-E0A9-E50E24DCCA9E"),
    _FLAG_WRITE | _FLAG_WRITE_NO_RESPONSE,
)
_UART_SERVICE = (
    _UART_UUID,
    (_UART_TX, _UART_RX),
)

uart = UART(0, baudrate=9600, tx=Pin(0), rx=Pin(1))
i1 = Pin(16, Pin.OUT)
i2 = Pin(17, Pin.OUT)
speed = PWM(Pin(18))
speed.freq(1000)
full = 65000
led1 = Pin(5, Pin.OUT)
led2 = Pin(12, Pin.OUT)
led = Pin("LED", Pin.OUT)
led.on()
class BLESimplePeripheral:
    def __init__(self, ble, name="cable_cam"):
        self._ble = ble
        self._ble.active(True)
        self._ble.irq(self._irq)
        ((self._handle_tx, self._handle_rx),) = self._ble.gatts_register_services((_UART_SERVICE,))
        self._connections = set()
        self._write_callback = None
        self._payload = advertising_payload(name=name, services=[_UART_UUID])
        self._advertise()

    def _irq(self, event, data):
        if event == _IRQ_CENTRAL_CONNECT:
            conn_handle, _, _ = data
            print("New connection", conn_handle)
            led1.on()
            self._connections.add(conn_handle)
        elif event == _IRQ_CENTRAL_DISCONNECT:
            conn_handle, _, _ = data
            print("Disconnected", conn_handle)
            i1.off()
            i2.off()
            led1.off()
            self._connections.remove(conn_handle)
            self._advertise()
        elif event == _IRQ_GATTS_WRITE:
            conn_handle, value_handle = data
            value = self._ble.gatts_read(value_handle)
            if value_handle == self._handle_rx and self._write_callback:
                self._write_callback(value)

    def send(self, data):
        for conn_handle in self._connections:
            self._ble.gatts_notify(conn_handle, self._handle_tx, data)

    def is_connected(self):
        return len(self._connections) > 0

    def _advertise(self, interval_us=500000):
        print("Starting advertising")
        self._ble.gap_advertise(interval_us, adv_data=self._payload)

    def on_write(self, callback):
        self._write_callback = callback


def main():
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
    def pr5():
        pass
    def run_motor(pwm_num):
        led2.on()
        print(round(abs(full*pwm_num*0.01)))
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
    ble = bluetooth.BLE()
    p = BLESimplePeripheral(ble)
    def on_rx(v):
        v = v.decode().rstrip("\r\n")
        print(v)
        if v == "prs1":
            pr1()
        elif v == "stop":
            stop()
        elif v == "prs3":
            pr3()
        elif v == "prs4":
            prs4()
        else:
            try:
                run_motor(int(v))
            except ValueError:
                 pass
    p.on_write(on_rx)
    while True:
        if p.is_connected():
            pass
        
if __name__ == "__main__":
    main()

