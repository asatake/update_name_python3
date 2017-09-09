#!/usr/bin/python
# ! -*- coding: utf-8 -*-
__author__ = 'asatake'

from twitter import Twitter, OAuth, TwitterStream
from logging import basicConfig, getLogger, FileHandler, Formatter, DEBUG, ERROR
import configparser
import os
import re


class UpdateName:
    def __init__(self):
        # config.iniを読み込み. consumer_keyなどを取得
        self.config = configparser.ConfigParser()
        self.config.read(
            os.path.join(os.path.dirname(__file__), '../config/config.ini'))
        self.oauth_config = self.config['oauth']

        # loggingの設定
        self.debug_logger = getLogger(__name__)
        if not self.debug_logger.handlers:
            debugFileHandler = FileHandler(r'log/debug.log')
            debugFileHandler.setLevel(DEBUG)
            debugFormatter = Formatter('%(asctime)s %(message)s')
            debugFileHandler.setFormatter(debugFormatter)
            self.debug_logger.setLevel(DEBUG)
            self.debug_logger.addHandler(debugFileHandler)

        self.error_logger = getLogger(__name__)
        if not self.error_logger.handlers:
            errorFileHandler = FileHandler(r'log/error.log')
            errorFileHandler.setLevel(ERROR)
            errorFormatter = Formatter('%(asctime)s:%(lineno)d %(message)s')
            errorFileHandler.setFormatter(errorFormatter)
            self.error_logger.setLevel(ERROR)
            self.error_logger.addHandler(errorFileHandler)

        # userstream用に作成.
        self.oauth = OAuth(
            consumer_key=self.oauth_config['consumer'],
            consumer_secret=self.oauth_config['consumer_secret'],
            token=self.oauth_config['token'],
            token_secret=self.oauth_config['token_secret']
        )

        # ツイートやらプロフィールを取ってくるため作成
        self.tw = Twitter(
            auth=OAuth(
                self.oauth_config['token'],
                self.oauth_config['token_secret'],
                self.oauth_config['consumer'],
                self.oauth_config['consumer_secret'])
        )

        # screen_nameを記憶
        self.my_name = self.tw.account.settings()['screen_name']

    # &などhtml特殊文字は置き換える
    # リプライの文頭にある自分のscreen_nameも消す
    def replace_special(self, sentence):
        sentence = sentence.replace('&amp;', '&')
        sentence = sentence.replace('&amp;', '&')
        sentence = sentence.replace('&lt;', '＜')
        sentence = sentence.replace('&gt;', '＞')
        pat = re.compile(r'^@{0}+\s+'.format(self.my_name))
        sentence = re.sub(pat, '', sentence)
        return sentence

    # ツイートのテキストから名前を新しい名前を抽出
    def get_new_name(self, current):
        new_name = self.replace_special(current)
        # @[screen_name]になってなかったら処理しない
        # あとは新しい名前の部分を取り出すだけ
        if re.findall(r'^@(?!{0})'.format(self.my_name), new_name):
            return
        elif re.findall(
                r'.*[\(（]+[\s]*@{0}+\s*[\)）]+\s*$'.format(self.my_name),
                new_name):
            new_name = re.sub(
                r'[\(（]+[\s]*@{0}+[\s]*[\)）]+\s*$'.format(self.my_name),
                '',
                new_name)
        return new_name

    # update_nameのトリガーになったツイートのURLを取得
    def get_tweet_url(self, screen_name, t_id):
        url = "https://twitter.com/" + \
              screen_name + "/status/" + "{0}".format(t_id)
        return url

    # 名前を更新してツイート
    def update_name(self, new_name, url):
        current_name = self.tw.account.verify_credentials()['name']
        # update_nameする
        update_name_tweets = new_name + ' になりました。\n' + url

        if len(new_name) > 0 \
           and len(new_name) <= 20:
            self.tw.account.update_profile(name=new_name)
            self.tw.statuses.update(status=update_name_tweets)
            self.debug_logger.debug('{0} => {1}'.format(current_name, new_name))
            self.debug_logger.debug(update_name_tweets)
            # print(update_name_tweets)

    # 主処理
    def main(self):
        # user stream取得
        tw_us = TwitterStream(auth=self.oauth, domain='userstream.twitter.com')
        for msg in tw_us.user():
            if 'text' in msg:
                text = msg['text']
                text = text.replace('　', ' ')

                screen_name = msg['user']['screen_name']
                t_id = msg['id']
                url = self.get_tweet_url(screen_name, t_id)

                try:
                    if text.startswith('RT '):
                        continue
                    elif re.findall(
                            r'^@(?!{0})'.format(self.my_name),
                            text):
                        continue
                    elif re.findall(
                            r'.*[\(（][\s]*@{0}[\s]*[\)）]\s*$'.format(
                                self.my_name),
                            text):
                        new_name = self.get_new_name(text)
                        self.update_name(new_name, url)

                except Exception as e:
                    self.error_logger.error(e.args)
                    continue
