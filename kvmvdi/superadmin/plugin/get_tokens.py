import requests
import json
from opsutils import Base

def gettoken():
    url ='http://192.168.40.146:5000/v2.0/tokens'
    data = {"auth": {"tenantName":"admin","passwordCredentials":{"username":"admin","password":"ok123"}}}
    a = requests.post(url,json.dumps(data),headers = {'Content-Type':'application/json'})
    if a.status_code !=200:
	    raise Exception("Platform9 login returned %d, body: %s" %(a.status_code, a.text))
    else:
	    response = a.json()
	    return response

respon = gettoken()
token =  respon['access']['token']['id']
print(token)

connect = Base(ip='192.168.40.146', username='admin', password='ok123', project_name='admin', user_domain_id='default', project_domain_id='default')
