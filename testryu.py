import requests, time
from models import alert

while 1:
    url = "https://www.labgen.lid.uff.br/ryu/status.txt"
    response = requests.get(url).json()
    if not response['status']:
        alert.scream()
    time.sleep(5)
