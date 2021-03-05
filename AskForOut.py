from readConfig import ConfigReader
from Loginer import Loginer
from utils import readState, writeLog, pushMsg
import requests
import json
import time
from bs4 import BeautifulSoup
import datetime

class AskForOut(object):
    def __init__(self):
        self.reader = ConfigReader()
        self.usr = self.reader.get('DEFAULT', 'usr')
        self.passwd = self.reader.get('DEFAULT', 'passwd')
        self.loginer = Loginer(self.usr, self.passwd)
        self.session = requests.Session()
        self.session.headers = {
            'User-Agent': self.reader.get('Website', 'usr-agent'),
        }
        self.loginUrl = self.reader.get('Website', 'Login-url')
        self.pushUrl = self.reader.get('Push', 'pushUrl')
    
    def login_ask_for_out(self):
        result, self.session = self.loginer.login(self.session, self.loginUrl, 'xg.hit.edu.cn/zhxy-xgzs/xg_yqglxs/xsmrsb')
        return result
    
    def get_last_out_date(self):
        rtn = self.session.post(self.reader.get('AskForOut', 'outlistUrl'))
        rtn = json.loads(rtn.content)
        if rtn['isSuccess']:
            data = rtn['module']['data']
            for msg in data:
                date = msg['rq']
                if date != '':
                    date = datetime.datetime.strptime(date,'%Y-%m-%d').date()
                    return date
            
            date = datetime.date.today() 
            return date
        else:
            pushMsg(time.strftime("%m-%d %H:%M:%S", time.localtime()) + " 获取出校时间失败，无法申请", 
                        "获取出校时间失败，添加时间为" + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + "\n", self.pushUrl, self.reader.get('Push', 'token'), self.reader.get('Push', 'template'))
            return None

    def ask_for_nextday_out(self, date):
        rtn = self.session.get(self.reader.get('AskForOut', 'editUrl'))
        k = 1






if __name__ == "__main__":
    askForOut = AskForOut()
    askForOut.login_ask_for_out()
    date = askForOut.get_last_out_date()
    if date:
        askForOut.ask_for_nextday_out(date)




