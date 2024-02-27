#!/bin/bash
set -x

HARP_FOLDER="/home/pi/harp"
VENV_FOLDER="${HARP_FOLDER}/venv"
GITHUB_REPO="https://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@github.com/stephenpaulraj/harp-prod.git"
GITHUB_VERSION_FILE="https://raw.githubusercontent.com/stephenpaulraj/harp/main/version.txt"
TEMP_FOLDER="/home/pi/temp"

sudo apt-get update
sudo apt-get install -y python3-pip git python3-venv

if [ ! -d ${HARP_FOLDER} ]; then
    mkdir ${HARP_FOLDER}
    python3 -m venv ${VENV_FOLDER}
fi

if [ ! -d ${TEMP_FOLDER} ]; then
    mkdir ${TEMP_FOLDER}
fi

cd ${TEMP_FOLDER}
git clone ${GITHUB_REPO}
cp -r ${TEMP_FOLDER}/harp/* ${HARP_FOLDER}/
rm -rf ${TEMP_FOLDER}/*
cd ${HARP_FOLDER}

source venv/bin/activate
pip install -r requirement.txt
python main.py