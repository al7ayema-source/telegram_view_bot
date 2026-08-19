#!/bin/bash

# تحديث الحزم
apt-get update

# تثبيت Chrome و Chromium
apt-get install -y wget curl unzip

# تحميل وتثبيت Chrome
wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list
apt-get update
apt-get install -y google-chrome-stable

# تثبيت Chromium كبديل
apt-get install -y chromium chromium-driver

# تثبيت المكتبات المطلوبة
pip install -r requirements.txt

echo "✅ تم تثبيت Chrome بنجاح"
