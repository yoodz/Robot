# encoding: utf-8
"""
@author: xsren 
@contact: bestrenxs@gmail.com
@site: xsren.me

@version: 1.0
@license: Apache Licence
@file: wx_bot.py
@time: 2017/5/28 上午10:40

"""
from __future__ import unicode_literals

import platform
import re
import threading
import traceback

import itchat
import requests
from itchat.content import *

from libs import utils
from libs.alimama import Alimama

logger = utils.init_logger()

al = Alimama(logger)
al.login()


# 检查是否是淘宝链接
def check_if_is_tb_link(msg):
    if re.search(r'【.*】', msg['Text']) and (
                        u'打开👉手机淘宝👈' in msg['Text'] or u'打开👉天猫APP👈' in msg['Text'] or u'打开👉手淘👈' in msg['Text']):
        try:
            logger.debug(msg['Text'])
            q = re.search(r'【.*】', msg['Text']).group().replace(u'【', '').replace(u'】', '')
            if u'打开👉天猫APP👈' in msg['Text']:
                try:
                    url = re.search(r'http://.* \)', msg['Text']).group().replace(u' )', '')
                except:
                    url = None

            else:
                try:
                    url = re.search(r'http://.* ，', msg['Text']).group().replace(u' ，', '')
                except:
                    url = None
            if url is None:
                taokoulingurl = 'http://www.taokouling.com/index.php?m=api&a=taokoulingjm'
                taokouling = re.search(r'￥.*?￥', msg['Text']).group()
                parms = {'username': 'wx_tb_fanli', 'password': 'wx_tb_fanli', 'text': taokouling}
                res = requests.post(taokoulingurl, data=parms)
                url = res.json()['url'].replace('https://', 'http://')
                info = "tkl url: {}".format(url)
                logger.debug(info)


            replayMessage(url, msg)
        except Exception as e:
            trace = traceback.format_exc()
            logger.warning("error:{},trace:{}".format(str(e), trace))
            info = u'''%s
-----------------
该宝贝暂时没有找到内部返利通道！亲您可以换个宝贝试试，也可以联系我们群内管理员帮着寻找有返现的类似商品
            ''' % q
            itchat.send(info, msg['FromUserName'])
    elif re.search(r'http', msg['Text']):
        logger.debug("这是一条纯url的链接")
        logger.debug(msg['Text'])
        replayMessage(msg['Text'], msg)


def replayMessage(url, msg):
    try:
        real_url = al.get_real_url(url)
        info = "real_url: {}".format(real_url)
        logger.debug("找到真正的url")
        logger.debug(info)

        # get detail
        res = al.get_detail(real_url)
        auctionid = res['auctionId']
        coupon_amount = res['couponAmount']
        tk_rate = res['tkRate']
        price = res['zkPrice']
        logger.debug("这是返利的价钱")
        fx = (price - coupon_amount) * tk_rate / 100
        logger.debug(fx)
        logger.debug("这是res")
        logger.debug(res)
        q=res['title']

        # get tk link
        res1 = al.get_tk_link(auctionid)
        logger.debug("这是res1")
        logger.debug(res1)
        
        tao_token = res1['taoToken']
        short_link = res1['shortLinkUrl']
        coupon_link = res1['couponLinkTaoToken']

        if coupon_link != "":
            logger.debug("coupon_link")
            logger.debug(coupon_link)
            
            coupon_token = res1['couponLinkTaoToken']
            res_text = ''' 
%s
【返现】%.2f
【优惠券】%s元
请复制%s淘口令、打开淘宝APP下单
-----------------
【下单地址】%s
                    ''' % (q, fx, coupon_amount, coupon_token, short_link)
        else:
            res_text = '''
%s
【返现】%.2f元
【优惠券】%s元
请复制%s淘口令、打开淘宝APP下单
-----------------
【下单地址】%s
                                    ''' % (q, fx, coupon_amount, tao_token, short_link)
        itchat.send(res_text, msg['FromUserName'])
    except Exception as e:
        trace = traceback.format_exc()
        logger.warning("error:{},trace:{}".format(str(e), trace))
        info = u'''%s
-----------------
该宝贝暂时没有找到内部返利通道！亲您可以换个宝贝试试，也可以联系我们群内管理员帮着寻找有返现的类似商品
            ''' % q
        itchat.send(info, msg['FromUserName'])


class WxBot(object):
    @itchat.msg_register(itchat.content.TEXT)
    # @itchat.msg_register([TEXT])
    def text_reply(msg):
        logger.debug(msg)
        check_if_is_tb_link(msg)
        # msg.user.send('%s: %s' % (msg.type, msg['Text']))

    @itchat.msg_register(TEXT, isGroupChat=True)
    def text_reply(msg):
        check_if_is_tb_link(msg)
        # if msg.isAt:
        #     msg.user.send(u'@%s\u2005I received: %s' % (
        #         msg.actualNickName, msg['Text']))

    def run(self):
        #获取操作系统的类型
        sysstr = platform.system()
        if (sysstr == "Linux") or (sysstr == "Darwin"):
            itchat.auto_login(enableCmdQR=2, hotReload=True)
        else:
            itchat.auto_login(hotReload=True)
        itchat.run(True)


if __name__ == '__main__':
    mi = WxBot()
    t = threading.Thread(target=mi.run, args=())
    t.start()
