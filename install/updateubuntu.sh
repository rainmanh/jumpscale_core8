apt-get update
apt-get autoremove -y
apt-get -f install -y
apt-get upgrade -y
apt-get install mc curl git ssh python3.5 python-requests  -y

rm -f /usr/bin/python
rm -f /usr/bin/python3
ln -s /usr/bin/python3.5 /usr/bin/python
ln -s /usr/bin/python3.5 /usr/bin/python3
