#!/usr/bin/python
#_*_coding:utf-8 _*_
import urllib,urllib2
import json
import sys
import simplejson
from myapp.etc import config

import os
reload(sys)
sys.setdefaultencoding('utf-8')

wechart_corpid = config.wechart_corpid
wechart_corpsecret= config.wechart_corpsecret
wechart_agentid=config.wechart_agentid



'''[[[url]]]]  https://work.weixin.qq.com/wework_admin/frame#contacts'''
def gettoken(corpid,corpsecret):
    gettoken_url = 'https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid=' + corpid + '&corpsecret=' + corpsecret
    #print gettoken_url
    try:
        token_file = urllib2.urlopen(gettoken_url)
    except urllib2.HTTPError as e:
        # print e.code
        # print e.read().decode("utf8")
        sys.exit()
    token_data = token_file.read().decode('utf-8')
    token_json = json.loads(token_data)
    token_json.keys()
    token = token_json['access_token']
    return token
def wxsenddata(user,subject,content):
    corpid =wechart_corpid
    #CorpID是企业号的标识
    corpsecret = wechart_corpsecret
    #corpsecretSecret是管理组凭证密钥
    accesstoken = gettoken(corpid,corpsecret)

    send_url = 'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=' + accesstoken
    users=user.split(',')
    for u in users:
        send_values = {
        "touser":u, #企业号中的用户帐号，在zabbix用户Media中配置，如果配置不正常，将按部门发送。
        #"toparty":"1", #企业号中的部门id。
        "msgtype":"text", #消息类型。
        "agentid":wechart_agentid, #企业号中的应用id。
        "text":{
        "content":subject + '\n' + content
        },"safe":"0"
        }
# send_data = json.dumps(send_values, ensure_ascii=False)
        send_data = simplejson.dumps(send_values, ensure_ascii=False).encode('utf-8')
        send_request = urllib2.Request(send_url, send_data)
        response = json.loads(urllib2.urlopen(send_request).read())
# if __name__ == '__main__':
#     wxsenddata('YueRenLiang', 'MYSQL test', 'sdfsfsdfsdfsdfd')
# #     user = str('YueRenLiang')
#     # zabbix传过来的第一个参数
#     subject = str('title')
#     #zabbix传过来的第二个参数
#     content = str('this is my first message11')
#     #zabbix传过来的第三个参数
#     senddata(user,subject,content)'''