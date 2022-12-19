# stromzaehler

reads power-consumption (utilizing the "S0"-interface of my powermeter) and ingests measured data into a MySQL-instance running on a different server


gunicorn start-command:
gunicorn -w 4 -b 127.0.0.1 --error-logfile /var/log/gunicorn/error.log --log-level info --access-logfile /var/log/gunicorn/access.log stromzaehler.backend.src.main.main:app