from serial.threaded import *
from serial.tools import list_ports
import multiprocessing as mp
import copy
import time


def to_list(queue: mp.Queue):
    queue_list = [queue.get() for _ in range(queue.qsize()) if queue]
    return queue_list


class SerialServer(mp.Process):
    def __init__(self, port=None, baudrate=9600, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE,
                 stopbits=serial.STOPBITS_ONE, queue: mp.Queue=None):
        mp.Process.__init__(self)
        self.recv_queue = queue
        self.send_queue = mp.Queue()
        self.port = mp.Queue()
        self.port.put(port)
        self.baudrate = baudrate
        self.bytesize = bytesize
        self.parity = parity
        self.stopbits = stopbits
        self._lock = mp.Lock()
        self._running_event = mp.Event()
        self._running_event.clear()
        self._alive = mp.Event()
        self._alive.set()
        self._recording_data = mp.Event()
        self._recording_data.clear()

        try:
            self.serv = serial.Serial(port=self.port.get(), baudrate=self.baudrate, bytesize=self.bytesize,
                                      parity=self.parity, stopbits=self.stopbits)
        except serial.SerialException as ee:
            print(ee)

    def run(self):
        while self._alive.is_set():
            if not self._running_event.is_set():
                try: time.sleep(0.05)
                except:
                    self._alive.clear()
                    self._running_event.clear()
                    self._recording_data.clear()
                    break
            else:
                self._open_serial()
                while self.serv.is_open and self._running_event.is_set() and self._recording_data.is_set():
                    try:
                        self.recv_queue.put(self.serv.readline().decode("ascii"))
                    except:
                        self._running_event.clear()
                        self._recording_data.clear()
                        break
                else: time.sleep(0.05)

    def _open_serial(self):
        with self._lock:
            if not self.serv.is_open:
                s = self.port.get()
                self.serv.port = s
                self.serv.baudrate = self.baudrate
                self.serv.bytesize = self.bytesize
                self.serv.parity = self.parity
                self.serv.stopbits = self.stopbits
                try:
                    self.serv.open()
                except Exception as e:
                    print("Connection error {}".format(e))
                    self._running_event.clear()
                    self._recording_data.clear()

    def send_data(self, line):
        self._open_serial()
        with self._lock:
            if self.serv.is_open:
                try:
                    self.serv.write("{}\n".format(line).encode("ascii"))
                except:
                    self._recording_data.clear()

    def is_server_pending(self):
        return self._running_event.is_set()

    def start_recv(self):
        self._running_event.set()

    def stop_recv(self):
        self._running_event.clear()

    def record_data_start(self):
        self._recording_data.set()

    def record_data_stop(self):
        self._recording_data.clear()

    def is_recording_data(self):
        return self._recording_data.is_set()

    def set_port(self, port: str = None):
        with self._lock:
            while not self.port.empty():
                self.port.get()
            self.port.put(port)

    def join(self, timeout=None):
        self._running_event.clear()
        self._recording_data.clear()
        self._alive.clear()
        mp.Process.join(self, timeout)

    @staticmethod
    def list_ports():
        return list_ports.comports()


if __name__ == "__main__":
    coms = SerialServer.list_ports()
    q = mp.Queue()
    server = SerialServer(port=coms[0].device, baudrate=115200, queue=q)
    i = 0
    # l = [x for x in range(100001)]
    server.start()
    server.start_recv()
    server.record_data_start()
    while True:
        try:
            elem = q.get().rstrip() + " " + str(i)
            # i = l.pop(1)
            i += 1
            print(elem)
            try:
                server.send_data(elem)
            except Exception as e:
                print("END {}".format(e))
                break
        except KeyboardInterrupt:
            print("Interrupt")
            break
    server.stop_recv()
    server.join()
