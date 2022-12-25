# 크롬 드라이버 설치.
import re
import os
import stat
import glob
import shutil
import requests
import subprocess
from zipfile import ZipFile
from bs4 import BeautifulSoup
from tempfile import gettempdir
from urllib.parse import urljoin


# 크롬드라이버의 다운로드 url를 가져옴
def _get_download_url_chrome(browser_version):
    hp_url = 'https://chromedriver.chromium.org/downloads'

    r = requests.get(hp_url)
    soup = BeautifulSoup(r.text, 'html.parser')
    for x in soup.find_all('a'):
        atext = x.text
        rec = re.compile(r'ChromeDriver\s[\d.]+')
        m = rec.search(atext)
        if m is None:
            continue
        version = atext.split()[1]
        if version.startswith(browser_version + '.'):
            href = x.get('href')
            r = requests.get(href)
            soup = BeautifulSoup(r.text, 'html.parser')
            # chromedriver_linux64.zip
            d_link = None
            download_link = urljoin(href, version + '/chromedriver_win32.zip')
            if download_link:
                return download_link


# 크롬드라이버를 설치함.
def _download_driver(driver_path, browser_version):
    url = _get_download_url_chrome(browser_version)
    r = requests.get(url, allow_redirects=True)
    is_unzip = url.lower().endswith('.zip')
    if is_unzip:
        with open(f'{driver_path}.zip', 'wb') as ofp:
            ofp.write(r.content)
        tmp_d = os.path.join(gettempdir(), os.path.basename(driver_path))
        with ZipFile(f'{driver_path}.zip') as zfp:
            zflist = zfp.namelist()
        wd_name = None
        for zf in zflist:
            if zf.find('/') > 0 or zf.find('\\') > 0:
                continue
            wd_name = zf
            break
        if not wd_name:
            raise ReferenceError(f'Cannot find webdriver at "{driver_path}.zip"')
        with ZipFile(f'{driver_path}.zip') as zfp:
            zfp.extract(wd_name, tmp_d)
        for f in glob.glob(os.path.join(tmp_d, '*')):
            shutil.move(f, driver_path)
            break
        shutil.rmtree(tmp_d)
        os.remove(f'{driver_path}.zip')
    else:
        with open(driver_path, 'wb') as ofp:
            ofp.write(r.content)
    st = os.stat(driver_path)
    os.chmod(driver_path, st.st_mode | stat.S_IEXEC)


# 크롬드라이버의 버전을 가져옴.
def get_driver():
    cmd = [
        'powershell',
        '-command',
        r"(Get-Item (Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe').'(Default)').VersionInfo"
                    ]
    po = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    po.wait()
    out = po.stdout.read().decode().strip()
    lines = out.split('\n')
    bv = lines[-1].split('.')[0]
    browser_version = bv.split('.')[0]
    po.stdout.close()

    CACHE_FOLDER = os.path.join(r'C:\Users\akb09\Desktop\Study\Python Selenium Basic', 'driver')
    bn = f'win32_Chrome_{browser_version}.exe'
    driver_path = os.path.join(CACHE_FOLDER, bn)
    if not os.path.exists(driver_path):
        os.makedirs(driver_path)
        _download_driver(driver_path, browser_version)
    driver_f = os.path.join(driver_path, 'chromedriver.exe')
    return driver_f


if __name__ == '__main__':
    a = get_driver()
    print(a)
