import can
import threading
from time import sleep

bus = can.interface.Bus(interface="socketcan", channel="vcan0", bitrate=500000)

id_res = ""

def capture_response():
    global bus, id_res
    bus = can.interface.Bus(interface="socketcan", channel="vcan0", bitrate=500000)
    while not id_res:
        msg = bus.recv(count=1)
        print(msg.data)
        if msg and [0x10, 0x50, 0x01] in msg.data:
            id_res = msg.arbitration_id
            break

msg = can.Message(
                arbitration_id=0x600,
                data=[0x02,0x10, 0x01, 0xAA, 0xBB, 0xCC, 0xDD, 0xAA],
                is_extended_id=False
            )

basic_msg_thread = threading.Thread(target=capture_response)
basic_msg_thread.start()
while not id_res:
    bus.send(msg)
    sleep(0.15)
    if not id_res:
        msg.arbitration_id += 1
    else: 
        break
    if msg.arbitration_id >= 0x800:
        break

print(f"los ids son -> req: {msg.arbitration_id}, res: {id_res}")
