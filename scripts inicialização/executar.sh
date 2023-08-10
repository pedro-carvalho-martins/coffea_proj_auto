#sudo rfcomm release all
#sudo rfcomm bind /dev/rfcomm0 70:4A:0E:D4:E1:D7 1
#sudo chmod 777 /dev/rfcomm0
cd coffea_proj_auto
cd python
python startup_BT_connection.py
sleep 4
nohup python launch_background.py &
sleep 1
python main.py
