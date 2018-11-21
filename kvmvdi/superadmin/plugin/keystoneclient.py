from superadmin.plugin import opsutils
from keystoneclient.v3 import client
from kvmvdi.settings import RULE_USER, RULE_ADMIN

class keystone(opsutils.Base):
    def __init__ (self, ip, username, password, project_name, user_domain_id, project_domain_id):
        super().__init__(ip, username, password, project_name, user_domain_id, project_domain_id)
        self.token_id = self.sess.get_token(self.auth)
        self.keystone = client.Client(session=self.sess)

    def create_project(self, name, domain):
        self.keystone.projects.create(name=name, domain=domain, description=None, enabled=True, parent=None)
    
    def create_user(self, name, domain, project, password, email):
        self.keystone.users.create(name=name, domain=domain, project=project, password=password, email=email, description=None, enabled=True, parent=None)

    def add_user_to_project(self, user, project):
        self.user = self.keystone.users.find(name=user)
        self.project = self.keystone.projects.find(name=project)
        self.role = self.keystone.roles.find(name=RULE_USER)
        self.keystone.roles.grant(self.role, user=self.user, project=self.project)


    def find_project(self, project):
        return self.keystone.projects.find(name=project)

    def find_user(self, user):
        return self.keystone.users.find(name=user)
    # def get_role(self):
    #     print(self.keystone.roles.find(name='admin'))
    #     print(self.keystone.projects.find(name='user1'))
    #     print(self.keystone.users.find(name='admin'))