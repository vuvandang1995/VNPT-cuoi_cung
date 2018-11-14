from keystoneauth1 import loading
from keystoneauth1 import session
loader = loading.get_plugin_loader('password')

class Base:
    def __init__(self, ip, username, password, project_name, user_domain_id, project_domain_id):
        self.ip = ip
        self.username = username
        self.password = password
        self.project_name = project_name
        self.project_domain_id = project_domain_id
        self.user_domain_id = user_domain_id
        auth_url = "http://"+self.ip+":5000/v3"
        self.auth = loader.load_from_options(auth_url=auth_url, username=self.username, password=self.password, project_name=self.project_name, user_domain_id=self.user_domain_id, project_domain_id=self.project_domain_id)
        self.sess = session.Session(auth=self.auth)
        # self.auth = loader.load_from_options(auth_url="http://192.168.40.146:5000/v3", username='admin', password='ok123', project_name='admin', user_domain_id='default', project_domain_id='default')