from superadmin.plugin import opsutils
from keystoneauth1.identity import v3
from keystoneauth1 import session
from novaclient import client
from cinderclient import client as client_cinder
from neutronclient.v2_0 import client as client_neutron #dòng này có nghĩa là thay tên cho "client" cần được import vào để tránh trùng với dùng thứ 3

class nova():
    def __init__(self, ip, token_id, project_name, project_domain_id):
        self.auth = v3.Token(auth_url="http://"+ip+":5000/v3", token=token_id, project_domain_id=project_domain_id, project_name=project_name, reauthenticate=False)
        self.sess = session.Session(auth=self.auth)
        self.nova = client.Client(2, session=self.sess)
        self.cinder = client_cinder.Client(3, session=self.sess)
        self.neutron = client_neutron.Client(session=self.sess)
        self.network = self.neutron.list_networks()["networks"]
        self.servers = self.nova.servers.list()
        self.flavors = self.nova.flavors.list()
        self.images = self.nova.glance.list()
        try:
            self.services = self.nova.services.list()
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

    def createVM(self, svname, flavor, image, network_id, max_count, volume_id, key_name, admin_pass):
        # self.nova.servers.create(svname, flavor=flavor, image=image, nics = [{'net-id':network_id}], max_count=max_count, availability_zone='nova:compute2')
        return self.nova.servers.create(svname, flavor=flavor, image=image, nics = [{'net-id':network_id}], block_device_mapping = {'vda': volume_id}, key_name=key_name, admin_pass=admin_pass, max_count=max_count)

    def createFlavor(self, svname, ram, vcpus, disk):
        self.nova.flavors.create(svname, ram, vcpus, disk, flavorid='auto', ephemeral=0, swap=0, rxtx_factor=1.0, is_public=True, description=None)

    def create_sshkey(self, sshkeyname):
        return self.nova.keypairs.create(name=sshkeyname)

    def create_volume(self, name, imageRef, size, volume_type):
        if int(size) > 0:
            self.cinder.volumes.create(size=size, name=name, imageRef=imageRef, volume_type=volume_type)
        else:
            self.cinder.volumes.create(size='10', name=name, imageRef=imageRef, volume_type=volume_type)

    def delete_vm(self, svid):
        self.nova.servers.delete(svid)
    
    def start_vm(self, svid):
        self.nova.servers.start(svid)

    def reboot_vm(self, svid):
        self.nova.servers.reboot(svid, reboot_type='SOFT')
    
    def reboot_vm_hard(self, svid):
        self.nova.servers.reboot(svid, reboot_type='HARD')

    def stop_vm(self, svid):
        self.nova.servers.stop(svid)

    def rebuild(self, svid, image, disk_config):
        self.nova.servers.rebuild(svid, image=image, disk_config=disk_config)

    def snapshot_vm(self, svid, snapshotname):
        self.nova.servers.create_image(svid, image_name=snapshotname)

    def resetpass(self, svid, newpass):
        self.nova.servers.change_password(svid, password=newpass)

    def backup_vm(self, svid, backup_name, backup_type, rotation):
        self.nova.servers.backup(svid, backup_name=backup_name, backup_type=backup_type, rotation=rotation)
    
    def find_flavor(self, ram=None, vcpus=None, disk=None, id=None):
        if id is None:
            return self.nova.flavors.find(ram=ram, vcpus=vcpus, disk=disk)
        else:
            return self.nova.flavors.find(id=id)
    
    def find_image(self, image):
        return self.nova.glance.find_image(image)

    def check_volume(self, name):
        return self.cinder.volumes.find(name=name).status

    def find_volume(self, name):
        return self.cinder.volumes.find(name=name)

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

    def list_sshkey(self):
        sshkey_list = []
        for item in self.nova.keypairs.list():
            sshkey_list.append(item.name)
        sshkey_list.insert(0, "sshkey_list")
        return sshkey_list