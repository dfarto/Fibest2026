import can
from threading import Thread

bus = can.interface.Bus(
  interface="socketcan", 
  channel="vcan0", 
  bitrate=500000
)

def escucha():
	global bus
	while True:
		resp = bus.recv(1)
			
if __name__ == "__main__":
	resp = bus.recv(1)
	msg = can.Message(arbitration_id=0x711, data=[0x0,0x0,0x0,0x0,0x0,0x0,0x0,0x0], is_extended_id=False)
	bus.send(msg)

	#hilo = Thread(target=escucha())
	#hilo.start()
