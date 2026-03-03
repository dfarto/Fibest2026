import random
import can
import threading
from time import sleep, time

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
        self.sesion = 1
        self.session_time = 0
        self.iter = 0
        self.basic_msg = can.Message(
                        arbitration_id=random.randint(0x300, 0x600),
                        data= [0x41, 0x4c, 0x49, 0x56, 0x45, 0x00, 0x00, 0x00],
                        is_extended_id=False
                    )
        self.basic_msg_thread = None
        self.sec_seed = 0
        self.low_ids = 0
        self.prev_timeout = time()

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
            sleep(0.1)
            self.session_time+=0.1
            if self.session_time >= 2.0:
                self.sesion = 1
                self.basic_msg.data = [0x41, 0x4c, 0x49, 0x56, 0x45, 0x00, 0x00, 0x00]
            self.basic_msg.data[7] = self.iter

    def _session_serv(self, data:list):
        if data[0] == 0x02:
            match data[2]:
                case 0x01:
                    response = can.Message(
                        arbitration_id=self.response_id,
                        data=[0x06,0x50, 0x01, 0xAA, 0xBB, 0xCC, 0xDD, 0xAA],
                        is_extended_id=False
                    )
                    self.sesion = 1
                    self.session_time = 0
                    self.basic_msg.data = [0x41, 0x4c, 0x49, 0x56, 0x45, 0x00, 0x00, 0x00]
                case 0x02:
                    if self.sesion in [2, 3, 27]:
                        response = can.Message(
                            arbitration_id=self.response_id,
                            data=[0x06,0x50, 0x02, 0xAA, 0xBB, 0xCC, 0xDD, 0xAA],
                            is_extended_id=False
                        )
                        self.sesion = 2
                        self.session_time = 0
                        self.basic_msg.data = [0x50, 0x52, 0x4f, 0x47, 0x52, 0x41, 0x4d, 0x00]
                    else:
                        response = can.Message(
                            arbitration_id=self.response_id,
                            data=[0x03,0x7f, 0x10, 0x7e, 0xBB, 0xCC, 0xDD, 0xAA],
                            is_extended_id=False
                        )
                case 0x03:
                    response = can.Message(
                        arbitration_id=self.response_id,
                        data=[0x06,0x50, 0x03, 0xAA, 0xBB, 0xCC, 0xDD, 0xAA],
                        is_extended_id=False
                    )
                    self.sesion = 3
                    self.session_time = 0
                    self.basic_msg.data = [0x45, 0x58, 0x54, 0x45, 0x4E, 0x44, 0x00, 0x00]
                case 0x04:
                    if self.sesion in [27]:
                        response = can.Message(
                            arbitration_id=self.response_id,
                            data=[0x06,0x50, 0x04, 0xAA, 0xBB, 0xCC, 0xDD, 0xAA],
                            is_extended_id=False
                        )
                        self.sesion = 4
                        self.session_time = 0
                        self.basic_msg.data = [0x53, 0x41, 0x46, 0x45, 0x54, 0x59, 0x00, 0x00]
                    else:
                        response = can.Message(
                            arbitration_id=self.response_id,
                            data=[0x03,0x7f, 0x10, 0x7e, 0xBB, 0xCC, 0xDD, 0xAA],
                            is_extended_id=False
                        )
                case _:
                    response = can.Message(
                        arbitration_id=self.response_id,
                        data=[0x03,0x7f, 0x10, 0x12, 0xBB, 0xCC, 0xDD, 0xAA],
                        is_extended_id=False
                    )

        else:
            response = can.Message(
                    arbitration_id=self.response_id,
                    data=[0x03,0x7f, 0x10, 0x13, 0xBB, 0xCC, 0xDD, 0xAA],
                    is_extended_id=False
                )
        self.bus.send(response)

    def _reset_serv(self, data: list):
        if data[0] == 0x02:
            match data[2]:
                case 0x01:
                    response = can.Message(
                        arbitration_id=self.response_id,
                        data=[0x02, 0x51, 0x01, 0xBB, 0xCC, 0xDD, 0xAA, 0xAA],
                        is_extended_id=False
                    )
                case 0x02:
                    if self.sesion in [0x03, 0x02, 0x04, 0x27]:
                        response = can.Message(
                            arbitration_id=self.response_id,
                            data=[0x02, 0x51, 0x02, 0xBB, 0xCC, 0xDD, 0xAA, 0xAA],
                            is_extended_id=False
                        )
                    else:
                        response = can.Message(
                            arbitration_id=self.response_id,
                            data=[0x03, 0x7f, 0x11, 0x7E, 0xCC, 0xDD, 0xAA, 0xAA],
                            is_extended_id=False
                        )
                case 0x03:
                    if self.sesion in [0x02, 0x04, 0x27]:
                        response = can.Message(
                            arbitration_id=self.response_id,
                            data=[0x02, 0x51, 0x03, 0xBB, 0xCC, 0xDD, 0xAA, 0xAA],
                            is_extended_id=False
                        )
                    else:
                        response = can.Message(
                            arbitration_id=self.response_id,
                            data=[0x03, 0x7f, 0x11, 0x7E, 0xCC, 0xDD, 0xAA, 0xAA],
                            is_extended_id=False
                        )
                case 0x10:
                    self.stop()
                case _:
                    response = can.Message(
                        arbitration_id=self.response_id,
                        data=[0x0e,0x7f, 0x11, 0x12, 0xBB, 0xCC, 0xDD, 0xAA],
                        is_extended_id=False
                    )
        else:
            response = can.Message(
                    arbitration_id=self.response_id,
                    data=[0x03,0x7f, 0x11, 0x13, 0xBB, 0xCC, 0xDD, 0xAA],
                    is_extended_id=False
                )
        try:
            self.bus.send(response)
        except:
            pass

    def _read_serv(self, data: list):
        if data[0] == 0x03:
            if data[2] == 0xf1 and data[3]>0x80:
                response = can.Message(
                        arbitration_id=self.response_id,
                        data=[0x07,0x62, 0xf1, data[3], 0x4E, 0x49, 0x43, 0x45],
                        is_extended_id=False
                    )
            else:
                response = can.Message(
                        arbitration_id=self.response_id,
                        data=[0x03,0x7F, 0x22, 0x12, 0xAA, 0xAA, 0xAA, 0xAA],
                        is_extended_id=False
                    )
        else:
            response = can.Message(
                    arbitration_id=self.response_id,
                    data=[0x03,0x7F, 0x22, 0x13, 0xAA, 0xAA, 0xAA, 0xAA],
                    is_extended_id=False
                )
        self.bus.send(response)

    def _one_byte_managing(self, data):
        match data[1]:
            case 0x10:
                response = can.Message(
                        arbitration_id=self.response_id,
                        data=[0x03,0x7f, 0x10, 0x13, 0xBB, 0xCC, 0xDD, 0xAA],
                        is_extended_id=False
                    )
            case 0x11:
                response = can.Message(
                        arbitration_id=self.response_id,
                        data=[0x03,0x7f, 0x11, 0x13, 0xBB, 0xCC, 0xDD, 0xAA],
                        is_extended_id=False
                    )
            case 0x22:
                response = can.Message(
                        arbitration_id=self.response_id,
                        data=[0x03,0x7f, 0x22, 0x13, 0xBB, 0xCC, 0xDD, 0xAA],
                        is_extended_id=False
                    )
            case 0x27:
                response = can.Message(
                        arbitration_id=self.response_id,
                        data=[0x03,0x7f, 0x27, 0x13, 0xBB, 0xCC, 0xDD, 0xAA],
                        is_extended_id=False
                    )
            case 0x2e:
                response = can.Message(
                        arbitration_id=self.response_id,
                        data=[0x03,0x7f, 0x2e, 0x11, 0xBB, 0xCC, 0xDD, 0xAA],
                        is_extended_id=False
                    )
            case 0x3e:
                response = can.Message(
                        arbitration_id=self.response_id,
                        data=[0x03,0x7f, 0x3e, 0x13, 0xBB, 0xCC, 0xDD, 0xAA],
                        is_extended_id=False
                    )
            case _:
                response = can.Message(
                        arbitration_id=self.response_id,
                        data=[0x03,0x7f, data[1], 0x11, 0xBB, 0xCC, 0xDD, 0xAA],
                        is_extended_id=False
                    )
        self.bus.send(response)
    
    def _secur_access_managing(self, data):
        match data[2]:
            case 0x01:
                if self.sesion in [0x03, 0x02, 0x04]:
                    self.sec_seed=[random.randint(00, 255) for _ in range(5)]
                    response = can.Message(
                        arbitration_id=self.response_id,
                        data=[0x07,0x67, 0x01]+ self.sec_seed,
                        is_extended_id=False
                    )
                else:
                    response = can.Message(
                        arbitration_id=self.response_id,
                        data=[0x03,0x7f, 0x27, 0x7E, 0xBB, 0xCC, 0xDD, 0xAA],
                        is_extended_id=False
                    )
            case 0x02:
                if self.sesion in [0x03, 0x02, 0x04]:
                    if data[0] == 0x07:
                        if data[3:] == self.sec_seed[3:] + self.sec_seed[:2] + [self.request_id & 0xFF]:
                            response = can.Message(
                                arbitration_id=self.response_id,
                                data=[0x03,0x67, 0x02]+ [0xaa]*5,
                                is_extended_id=False
                            )
                            self.sesion = 27
                            self.session_time = 0
                            self.basic_msg.data = [0x53, 0x45, 0x43, 0x55, 0x52, 0x59, 0x54, 0x00]
                        else:
                            response = can.Message(
                                arbitration_id=self.response_id,
                                data=[0x03,0x7f, 0x27, 0x33, 0xBB, 0xCC, 0xDD, 0xAA],
                                is_extended_id=False
                            )
                    else:
                        response = can.Message(
                        arbitration_id=self.response_id,
                        data=[0x03,0x7f, 0x27, 0x13, 0xBB, 0xCC, 0xDD, 0xAA],
                        is_extended_id=False
                    )
                else:
                    response = can.Message(
                        arbitration_id=self.response_id,
                        data=[0x03,0x7f, 0x27, 0x7E, 0xBB, 0xCC, 0xDD, 0xAA],
                        is_extended_id=False
                    )
            case _:
                response = can.Message(
                        arbitration_id=self.response_id,
                        data=[0x03,0x7f, 0x27, 0x12, 0xBB, 0xCC, 0xDD, 0xAA],
                        is_extended_id=False
                    )
        self.bus.send(response)
        
    def _tester_present_managing(self, data):
        match data[2]:
            case 0x00:
                self.session_time = 0
                response = can.Message(
                    arbitration_id=self.response_id,
                    data=[0x07, 0x7E, 0x00]+[0xaa]*5,
                    is_extended_id=False
                )
                self.bus.send(response)
            case 0x80:
                response = can.Message(
                    arbitration_id=self.response_id,
                    data=[0x07, 0x7E, 0x00]+[0xaa]*5,
                    is_extended_id=False
                )
                self.session_time = 0
            case _:
                response = can.Message(
                        arbitration_id=self.response_id,
                        data=[0x03,0x7f, 0x2e, 0x12, 0xBB, 0xCC, 0xDD, 0xAA],
                        is_extended_id=False
                    )
                self.bus.send(response)

    def _noiso_tp_bytes_managing(self, data):
        match data[1]: # session control
            case 0x10:
                self._session_serv(data)
            case 0x11:
                self._reset_serv(data)
            case 0x22:
                self._read_serv(data)
            case 0x27:
                self._secur_access_managing(data)
            case 0x2e:
                response = can.Message(
                        arbitration_id=self.response_id,
                        data=[0x03,0x7f, 0x2e, 0x11, 0xBB, 0xCC, 0xDD, 0xAA],
                        is_extended_id=False
                    )
                self.bus.send(response)
            case 0x3e:
                self._tester_present_managing(data)
            case _:
                response = can.Message(
                        arbitration_id=self.response_id,
                        data=[0x03,0x7f, data[1], 0x11, 0xBB, 0xCC, 0xDD, 0xAA],
                        is_extended_id=False
                    )

    def listen_and_respond(self):
        """
        Escucha los mensajes y responde si detecta un mensaje con 1003.
        """
        while self.running:
            message = self.bus.recv(1)  # Timeout de 1 segundo
            if message:
                try:
                    data = list(message.data)
                except:
                    data = []

            if message and message.arbitration_id == self.request_id:
                if data[0] == 0x01: # 1 byte
                    self._one_byte_managing(data=data)
                elif data[0] <= 0x07: # Otros tamaños de mensaje
                    self._noiso_tp_bytes_managing(data=data)

                else:
                    response = can.Message(
                        arbitration_id=self.response_id,
                        data=[0x03,0x7f, list(message.data)[1], 0x13, 0xAA, 0xAA, 0xAA, 0xAA],  # Positive Response to 1003
                        is_extended_id=False
                    )
                    self.bus.send(response)
            if message and message.arbitration_id <= 0x300:
                self.low_ids += 1
            else:
                self.low_ids = 0
            if message and data[:8] == self.basic_msg.data[:8] and time() - self.prev_timeout < 0.9:
                self.low_ids += 2
            else:
                self.prev_timeout = time()
                self.low_ids = 0
            if self.low_ids == 10:
                self.stop()
            
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
