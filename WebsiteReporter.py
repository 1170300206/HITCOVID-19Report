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
        self.twloginUrl = self.reader.get('temperature', 'Login-url')
        self.addUrl = self.reader.get('Website', 'addUrl')
        self.editUrl = self.reader.get('Website', 'editUrl')
        self.saveUrl = self.reader.get('Website', 'saveUrl')
        self.pushUrl = self.reader.get('Push', 'pushUrl')

    def login_mrsb(self):
        rtn = self.session.post(self.loginUrl, data=self.getLoginInfo())
        print(rtn.url)
        if 'xg.hit.edu.cn/zhxy-xgzs/xg_yqglxs/xsmrsb' in rtn.url:
            print('user:' + self.usr + " login success!")
            return True
        return False

    def login_twsb(self):
        rtn = self.session.post(self.twloginUrl, data=self.getLoginInfo())
        print(rtn.url)
        if 'xg.hit.edu.cn/zhxy-xgzs/xg_yqglxs/xsmrsb' in rtn.url:
            print('user:' + self.usr + " login success!")
            return True
        return False

    def writeLog(self, flag, time, filename ='log.txt'):
        with open(os.path.join(os.path.dirname(__file__), filename), "a+", encoding="utf-8") as f:
            f.write(time + "\t" + flag + "\n")

    @staticmethod
    def readState(filename, time):
        with open(os.path.join(os.path.dirname(__file__), filename), "r", encoding="utf-8") as f:
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

    def reportTemperature(self, morning = True):
        rtn = self.session.post(self.reader.get('temperature', 'getstateUrl'))
        rtn = json.loads(rtn.content)
        if rtn['module'][0]['sfdt'] == "1":
            #self.pushMsg(time.strftime("%m-%d %H:%M:%S", time.localtime()) + " 添加体温失败", 
            #        "今日添加体温失败，添加时间为" + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + "\n" +
            #        "上报用户名: " + self.usr + "\n"
            #        + "错误原因：" + '已经生成今日体温')
            tokenstr = rtn['module'][0]["id"]
        else:
            token_url = self.reader.get('temperature', 'token-url')
            tokenstr = bytes.decode(self.session.post(token_url).content)
            addUrl = self.reader.get('temperature', 'addUrl')
            result = self.session.post(addUrl, data = {"info": json.dumps({'token': tokenstr}, ensure_ascii=False)})
            if json.loads(result.content)['isSuccess']:
                self.pushMsg(time.strftime("%m-%d %H:%M:%S", time.localtime()) + " 添加体温失败", 
                        "今日添加体温失败，添加时间为" + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + "\n" +
                        "上报用户名: " + self.usr + "\n" + "错误原因：" + json.loads(result.content)['msg'])  
        #StateById = self.reader.get('temperature', 'getstateByid')
        #rtn = json.loads(self.session.post(StateById, data = {"info": json.dumps({'id': tokenstr}, ensure_ascii=False)}).content)['module']
        updateUrl = addUrl = self.reader.get('temperature', 'update-url')
        data = {
            "id": tokenstr,
            "sdid1": "1",
            "tw1" : "37.2",
            "fr1" : "0",
            "bs" : "1"
        }
        rtn1 = json.loads(self.session.post(updateUrl, data={"info": json.dumps({"data": data}, ensure_ascii=False)}).content)['isSuccess']
        data = {
            "id": tokenstr,
            "sdid2": "3",
            "tw2" : "37.2",
            "fr2" : "0",
            "bs" : "2"
        }
        rtn2 = json.loads(self.session.post(updateUrl, data={"info": json.dumps({"data": data}, ensure_ascii=False)}).content)['isSuccess']
        if rtn1 and rtn2:
            self.writeLog('success', time.strftime("%m-%d", time.localtime()), "tempLog1.txt")
            self.pushMsg(time.strftime("%m-%d %H:%M:%S", time.localtime()) + " 体温上报成功", 
                    "下午体温上报成功，上报时间为" + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + "\n" +
                    "上报用户名: " + self.usr)
        else:
            self.writeLog('fail', time.strftime("%m-%d", time.localtime()), "tempLog2.txt")
            self.pushMsg(time.strftime("%m-%d %H:%M:%S", time.localtime()) + " 体温上报失败", 
                    "下午体温上报失败，上报时间为" + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + "\n" +
                    "上报用户名: " + self.usr)



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
    if not WebsiteReporter.readState('log.txt', time.strftime("%m-%d", time.localtime())):
        reporter = WebsiteReporter()
        reporter.login_mrsb()
        reporter.report()