# Fibest2026
Creacion de los talleres para el Fibest de 2026

## Primeros pasos 
Creación de los canales virtuales del taller.

## 0- Instalar si no se tienen los canales 
sudo apt update

sudo apt install can-utils

## 1- Activar en ubuntu los canales de CAN:
sudo modprobe can

sudo modprobe can_raw

sudo modprobe can_dev

sudo modprobe vcan

## 2- Verificar que se hayan activado con
lsmod | grep can

## 3- Levantar las interfaces virtuales
sudo ip link add dev vcan0 type vcan

sudo ip link set up vcan0

## 4- Probarla con un envío y una recepción.
Abra dos terminales
  * En el primero escriba: candump vcan0
  * En el segundo: cansend vcan0 123#11223344

## 5- Instalaciones previas.
* venv: sudo apt install python3-venv python3-pip
* Crear el entorno virtual: python3 -m venv .venv
* activar el entorno virtual: source .venv/bin/activate
* Instalaciones de can en python: pip install python-can


## Principales funciones de python-can
* Message: para crear el mensaje: Message(arbitration_id=0x123, data=[1,2,3,4], is_extended_id=False)
* send: para enviar un mensaje, send(msg, timeout=None)
* recv: para escuchar un canal, termina con el primer mensaje escuchado, recv(timeout=None)
