import serial
import dashboard
import time
import json
import redis
import sys

class MagibuxPressures:
    def __init__(self, port):
        self.board = serial.Serial(port, 9600)
        # self.queue = redis.Redis()

        self.sensors = 10

        self.pressure = dashboard.DashboardSlave("pressure")
        self.pressinfo = [0] * self.sensors

        self.lasttime = 0

        """
        self.channels = {
            "press1": "RGN",
            "press0": "RGE"
        }
        """

    def loop(self):
        line = self.board.readline()

        try:
            data = line.decode('utf-8').strip()

        except Exception as e:
            print(e)
            return

        print(data)

        items = data.split(": ")

        if items[0] == "pressure":
            values = items[1].split(" ")

            if len(values) != (self.sensors + 1):
                print("[-] not enough data found")
                return

            if values[self.sensors] != "bar":
                print("[-] malformed or incomplete values line")
                return

            for id, value in enumerate(values):
                if id == self.sensors:
                    # list is complete
                    print(self.pressinfo)

                    if time.time() > self.lasttime + 5:
                        print("[+] pushing new values")

                        self.lasttime = time.time()

                        self.pressure.set(self.pressinfo)
                        self.pressure.publish()

                    return

                self.pressinfo[id] = float(value)

            """ FIXME
            if previous >= now + 0.05 or previous <= now - 0.05:
                self.pressure.set(source, key)
                self.pressure.publish()

                persistance = {
                    "type": "pressure",
                    "source": key,
                    "value": float(value[0])
                }

                # self.queue.publish("persistance", json.dumps(persistance))
            """

    def monitor(self):
        while True:
            self.loop()

if __name__ == "__main__":
    port = "/dev/serial/by-id/usb-Arduino__www.arduino.cc__0042_85735313233351512171-if00"

    if len(sys.argv) > 1:
        port = sys.argv[1]

    print(f"[+] opening serial port: {port}")

    sensors = MagibuxPressures(port)
    sensors.monitor()
