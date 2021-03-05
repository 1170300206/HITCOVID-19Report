import os
import json
import requests

def readState(filename, time):
    with open(os.path.join(os.path.dirname(__file__), filename), "r", encoding="utf-8") as f:
        logs = f.readlines()
        if len(logs) > 0 and len(logs[-1].strip()) > 0:
            time1, state = logs[-1].split("\t")
            if time1 == time and state.startswith('success'):
                return True
        return False


def writeLog(flag, time, filename ='log.txt'):
    with open(os.path.join(os.path.dirname(__file__), filename), "a+", encoding="utf-8") as f:
        f.write(time + "\t" + flag + "\n")


def pushMsg(title, msg, push_rul, push_token, push_template = 'html'):
    if push_rul is not "":
        requests.post(push_rul, headers={'Content-Type': 'application/json'}, data=json.dumps({
            'token': push_token, "title": title, 'content': msg, 'template': push_template}).encode("utf-8"))