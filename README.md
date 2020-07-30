# HITCOVID-19Report
Harbin Institute of Technology's COVID-19 daily report

哈尔滨工业大学2020每日自动上报

## Dependencies

Python 3

pycryptodome

beautifulsoup4

readconfig

configparser

## v1.0

通过xg.hit.edu.cn进行每日上报，暂时没有实现验证码识别

## How to use

### 直接运行

通过pip安装必须的依赖：

```shell
pip install -r requirements.txt
```

在config.txt中，填写自己的学号和密码，直接运行Websitereporter.py即可完成上报，上报的时间段在6:00 - 20:00之间

### linux下定时运行

通过pip安装必须的依赖

```shell
pip install -r requirements.txt
```

在config.txt中，填写自己的学号和密码，如果需要通过微信进行推送登录是否成功的消息，请通过<a href="http://pushplus.hxtrip.com/">pushplus</a>得到token，填写到config.txt中的token字段，其会将每次运行的状况通过微信发送

设置文件的读写权限

```shell
chmod +x run.sh
chmod 744 WebsiteReporter.py
```

由于文件在windows下编写，因此run.sh会产生编码错误，请使用vim打开run.sh

```shell
vi run.sh
```

在vim中运行set ff=unix来进行编码的转换

使用crontab进行定时运行，程序通过检查log.txt中的内容来判断是否再次签到。

首先对cronotab的定时任务进行编辑

```shell
crontab -e
```

在打开的内容中添加如下定时任务，其会在每天8-18点间每半个小时执行一次脚本，当log.txt中有当天的执行成功记录，则不会再运行。

```shell
0,30 8-18 * * * yourpath/HITCOVID-19Report/run.sh
```

以下是crontab的一些常用命令

```shell
crontab -l # 列出当前的任务
tail -f /var/log/cron # 列出crontab的执行记录
```

需要保证crontab已经运行，crontab的运行可以查阅<a href="https://www.cnblogs.com/ftl1012/p/crontab.html">这里</a>