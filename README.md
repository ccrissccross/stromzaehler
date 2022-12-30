# stromzaehler

reads power-consumption (utilizing the "S0"-interface of my powermeter) and ingests measured data into a MySQL-instance running on a different server

# On Raspberry Pis:
1) install RPi.GPIO lib:
   sudo apt-get install RPi.GPIO
2) install and build libgiod (to be able to use DHT-sensors):
   sudo apt install libgpiod-dev git build-essential
   git clone https://github.com/adafruit/libgpiod_pulsein.git
   cd libgpiod_pulsein/src
   make

# start REST API
gunicorn -w 4 -b 127.0.0.1 --error-logfile /var/log/gunicorn/error.log --log-level info --access-logfile /var/log/gunicorn/access.log stromzaehler.backend.src.main.main:app