import random
import can
import threading
from time import sleep

class VirtualECU:
    def __init__(self, request_id, response_id):
        """
        Inicializa una ECU virtual.
        """
        self.request_id = request_id
        self.response_id = response_id
        self.bus = can.interface.Bus(interface="socketcan", channel="vcan0", bitrate=500000)
        self.running = False
        self.thread = None
        self.sesion = "Default"
        self.sec_access = ""
        self.iter = 0
        self.basic_msg = can.Message(
                        arbitration_id=random.randint(0x001, 0x600),
                        data= [0x41, 0x4c, 0x49, 0x56, 0x45, 0x00, 0x00, 0x00],
                        is_extended_id=False
                    )
        self.basic_msg_thread = None

    def start(self):
        """
        Inicia la ECU virtual para escuchar mensajes y responder.
        """
        self.running = True
        self.thread = threading.Thread(target=self.listen_and_respond)
        self.thread.daemon = True
        self.thread.start()
        self.basic_msg_thread = threading.Thread(target=self.send_basic_msg)
        self.basic_msg_thread.start()

    def stop(self):
        """
        Detiene la ECU virtual.
        """
        self.running = False
        if self.thread is not None:
            self.bus.shutdown()
            self.thread.join()

    def send_basic_msg(self):
        """
        Envia el mensaje genérico.
        """
        while self.running:
            self.iter = (self.iter + 1)%255
            self.bus.send(self.basic_msg)
            self.basic_msg.data[7] = self.iter
            sleep(0.1)

    def listen_and_respond(self):
        """
        Escucha los mensajes y responde si detecta un mensaje con 1003.
        """
        while self.running:
            message = self.bus.recv(1)  # Timeout de 1 segundo
            
            if message and message.arbitration_id == self.request_id:
                if bytes([0x02,0x10,0x01]) in message.data:
                    response = can.Message(
                        arbitration_id=self.response_id,
                        data=[0x06,0x50, 0x01, 0xAA, 0xBB, 0xCC, 0xDD, 0xAA],
                        is_extended_id=False
                    )
                    self.bus.send(response)
                
                if bytes([0x02,0x10,0x02]) in message.data:
                    response = can.Message(
                        arbitration_id=self.response_id,
                        data=[0x06,0x50, 0x02, 0xAA, 0xBB, 0xCC, 0xDD, 0xAA],  # Positive Response to 1003
                        is_extended_id=False
                    )
                    self.bus.send(response)
                if bytes([0x02,0x10,0x03]) in message.data:
                    response = can.Message(
                        arbitration_id=self.response_id,
                        data=[0x06,0x50, 0x03, 0xAA, 0xBB, 0xCC, 0xDD, 0xAA],  # Positive Response to 1003
                        is_extended_id=False
                    )
                    self.bus.send(response)

class VirtualECUManager:
    def __init__(self):
        """
        Inicializa el manejador de múltiples ECUs virtuales.
        """
        self.ecus = []

    def create_vecu(self):
        """
        Genera una ECU virtual con IDs aleatorios.
        """
        request_id = random.randint(0x600, 0x7EE)
        response_id = request_id + random.randint(0x05,0x10)  # Frame ID cercano
        vecu = VirtualECU(request_id, response_id)
        vecu.start()
        self.ecus.append(vecu)
        return vecu

    def stop_all(self):
        """
        Detiene todas las ECUs virtuales.
        """
        for ecu in self.ecus:
            ecu.stop()
        self.ecus = []


# Ejemplo de uso
if __name__ == "__main__":
    # Configuración del bus CAN
    # Crear el manejador de ECUs virtuales
    manager = VirtualECUManager()

    # Crear varias ECUs virtuales
    for _ in range(1):
        manager.create_vecu()

    try:
        while True:
            pass  # Mantener el programa corriendo
    except KeyboardInterrupt:
        manager.stop_all()
