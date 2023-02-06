#!/bin/bash


if [ -a /dev/rfcomm* ]
then
echo "Bluetooth ja mapeado e ativo"
else
echo "Pressione botão zero do terminal"
sudo hcitool scan
read -p "Insira o mac-address correto = " mac
#read -p "Escolha a porta rfcomm = " porta

sudo rfcomm release all
sudo rfcomm bind /dev/rfcomm0 $mac 1
sudo chmod 777 /dev/rfcomm0
fi


