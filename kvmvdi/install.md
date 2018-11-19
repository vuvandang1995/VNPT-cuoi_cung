### Cài đặt môi trường cần thiết 
```
sudo apt-get update
sudo apt-get -y upgrade
sudo apt-get install -y python3-pip 
sudo apt-get install -y python3.5-dev libmysqlclient-dev  memcached libffi-dev libssl-dev
sudo apt-get install -y git nginx redis-server
```

### Tải source code và cài các gói cần thiết để chạy code 
```
git clone https://github.com/vuvandang1995/VNPT-cuoi_cung.git
cd VNPT-cuoi_cung
export LC_ALL="en_US.UTF-8"
export LC_CTYPE="en_US.UTF-8"
sudo pip3 install -r requirements.txt
```

### Lưu ý:
- khi chỉnh sửa cụm OPS, nhớ sửa cả tên rule ở hàm `add_user_to_project` trong `keystoneclient.py`
- sửa địa chỉ IP ở `instances.html` dòng 41
- đổi địa chỉ IP ở `show_instances.html`
- Sửa network ở `client/view.py` dòng 200
- Thay đổi `type_disk` ở modal tạo máy ảo ở `instances.html` dòng 184
## lưu ý python
- Khi đinh nghĩa 1 hàm, biến truyền vào là None, có nghĩa là khi gọi tới hàm, không truyền biến đó thì mặc định nó là None
- Các biến khởi tạo bằng None phải năm cuối
- Ví dụ:
```
def createVM(self, svname, flavor, image, network_id, max_count, key_name=None, admin_pass=None):
        self.nova.servers.create(svname, flavor=flavor, image=image, nics = [{'net-id':network_id}], key_name=key_name, admin_pass=admin_pass, max_count=max_count)
```
