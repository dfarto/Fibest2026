import can
from time import sleep

request_id = 0x695
response_id = 0x69f

bus = can.interface.Bus(interface="socketcan", channel="vcan0", bitrate=500000)

#step 1: extended session.
msg = can.Message(
                        arbitration_id=request_id,
                        data=[0x02,0x10, 0x03, 0xAA, 0xBB, 0xCC, 0xDD, 0xAA],
                        is_extended_id=False
                    )
bus.send(msg)
sleep(0.1)

#step 2: seed request
msg = can.Message(
                        arbitration_id=request_id,
                        data=[0x02,0x27, 0x01, 0xAA, 0xBB, 0xCC, 0xDD, 0xAA],
                        is_extended_id=False
                    )
bus.send(msg)
while True:
    response = bus.recv(1)
    if response and response.arbitration_id == response_id and list(response.data)[1]==0x67:
        data = list(response.data)[3:]
        break
sleep(0.1)
# Decrypt tries:
#############################

msg = can.Message(
    arbitration_id=request_id,
    data=[0x07,0x27, 0x02] + data,
    is_extended_id=False
)
bus.send(msg)

while True:
    response = bus.recv(1)
    if response and response.arbitration_id == response_id:
        print(response)
        break
