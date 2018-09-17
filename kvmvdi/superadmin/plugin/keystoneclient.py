from superadmin.plugin import opsutils
from keystoneclient.v3 import client

class keystone(opsutils.Base):
    def __init__ (self, ip, username, password, project_name, user_domain_id, project_domain_id):
        super().__init__(ip, username, password, project_name, user_domain_id, project_domain_id)
        self.keystone = client.Client(session=self.sess)

    def create_project(self, name, domain):
        self.keystone.projects.create(name=name, domain=domain, description=None, enabled=True, parent=None)

    # def add_user_to_project(self, user, project):
    #     self.user = self.keystone.users.get('admin')
    #     self.project = self.keystone.users.get('admin')
    #     self.keystone.grant(role, user=user, project=project)

    # def get_role(self):
    #     print(self.keystone.roles.get('68134d4111374c9ba9aea9d09683375b'))