from keystoneauth1 import loading
from keystoneauth1 import session
from novaclient import client
from glanceclient import Client
from neutronclient.v2_0 import client as client_neutron
loader = loading.get_plugin_loader('password')
auth = loader.load_from_options(auth_url="http://192.168.40.61:5000/v3", username="admin", password="ducnm37", project_name="admin", user_domain_id="default", project_domain_id="default")
sess = session.Session(auth=auth)

nova = client.Client(2, session=sess)
glance = Client('2', session=sess)
neutron = client_neutron.Client(session=sess)

im = glance.images.get("e51826a7-72a2-4ffb-a16c-adad74ffc681")
fl = nova.flavors.find(name="tiny")
net = neutron.list_networks(name="self service")
network_id = net['networks'][0]['id']

nova.servers.create("myserver", flavor=fl, image=im, nics = [{'net-id':network_id}],)

