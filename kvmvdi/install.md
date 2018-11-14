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
