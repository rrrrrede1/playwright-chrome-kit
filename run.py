import os
import shutil
import xml.dom.minidom
from datetime import datetime

import requests

url = 'https://tools.google.com/service/update2'

# Create XML request message for Google Omaha
# https://github.com/google/omaha/blob/master/doc/ServerProtocolV3.md
data = """<?xml version="1.0" encoding="UTF-8"?>
<request protocol="3.0" updater="Omaha" updaterversion="1.3.36.112" shell_version="1.3.36.111"
	installsource="update3web-ondemand" dedup="cr" ismachine="0" domainjoined="0">
	<os platform="win" version="10.0.22000.282" arch="x64"/>
	<app appid="{8A69D345-D564-463C-AFF1-A69D9E530F96}" ap="x64-stable-multi-chrome" lang="en-us">
		<updatecheck />
	</app>
</request>"""

response = requests.post(url, data=data)

dom = xml.dom.minidom.parseString(response.text)

print(dom.toprettyxml(indent='  '))

url = dom.getElementsByTagName("url")[0].getAttribute("codebase")
name = dom.getElementsByTagName("action")[0].getAttribute("run")

print(url, name)

response = requests.get(url + name)

# 创建必要的目录结构
os.makedirs('build/release/application/Chrome', exist_ok=True)
os.makedirs('build/release/application/UserData', exist_ok=True)

with open("chrome.7z.exe", "wb") as file:
    file.write(response.content)

os.system('chmod +x ./7zzs')
os.system('./7zzs x chrome.7z.exe')
os.system('./7zzs x chrome.7z')

# 获取Chrome版本号
version = '0.0.0.0'
path = 'Chrome-bin'
for i in os.listdir(path):
    if os.path.isdir(os.path.join(path, i)):
        version = i
        break

print(version)
if version == '0.0.0.0':
    exit(1)

# 移动Chrome文件到新的目录结构
for item in os.listdir('Chrome-bin'):
    source = os.path.join('Chrome-bin', item)
    dest = os.path.join('build/release/application/Chrome', item)
    if os.path.exists(dest):
        shutil.rmtree(dest) if os.path.isdir(dest) else os.remove(dest)
    shutil.move(source, dest)

# 创建启动脚本
start_bat_content = '''@echo off
start "" "%~dp0Chrome\\chrome.exe" --user-data-dir="%~dp0UserData"
'''

with open('build/release/application/start.bat', 'w') as f:
    f.write(start_bat_content)

# 设置构建名称
env = os.getenv('GITHUB_ENV')
if env:
    with open(env, 'a') as f:
        f.write(f'BUILD_NAME=Win64_{version}_{datetime.now().strftime("%Y-%m-%d")}')

# os.system(f'7z.exe a build/release/Win64_{version}_{datetime.now().strftime("%Y-%m-%d")}.7z Chrome')
