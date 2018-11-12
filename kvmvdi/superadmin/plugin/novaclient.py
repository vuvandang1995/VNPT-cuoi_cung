from superadmin.plugin import opsutils
from novaclient import client
from neutronclient.v2_0 import client as client_neutron #dòng này có nghĩa là thay tên cho "client" cần được import vào để tránh trùng với dùng thứ 3

class nova(opsutils.Base):
    def __init__ (self, ip, username, password, project_name, user_domain_id, project_domain_id):
        super().__init__(ip, username, password, project_name, user_domain_id, project_domain_id)
        self.nova = client.Client(2, session=self.sess)
        self.neutron = client_neutron.Client(session=self.sess)
        self.network = self.neutron.list_networks()["networks"]
        self.servers = self.nova.servers.list()
        try:
            self.services = self.nova.services.list()
            self.flavors = self.nova.flavors.list()
            self.images = self.nova.glance.list()
            self.hypervisors = self.nova.hypervisors.list()
        except:
            pass
    
    def list_server(self):
        return self.servers

    def get_server(self, serverid):
        return self.nova.servers.get(serverid)

    def list_hypervisor(self):
        return self.hypervisors

    def find_hypervisor(self, hypervisor):
        return self.nova.hypervisors.get(hypervisor)

    def list_images(self):
        image_list = []
        for image in self.images:
            image_list.append(image.name)
        image_list.insert(0, "image_list")
        return image_list

    def list_flavor(self):
        fl = self.flavors
        flavor_list = []
        for flavor in fl:
            combo = []
            combo = [flavor.ram, flavor.vcpus, flavor.disk]
            flavor_list.append(combo)
        return flavor_list

    def createVM(self, svname, flavor, image, network_id, max_count):
        # self.nova.servers.create(svname, flavor=flavor, image=image, nics = [{'net-id':network_id}], max_count=max_count, availability_zone='nova:compute2')
        self.nova.servers.create(svname, flavor=flavor, image=image, nics = [{'net-id':network_id}], max_count=max_count)

    def createFlavor(self, svname, ram, vcpus, disk):
        self.nova.flavors.create(svname, ram, vcpus, disk, flavorid='auto', ephemeral=0, swap=0, rxtx_factor=1.0, is_public=True, description=None)

    def delete_vm(self, svid):
        self.nova.servers.delete(svid)
    
    def start_vm(self, svid):
        self.nova.servers.start(svid)

    def reboot_vm(self, svid):
        self.nova.servers.reboot(svid, reboot_type='SOFT')

    def stop_vm(self, svid):
        self.nova.servers.stop(svid)

    def snapshot_vm(self, svid, snapshotname):
        self.nova.servers.create_image(svid, image_name=snapshotname)

    def backup_vm(self, svid, backup_name, backup_type, rotation):
        self.nova.servers.backup(svid, backup_name=backup_name, backup_type=backup_type, rotation=rotation)
    
    def find_flavor(self, ram=None, vcpus=None, disk=None, id=None):
        if id is None:
            return self.nova.flavors.find(ram=ram, vcpus=vcpus, disk=disk)
        else:
            return self.nova.flavors.find(id=id)
    
    def find_image(self, image):
        return self.nova.glance.find_image(image)

    def find_network(self, network):
        return self.nova.neutron.find_network(network).id

    def list_networks(self):
        network_list = []
        for item in self.network:
            network_keys = {'name'}
            for key, value in item.items():
                if key in network_keys:
                    network_list.append(value)
        network_list.insert(0, "network_list")
        return network_list