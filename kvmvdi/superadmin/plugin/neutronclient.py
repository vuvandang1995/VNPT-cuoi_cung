from superadmin.plugin import opsutils
from neutronclient.v2_0 import client as client

class neutron(opsutils.Base):
    def __init__ (self, ip, username, password, project_name, user_domain_id, project_domain_id):
        super().__init__(ip, username, password, project_name, user_domain_id, project_domain_id)
        self.neutron = client.Client(session=self.sess)
        self.network = self.neutron.list_networks()["networks"]

    def list_networks(self):
        network_list = []
        for item in self.network:
            network_keys = {'name'}
            for key, value in item.items():
                if key in network_keys:
                    network_list.append(value)
        network_list.insert(0, "network_list")
        return network_list