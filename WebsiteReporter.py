 # -*- coding: UTF-8 -*-
import requests
import time
import random
import json
import os
import base64
import sys
from Crypto.Cipher import AES
from Crypto import Random
from readConfig import ConfigReader
from bs4 import BeautifulSoup


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


class WebsiteReporter(object):
    def __init__(self):
        self.reader = ConfigReader()
        self.usr = self.reader.get('DEFAULT', 'usr')
        self.passwd = self.reader.get('DEFAULT', 'passwd')
        self.session = requests.Session()
        self.session.headers = {
            'User-Agent': self.reader.get('Website', 'usr-agent'),
        }
        self.captcha = self.reader.get('Website', 'captcha')
        self.loginUrl = self.reader.get('Website', 'Login-url')
        self.addUrl = self.reader.get('Website', 'addUrl')
        self.editUrl = self.reader.get('Website', 'editUrl')
        self.saveUrl = self.reader.get('Website', 'saveUrl')
        self.pushUrl = self.reader.get('Push', 'pushUrl')

    def login(self):
        rtn = self.session.post(self.loginUrl, data=self.getLoginInfo())
        print(rtn.url)
        if 'xg.hit.edu.cn/zhxy-xgzs/common' in rtn.url:
            print('user:' + self.usr + " login success!")
            return True
        return False

    def writeLog(self, flag, time):
        with open(os.path.join(os.path.dirname(__file__), "log.txt"), "a+", encoding="utf-8") as f:
            f.write(time + "\t" + flag + "\n")

    @staticmethod
    def readState(time):
        with open(os.path.join(os.path.dirname(__file__), "log.txt"), "r", encoding="utf-8") as f:
            logs = f.readlines()
            if len(logs) > 0 and len(logs[-1].strip()) > 0:
                time1, state = logs[-1].split("\t")
                if time1 == time and state.startswith('success'):
                    return True
            return False

    def pushMsg(self, title, msg):
        if self.reader.get('Push', 'pushUrl') is not "":
            requests.post(self.pushUrl, headers={'Content-Type': 'application/json'}, data=json.dumps({
                'token': self.reader.get('Push', 'token'), "title": title, 'content': msg, 'template': self.reader.get('Push', 'template')}).encode("utf-8"))

    def report(self):
        rtn = self.session.post(self.addUrl)
        # print(rtn.url)
        try:
            status = rtn.json()
        except:
            status = {"msg": "网页可能发生了错误"}
            self.writeLog('fail', time.strftime("%m-%d", time.localtime()))
            self.pushMsg(time.strftime("%m-%d %H:%M:%S", time.localtime()) + " 上报失败", 
                    "今日上报失败，上报时间为" + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + "\n" +
                    "上报用户名: " + self.usr + "\n"
                    + "错误原因：" + status['msg'])
            return False
        print(status)
        rtn = self.session.post(
            self.editUrl, data={'info': json.dumps({'id': status['module']})})
        data = rtn.json()['module']['data'][0]
        rtn = self.session.post(
            self.saveUrl, data={'info': json.dumps({'data': data})})
        try:
            print(rtn.text)
            status = rtn.json()
            if(status['isSuccess']):
                self.writeLog('success', time.strftime("%m-%d", time.localtime()))
                self.pushMsg(time.strftime("%m-%d %H:%M:%S", time.localtime()) + " 上报成功", 
                    "今日上报成功，上报时间为" + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + "\n" +
                    "上报用户名: " + self.usr)
                return True
            else:
                self.writeLog('fail', time.strftime("%m-%d", time.localtime()))
                self.pushMsg(time.strftime("%m-%d %H:%M:%S", time.localtime()) + " 上报失败", 
                    "今日上报失败，上报时间为" + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + "\n" +
                    "上报用户名: " + self.usr + "\n"
                    + "错误原因：辅导员已经审查")
                return False
        except:
            self.writeLog('fail', time.strftime("%m-%d", time.localtime()))
            self.pushMsg(time.strftime("%m-%d %H:%M:%S", time.localtime()) + " 上报失败", 
                    "今日上报失败，上报时间为" + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + "\n" +
                    "上报用户名: " + self.usr + "\n"
                    + "错误原因：" + status['msg'])
            return False

    def captchaState(self):
        postData = {
            'username': self.usr,
            'pwdEncrypt2': 'pwdEncryptSalt',
            '_': int(time.time())
        }
        x = self.session.post(self.captcha, data=postData)
        if "true" in x.text:
            return True
        return False

    def encrypt(self, data, passwd):
        return Aes.AESencrypt(self.rndStr(64)+data, passwd, self.rndStr(16))

    def getLoginInfo(self):
        x = self.session.get(self.loginUrl)
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


if __name__ == '__main__':
    if not WebsiteReporter.readState(time.strftime("%m-%d", time.localtime())):
        reporter = WebsiteReporter()
        reporter.login()
        reporter.report()