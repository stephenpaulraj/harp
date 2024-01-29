#!/bin/bash
set -x

HARP_FOLDER="/home/pi/harp"
VENV_FOLDER="${HARP_FOLDER}/venv"
GITHUB_REPO="https://github.com/stephenpaulraj/harp"
GITHUB_VERSION_FILE="https://raw.githubusercontent.com/stephenpaulraj/harp/main/version.txt"
TEMP_FOLDER="/home/pi/temp"

echo "nameserver 8.8.8.8" | sudo tee -a /etc/resolv.conf
service networking restart

sudo apt-get update
sudo apt-get install -y python3-pip git python3-venv

if [ ! -d ${HARP_FOLDER} ]; then
    mkdir ${HARP_FOLDER}
    python3 -m venv ${VENV_FOLDER}
fi

if [ ! -d ${TEMP_FOLDER} ]; then
    mkdir ${TEMP_FOLDER}
fi

check_tun0() {
    if ip link show tun0 &> /dev/null; then
        return 0
    else
        return 1
    fi
}

if ! check_tun0; then
    sudo openvpn --daemon --config /home/pi/vpn/gateway.ovpn
    sleep 60
    sudo supervisorctl restart tuxtunnel
fi

sudo mmcli -m 0 -e

cd ${TEMP_FOLDER}
git clone ${GITHUB_REPO}
cp -r ${TEMP_FOLDER}/harp/* ${HARP_FOLDER}/
rm -rf ${TEMP_FOLDER}/*
cd ${HARP_FOLDER}

source venv/bin/activate
pip install -r requirement.txt
python main.py