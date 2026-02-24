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
