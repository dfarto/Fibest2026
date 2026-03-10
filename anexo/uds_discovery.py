import can
from threading import Thread

if __name__ == "__main__":

    bus = can.interface.Bus(interface="socketcan", channel="vcan0", bitrate=500000)

    id=0x600

    numero_bytes = [0x02]

    mensaje_uds = [0x10,0x03]

    padding = [0xAA,0xAA,0xAA,0xAA,0xAA]

    message = can.Message(arbitration_id=id, 
                          data = numero_bytes + mensaje_uds + padding, 
                          is_extended_id = False
                          )
    
    while True:
        #Envío del mensaje
        bus.send(message)
        
        #Recepción del mensaje
        received = bus.recv(1)
        
        #Desglose del mensaje recibido
        payload = received.data
        lista = list(payload)
        
        #Comprobación de que sea respuesta
        if lista[1] == 0x50:
            
            print("ID DE LA REQUEST DECIMAL:", message.arbitration_id, "ID DE LA REQUEST HEXADECIMAL:", hex(message.arbitration_id))
            
            print("ID DE LA RESPONSE DECIMAL:", received.arbitration_id, "ID DE LA RESPONSE HEXADECIMAL:", hex(received.arbitration_id))
            break
        
        message.arbitration_id += 1
        
