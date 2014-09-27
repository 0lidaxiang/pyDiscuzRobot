#!/usr/bin/env python2.7
# coding: utf-8
# author: sandtears
# e-mail: me@sandtears.com

import requests
import logging
import time
from lxml import html


FORMAT = '[%(levelname)s] %(message)s'
logging.basicConfig(format=FORMAT, level=logging.INFO)


class LoginError(BaseException):
    pass


class DiscuzRobot:
    def __init__(self, forum_url, username, password, proxy=None):
        '''Init DiscuzRobot with username, password and proxy(optional)'''
        # Add 'http://' and '/' if needed.
        self.forum_url = forum_url if forum_url.endswith('/') else (forum_url + '/')
        self.forum_url = self.forum_url if self.forum_url.startswith('http') else ('http://' + self.forum_url)

        self.username = username
        self.password = password

        self.isLogin = False
        self.formhash = ''
        self.session = requests.session()
        self.proxies = {}
        if proxy:
            self.proxies['http'] = proxy
            self.proxies['https'] = proxy

    def login(self):
        '''login and get forum'''
        login_url = self.forum_url + "member.php?mod=logging&action=login&loginsubmit=yes&infloat=yes&inajax=1"
        login_data = {
            'username': self.username,
            'password': self.password,
            'answer': '',
            'cookietime': '2592000',
            'handlekey': 'ls',
            'questionid': '0',
            'quickforward': 'yes',
            'fastloginfield': 'username'
        }
        resp = self.session.post(login_url, login_data)
        if self.username in resp.content:
            logging.info('%s - login succeed' % self.username)
            self.isLogin = True
            self.get_formhash()
        else:
            logging.warning('%s - login failed' % self.username)
            raise LoginError, "Wrong username or password."

    def get_formhash(self):
        '''get the formhash to verify'''
        forum_url = self.forum_url + 'forum.php'
        resp = self.session.get(forum_url)
        formhash_xpath = '//*[@id="scbar_form"]/input[@name="formhash"]'
        doc = html.document_fromstring(resp.content)
        formhash_input = doc.xpath(formhash_xpath)
        if formhash_xpath:
            self.formhash = formhash_input[0].get('value')
        else:
            logging.warning('%s - cant find formhash' % self.username)
            raise LoginError, "Cant find formhash."

    def reply(self, fid, tid, subject, message):
        '''reply a subject'''
        reply_url = self.forum_url + 'forum.php?mod=post&action=reply&fid=' + str(fid) + '&tid=' + str(tid) + \
                    '&extra=page%3D1&replysubmit=yes&infloat=yes&handlekey=fastpost&inajax=1'
        reply_data = {
            'formhash': self.formhash,
            'message': message,
            'subject': subject,
            'posttime': int(time.time())
        }
        resp = self.session.post(reply_url, reply_data)
        resp.encoding = 'utf8'
        # print content
        if u'发布成功' in resp.text:
            logging.info('%s - reply succeed' % self.username)
        else:
            logging.warning('%s - reply failed' % self.username)

    def publish(self, fid, subject, message):
        '''publish a subject'''
        publish_url = self.forum_url + 'forum.php?mod=post&action=newthread&fid='+ str(fid) +'&extra=&topicsubmit=yes'
        publish_data = {
            'formhash': self.formhash,
            'message': message,
            'subject': subject,
            'posttime': int(time.time()),
            'addfeed':'1',
            'allownoticeauthor':'1',
            'checkbox':'0',
            'newalbum':'',
            'readperm':'',
            'rewardfloor':'',
            'rushreplyfrom':'',
            'rushreplyto':'',
            'save':'',
            'stopfloor':'',
            #'typeid':typeid,
            'uploadalbum':'',
            'usesig':'1',
            'wysiwyg':'0'
        }
        resp = self.session.post(publish_url, publish_data)
        resp.encoding = 'utf8'
        if subject.decode('utf8') in resp.text:
            logging.info('%s - publish succeed' % self.username)
        else:
            logging.warning('%s - publish failed' % self.username)
            print resp.text