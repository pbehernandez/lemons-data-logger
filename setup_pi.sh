sudo apt update
sudo apt install -y python3 python3-pip python3-venv i2c-tools
sudo raspi-config nonint do_i2c 0
cd ~/lemons-data-logger
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
chmod +x logger.py
./logger.py
