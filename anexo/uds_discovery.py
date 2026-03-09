import can
import threading
from time import sleep

bus = can.interface.Bus(interface="socketcan", channel="vcan0", bitrate=500000)

id_res = ""

def capture_response():
    global bus, id_res
    while not id_res:
        msg = bus.recv(timeout=1.0)
        if msg and len(list(msg.data))>3 and [0x50, 0x03] == list(msg.data)[1:3]:
            id_res = msg.arbitration_id
            break

msg = can.Message(
        arbitration_id=0x600,
        data=[0x02,0x10, 0x03, 0xAA, 0xBB, 0xCC, 0xDD, 0xAA],
        is_extended_id=False
    )

basic_msg_thread = threading.Thread(target=capture_response)
basic_msg_thread.start()
while not id_res:
    bus.send(msg)
    sleep(0.1)
    if not id_res:
        msg.arbitration_id += 1
    else: 
        break
    if msg.arbitration_id >= 0x800:
        break

id_res = id_res if id_res else 12
print(f"los ids son -> req: {hex(msg.arbitration_id)}, res: {hex(id_res)}")
