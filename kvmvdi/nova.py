from keystoneauth1 import loading
from keystoneauth1 import session
from novaclient import client
from glanceclient import Client
from neutronclient.v2_0 import client as client_neutron #dòng này có nghĩa là thay tên cho "client" cần được import vào để tránh trùng với dùng thứ 3
loader = loading.get_plugin_loader('password')

# xác thực kết nối tới Controller
auth = loader.load_from_options(auth_url="http://192.168.40.61:5000/v3", username="admin", password="ducnm37", project_name="admin", user_domain_id="default", project_domain_id="default")

# tạo phiên kết nối
sess = session.Session(auth=auth)

# tạo các class add session và version
nova = client.Client(2, session=sess)
glance = Client('2', session=sess)
neutron = client_neutron.Client(session=sess)

# lấy ra các thành phần cần thiết
# im = glance.images.get("e51826a7-72a2-4ffb-a16c-adad74ffc681") # lấy ra image có id là e51826a7-72a2-4ffb-a16c-adad74ffc681
im = nova.glance.find_image("cirros") # lấy ra image có name hoac id la cirros

fl = nova.flavors.find(name="tiny") # lấy ra flavor có name là tiny

# net = neutron.list_networks(name="self service") # lấy ra mạng có tên là self service
net = nova.neutron.find_network("self service") # lấy ra mạng có tên là self service
# network_id = net['networks'][0]['id'] # lấy ra id của network trên

nova.servers.create("myserver", flavor=fl, image=im, nics = [{'net-id':net.id}],) # lệnh tạo VM
sv = nova.servers.get("b6322a3a-66d3-43a2-86ff-b3e76f039b08")
print(sv.get_vnc_console("novnc"))


# image = glance.images.create(name="myNewImage")
# glance.images.upload(image.id, open('/home/mdtpro2018/Downloads/ubuntu-18.04.1-desktop-amd64.iso', 'rb'))
print('ok roi')