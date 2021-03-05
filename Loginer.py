import base64
import sys
import random
from Crypto.Cipher import AES
from Crypto import Random
from bs4 import BeautifulSoup
import time


class Aes(object):

    @staticmethod
    def AESencrypt(data, passwd, iv):
        length = len(iv)
        def pad(s): return s + (length - len(s) %
                                length) * chr(length - len(s) % length)
        cipher = AES.new(passwd.encode("utf-8"),
                         AES.MODE_CBC, iv.encode("utf-8"))
        data = cipher.encrypt(pad(data).encode("utf-8"))
        return base64.b64encode(data).decode("utf-8")

class Loginer(object):
    def __init__(self, usr, passwd):
        self.usr = usr
        self.passwd = passwd
    
    def login(self, session, login_url, check_url):
        rtn = session.post(login_url, data=self.getLoginInfo(session, login_url))
        print(rtn.url)

        if check_url in rtn.url:
            print('user:' + self.usr + " login success!")
            return True, session
        return False, session

    def encrypt(self, data, passwd):
        return Aes.AESencrypt(self.rndStr(64)+data, passwd, self.rndStr(16))

    def getLoginInfo(self, session, login_url):
        x = session.get(login_url)
        web = BeautifulSoup(x.text, 'lxml')
        data = {}
        data['username'] = self.usr
        hidden = web.findAll("input", attrs={'type': 'hidden'})
        salt = ""
        for item in hidden:
            if item.has_attr('name'):
                data[item['name']] = item['value']
            else:
                salt = item['value']
        data['password'] = self.encrypt(self.passwd, salt)
        return data

    def rndStr(self, length):
        return "".join(random.choices('ABCDEFGHJKMNPQRSTWXYZabcdefhijkmnprstwxyz2345678', k=length))


    def captchaState(self, session):
        postData = {
            'username': self.usr,
            'pwdEncrypt2': 'pwdEncryptSalt',
            '_': int(time.time())
        }
        x = session.post(self.captcha, data=postData)
        if "true" in x.text:
            return True
        return False