 # -*- coding: UTF-8 -*-
import requests
import time
import json
import os
from readConfig import ConfigReader
from Loginer import Loginer
from utils import readState, writeLog, pushMsg




class WebsiteReporter(object):
    def __init__(self):
        self.reader = ConfigReader()
        self.usr = self.reader.get('DEFAULT', 'usr')
        self.passwd = self.reader.get('DEFAULT', 'passwd')
        self.loginer = Loginer(self.usr, self.passwd)
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
    
    def login_ask_for_out(self):
        result, self.session = self.loginer.login(self.session, self.loginUrl, 'xg.hit.edu.cn/zhxy-xgzs/xg_yqglxs/xsmrsb')
        return result


    def login_mrsb(self):
        result, self.session = self.loginer.login(self.session, self.loginUrl, 'xg.hit.edu.cn/zhxy-xgzs/xg_yqglxs/xsmrsb')
        return result

    def login_twsb(self):
        result, self.session = self.loginer.login(self.session, self.twloginUrl, 'xg.hit.edu.cn/zhxy-xgzs/xg_yqglxs/xsmrsb')
        return result



    def reportTemperature(self, morning = True):
        rtn = self.session.post(self.reader.get('temperature', 'getstateUrl'))
        rtn = json.loads(rtn.content)
        if len(rtn['module']) > 0 and rtn['module'][0]['sfdt'] == "1":
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
            tokenstr = json.loads(result.content)['module']
            if not json.loads(result.content)['isSuccess']:
                pushMsg(time.strftime("%m-%d %H:%M:%S", time.localtime()) + " 添加体温失败", 
                        "今日添加体温失败，添加时间为" + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + "\n" +
                        "上报用户名: " + self.usr + "\n" + "错误原因：" + json.loads(result.content)['msg'], self.pushUrl, self.reader.get('Push', 'token'), self.reader.get('Push', 'template'))  
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
            writeLog('success', time.strftime("%m-%d", time.localtime()), "tempLog.txt")
            pushMsg(time.strftime("%m-%d %H:%M:%S", time.localtime()) + " 体温上报成功", 
                    "今日体温上报成功，上报时间为" + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + "\n" +
                    "上报用户名: " + self.usr, self.pushUrl, self.reader.get('Push', 'token'), self.reader.get('Push', 'template'))
        else:
            writeLog('fail', time.strftime("%m-%d", time.localtime()), "tempLog.txt")
            pushMsg(time.strftime("%m-%d %H:%M:%S", time.localtime()) + " 体温上报失败", 
                    "今日体温上报失败，上报时间为" + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + "\n" +
                    "上报用户名: " + self.usr, self.pushUrl, self.reader.get('Push', 'token'), self.reader.get('Push', 'template'))



    def report(self):
        rtn = self.session.post(self.addUrl)
        # print(rtn.url)
        try:
            status = rtn.json()
        except:
            status = {"msg": "网页可能发生了错误"}
            writeLog('fail', time.strftime("%m-%d", time.localtime()))
            pushMsg(time.strftime("%m-%d %H:%M:%S", time.localtime()) + " 上报失败", 
                    "今日上报失败，上报时间为" + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + "\n" +
                    "上报用户名: " + self.usr + "\n"
                    + "错误原因：" + status['msg'], self.pushUrl, self.reader.get('Push', 'token'), self.reader.get('Push', 'template'))
            return False
        print(status)
        rtn = self.session.post(
            self.editUrl, data={'info': json.dumps({'id': status['module']})})
        data = rtn.json()['module']['data'][0]
        if 'brzgtw' in data:
            data['brzgtw'] = '36.3'
        rtn = self.session.post(
            self.saveUrl, data={'info': json.dumps({'model': data})})
        try:
            print(rtn.text)
            status = rtn.json()
            if(status['isSuccess']):
                writeLog('success', time.strftime("%m-%d", time.localtime()))
                pushMsg(time.strftime("%m-%d %H:%M:%S", time.localtime()) + " 上报成功", 
                    "今日上报成功，上报时间为" + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + "\n" +
                    "上报用户名: " + self.usr, self.pushUrl, self.reader.get('Push', 'token'), self.reader.get('Push', 'template'))
                return True
            else:
                writeLog('fail', time.strftime("%m-%d", time.localtime()))
                pushMsg(time.strftime("%m-%d %H:%M:%S", time.localtime()) + " 上报失败", 
                    "今日上报失败，上报时间为" + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + "\n" +
                    "上报用户名: " + self.usr + "\n"
                    + "错误原因：辅导员已经审查", self.pushUrl, self.reader.get('Push', 'token'), self.reader.get('Push', 'template'))
                return False
        except:
            writeLog('fail', time.strftime("%m-%d", time.localtime()))
            pushMsg(time.strftime("%m-%d %H:%M:%S", time.localtime()) + " 上报失败", 
                    "今日上报失败，上报时间为" + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + "\n" +
                    "上报用户名: " + self.usr + "\n"
                    + "错误原因：" + status['msg'], self.pushUrl, self.reader.get('Push', 'token'), self.reader.get('Push', 'template'))
            return False


    


if __name__ == '__main__':
    
    reporter = WebsiteReporter()
    reporter.login_mrsb()

    '''
    if not WebsiteReporter.readState('log.txt', time.strftime("%m-%d", time.localtime())):
        reporter = WebsiteReporter()
        reporter.login_mrsb()
        reporter.report()
        '''