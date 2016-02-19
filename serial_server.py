from serial.threaded import *
from serial.tools import list_ports
import multiprocessing as mp
import time

def to_list(queue: mp.Queue):
    queue_list = [queue.get() for _ in range(queue.qsize()) if queue]
    return queue_list


class _SerialReadLine(LineReader):
    def connection_made(self, transport):
        super(_SerialReadLine, self).connection_made(transport=transport)
        print("Connection opened")
        self.ENCODING = "ascii"
        self.TERMINATOR = b'\n'

    def add_queue(self, recv_queue: mp.Queue=None):
        self.recv_queue = recv_queue

    def handle_line(self, line):
        # print(line)
        self.recv_queue.put(line)

    def connection_lost(self, exc):
        if exc:
            print(exc)
        print("Connection closed")


class SerialServer(mp.Process):
    def __init__(self, port=None, baudrate=9600, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE,
                 stopbits=serial.STOPBITS_ONE, queue: mp.Queue=None):
        mp.Process.__init__(self)
        self.recv_queue = queue
        self.send_queue = mp.Queue()
        self.port = port
        self.baudrate = baudrate
        self.bytesize = bytesize
        self.parity = parity
        self.stopbits = stopbits
        self.ser = None
        self.serv_manager = None

    def run(self):
        self.ser = serial.Serial(port=self.port, baudrate=self.baudrate, bytesize=self.bytesize,
                                 parity=self.parity, stopbits=self.stopbits)

        with ReaderThread(self.ser, _SerialReadLine) as self.serv_manager:
            self.serv_manager.add_queue(self.recv_queue)
            while True:
                try:
                    send_data = self.send_queue.get()
                    self.serv_manager.write_line(send_data)
                except KeyboardInterrupt: break

    @staticmethod
    def list_ports():
        return list_ports.comports()

    def send_data(self, line):
        self.send_queue.put(line)

if __name__ == "__main__":
    coms = SerialServer.list_ports()
    q = mp.Queue()
    server = SerialServer(port=coms[0].device, baudrate=115200, queue=q)
    i = 0
    l = [x for x in range(100001)]
    server.start()
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
        except KeyboardInterrupt: break

    server.join()
