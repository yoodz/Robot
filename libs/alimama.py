# encoding: utf-8
"""
@author: xsren 
@contact: bestrenxs@gmail.com
@site: xsren.me

@version: 1.0
@license: Apache Licence
@file: alimama.py
@time: 2017/5/27 下午9:55

"""
import json
import os.path
import platform
import re
import sys
import time
import traceback

if sys.version_info[0] < 3:
    import urllib
else:
    import urllib.parse as urllib
    
from io import BytesIO
from threading import Thread

import pyqrcode
import requests

from PIL import Image

sysstr = platform.system()
if (sysstr == "Linux") or (sysstr == "Darwin"):
    pass
cookie_fname = 'cookies.txt'


class Alimama:
    def __init__(self, logger):
        self.se = requests.session()
        self.load_cookies()
        self.myip = "127.0.0.1"
        self.start_keep_cookie_thread()
        self.logger = logger

    # 启动一个线程，定时访问淘宝联盟主页，防止cookie失效
    def start_keep_cookie_thread(self):
        t = Thread(target=self.visit_main_url, args=())
        t.setDaemon(True)
        t.start()

    def visit_main_url(self):
        url = "https://pub.alimama.com/"
        headers = {
            'method': 'GET',
            'authority': 'pub.alimama.com',
            'scheme': 'https',
            'path': '/common/getUnionPubContextInfo.json',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
            'Referer': 'http://pub.alimama.com/',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'zh,en-US;q=0.8,en;q=0.6,zh-CN;q=0.4,zh-TW;q=0.2',
        }
        while True:
            time.sleep(60000 * 5)
            try:
                self.logger.debug(
                    "visit_main_url......,time:{}".format(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
                self.get_url(url, headers)
                self.logger.debug(self.check_login())
                real_url = "https://detail.tmall.com/item.htm?id=42485910384"
                res = self.get_detail(real_url)
                auctionid = res['auctionId']
                self.logger.debug(self.get_tk_link(auctionid))
            except Exception as e:
                trace = traceback.format_exc()
                self.logger.warning("error:{},trace:{}".format(str(e), trace))

    def get_url(self, url, headers):
        res = self.se.get(url, headers=headers)
        return res

    def post_url(self, url, headers, data):
        res = self.se.post(url, headers=headers, data=data)
        return res

    def load_cookies(self):
        if os.path.isfile(cookie_fname):
            with open(cookie_fname, 'r') as f:
                c_str = f.read().strip()
                self.set_cookies(c_str)

    def set_cookies(self, c_str):
        try:
            cookies = json.loads(c_str)
        except:
            return
        for c in cookies:
            self.se.cookies.set(c[0], c[1])

    # check login
    def check_login(self):
        self.logger.debug('checking login status.....')
        url = 'https://pub.alimama.com/common/getUnionPubContextInfo.json'
        headers = {
            'method': 'GET',
            'authority': 'pub.alimama.com',
            'scheme': 'https',
            'path': '/common/getUnionPubContextInfo.json',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
            'Referer': 'http://pub.alimama.com/',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'zh,en-US;q=0.8,en;q=0.6,zh-CN;q=0.4,zh-TW;q=0.2',
        }

        res = self.get_url(url, headers=headers)
        rj = json.loads(res.text)
        return rj

    def visit_login_rediret_url(self, url):
        headers = {
            'method': 'GET',
            'authority': 'login.taobao.com',
            'scheme': 'https',
            'path': '/member/loginByIm.do?%s' % url.split('loginByIm.do?')[-1],
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
            'Referer': 'http://pub.alimama.com/',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'zh,en-US;q=0.8,en;q=0.6,zh-CN;q=0.4,zh-TW;q=0.2',
        }
        res = self.get_url(url, headers=headers)
        self.logger.debug(res.status_code)

    def get_scan_qr_status(self, lg_token):
        defaulturl = 'http://login.taobao.com/member/taobaoke/login.htm?is_login=1'
        url = 'https://qrlogin.taobao.com/qrcodelogin/qrcodeLoginCheck.do?lgToken=%s&defaulturl=%s&_ksTS=%s_30&callback=jsonp31' % (
            lg_token, defaulturl, int(time.time() * 1000))
        headers = {
            'method': 'GET',
            'authority': 'qrlogin.taobao.com',
            'scheme': 'https',
            'path': '/qrcodelogin/qrcodeLoginCheck.do?%s' % url.split('qrcodeLoginCheck.do?')[-1],
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
            'accept': '*/*',
            'referer': 'https://login.taobao.com/member/login.jhtml?style=mini&newMini2=true&from=alimama&redirectURL=http%3A%2F%2Flogin.taobao.com%2Fmember%2Ftaobaoke%2Flogin.htm%3Fis_login%3d1&full_redirect=true&disableQuickLogin=true',
            'accept-encoding': 'gzip, deflate, sdch, br',
            'accept-language': 'zh,en-US;q=0.8,en;q=0.6,zh-CN;q=0.4,zh-TW;q=0.2',
        }
        res = self.get_url(url, headers=headers)
        rj = json.loads(res.text.replace('(function(){jsonp31(', '').replace(');})();', ''))
        return rj

    def show_qr_image(self):
        self.logger.debug('begin to show qr image')
        url = 'https://qrlogin.taobao.com/qrcodelogin/generateQRCode4Login.do?from=alimama&_ksTS=%s_30&callback=jsonp31' % int(
            time.time() * 1000)

        # get qr image
        headers = {
            'method': 'GET',
            'authority': 'qrlogin.taobao.com',
            'scheme': 'https',
            'path': '/qrcodelogin/generateQRCode4Login.do?%s' % url.split('generateQRCode4Login.do?')[-1],
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
            'accept': '*/*',
            'referer': 'https://login.taobao.com/member/login.jhtml?style=mini&newMini2=true&from=alimama&redirectURL=http%3A%2F%2Flogin.taobao.com%2Fmember%2Ftaobaoke%2Flogin.htm%3Fis_login%3d1&full_redirect=true&disableQuickLogin=true',
            'accept-encoding': 'gzip, deflate, sdch, br',
            'accept-language': 'zh-CN,zh;q=0.8',
        }

        res = self.get_url(url, headers=headers)
        rj = json.loads(res.text.replace('(function(){jsonp31(', '').replace(');})();', ''))
        lg_token = rj['lgToken']
        url = 'https:%s' % rj['url']

        headers = {
            'method': 'GET',
            'authority': 'img.alicdn.com',
            'scheme': 'https',
            'path': '/tfscom/%s' % url.split('tfscom/')[-1],
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
            'accept': 'image/webp,image/*,*/*;q=0.8',
            'referer': 'https://login.taobao.com/member/login.jhtml?style=mini&newMini2=true&from=alimama&redirectURL=http%3A%2F%2Flogin.taobao.com%2Fmember%2Ftaobaoke%2Flogin.htm%3Fis_login%3d1&full_redirect=true&disableQuickLogin=true',
            'accept-encoding': 'gzip, deflate, sdch, br',
            'accept-language': 'zh,en-US;q=0.8,en;q=0.6,zh-CN;q=0.4,zh-TW;q=0.2',
        }
        res = self.get_url(url, headers=headers)
        qrimg = BytesIO(res.content)

        sysstr = platform.system()
        if (sysstr == "Windows"):
            # windows下可能无法打印请用下列代码
            img = Image.open(qrimg)
            img.show()
        elif (sysstr == "Linux") or (sysstr == "Darwin"):
            # 读取url
            import zbarlight
            img = Image.open(qrimg)
            codes = zbarlight.scan_codes('qrcode', img)
            qr_url = codes[0]
            # 使用pyqrcode在终端打印，只在linux下可以用
            pyqrcode_url = pyqrcode.create(qr_url)
            print (pyqrcode_url.terminal())

        self.logger.debug(u"请使用淘宝客户端扫码")
        return lg_token

    # do login
    def do_login(self):
        self.logger.debug('begin to login')
        # show qr image
        lg_token = self.show_qr_image()
        t0 = time.time()
        while True:
            rj = self.get_scan_qr_status(lg_token)
            # 扫码成功会有跳转
            if 'url' in rj:
                self.visit_login_rediret_url(rj['url'])
                self.logger.debug('login success')
                self.logger.debug(self.se.cookies.items())
                with open(cookie_fname, 'w') as f:
                    f.write(json.dumps(self.se.cookies.items()))
                return 'login success'
            # 二维码过一段时间会失效
            if time.time() - t0 > 60 * 5:
                self.logger.debug('scan timeout')
                return
            time.sleep(0.5)

    def login(self):
        try:
            clr = self.check_login()
            self.myip = clr['data']['ip']
            dlr = self.do_login()
            if dlr is None:
                return 'login failed'
            else:
                return 'login success'
            # if 'mmNick' in clr['data']:
            #     self.logger.debug(u"淘宝已经登录 不需要再次登录")
            #     return 'login success'
            # else:
            #     dlr = self.do_login()
            #     if dlr is None:
            #         return 'login failed'
            #     else:
            #         return 'login success'
        except Exception as e:
            trace = traceback.format_exc()
            self.logger.warning("{},{}".format(str(e), trace))
            return 'login failed'

    def get_tb_token(self):
        tb_token = None
        for c in self.se.cookies.items():
            if c[0] == '_tb_token_':
                return c[1]
        if tb_token is None:
            return 'test'

    # 获取商品详情
    def get_detail(self, q):
        try:
            t = int(time.time() * 1000)
            tb_token = self.se.cookies.get('_tb_token_', domain="pub.alimama.com")
            pvid = '10_%s_1686_%s' % (self.myip, t)
            url = 'http://pub.alimama.com/items/search.json?q=%s&_t=%s&auctionTag=&perPageSize=40&shopTag=&t=%s&_tb_token_=%s&pvid=%s' % (
                urllib.quote(q.encode('utf8')), t, t, tb_token, pvid)
            headers = {
                'method': 'GET',
                'authority': 'pub.alimama.com',
                'scheme': 'https',
                'path': '/items/search.json?%s' % url.split('search.json?')[-1],
                'accept': 'application/json, text/javascript, */*; q=0.01',
                'x-requested-with': 'XMLHttpRequest',
                'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
                'referer': 'https://pub.alimama.com',
                'accept-encoding': 'gzip, deflate, sdch, br',
                'accept-language': 'zh,en-US;q=0.8,en;q=0.6,zh-CN;q=0.4,zh-TW;q=0.2',
            }
            res = self.get_url(url, headers)
            rj = res.json()
            if len(rj['data']['pageList']) > 0:
                return rj['data']['pageList'][0]
            else:
                return 'no match item'
        except Exception as e:
            trace = traceback.format_exc()
            self.logger.warning("error:{},trace:{}".format(str(e), trace))

    # 获取淘宝客链接
    def get_tk_link(self, auctionid):
        t = int(time.time() * 1000)
        tb_token = self.se.cookies.get('_tb_token_', domain="pub.alimama.com")
        pvid = '10_%s_1686_%s' % (self.myip, t)
        try:
            gcid, siteid, adzoneid = self.__get_tk_link_s1(auctionid, tb_token, pvid)
            self.__get_tk_link_s2(gcid, siteid, adzoneid, auctionid, tb_token, pvid)
            res = self.__get_tk_link_s3(auctionid, adzoneid, siteid, tb_token, pvid)
            return res
        except Exception as e:
            trace = traceback.format_exc()
            self.logger.warning("error:{},trace:{}".format(str(e), trace))

    # 第一步，获取推广位相关信息
    def __get_tk_link_s1(self, auctionid, tb_token, pvid):
        url = 'http://pub.alimama.com/common/adzone/newSelfAdzone2.json?tag=29&itemId=%s&blockId=&t=%s&_tb_token_=%s&pvid=%s' % (
            auctionid, int(time.time() * 1000), tb_token, pvid)
        headers = {
            'Host': 'pub.alimama.com',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
            'Referer': 'http://pub.alimama.com/promo/search/index.htm',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'zh,en-US;q=0.8,en;q=0.6,zh-CN;q=0.4,zh-TW;q=0.2',
        }
        res = self.get_url(url, headers)
        self.logger.debug(res.text)
        rj = res.json()
        gcid = rj['data']['otherList'][0]['gcid']
        siteid = rj['data']['otherList'][0]['siteid']
        adzoneid = rj['data']['otherAdzones'][0]['sub'][0]['id']
        return gcid, siteid, adzoneid

    # post数据
    def __get_tk_link_s2(self, gcid, siteid, adzoneid, auctionid, tb_token, pvid):
        url = 'http://pub.alimama.com/common/adzone/selfAdzoneCreate.json'
        data = {
            'tag': '29',
            'gcid': gcid,
            'siteid': siteid,
            'selectact': 'sel',
            'adzoneid': adzoneid,
            't': int(time.time() * 1000),
            '_tb_token_': tb_token,
            'pvid': pvid,
        }
        headers = {
            'Host': 'pub.alimama.com',
            'Content-Length': str(len(json.dumps(data))),
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Origin': 'http://pub.alimama.com',
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Referer': 'http://pub.alimama.com/promo/search/index.htm',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh,en-US;q=0.8,en;q=0.6,zh-CN;q=0.4,zh-TW;q=0.2',
        }

        res = self.post_url(url, headers, data)
        return res

    # 获取口令
    def __get_tk_link_s3(self, auctionid, adzoneid, siteid, tb_token, pvid):
        url = 'http://pub.alimama.com/common/code/getAuctionCode.json?auctionid=%s&adzoneid=%s&siteid=%s&scenes=1&t=%s&_tb_token_=%s&pvid=%s' % (
            auctionid, adzoneid, siteid, int(time.time() * 1000), tb_token, pvid)
        headers = {
            'Host': 'pub.alimama.com',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'X-Requested-With': 'XMLHttpRequest',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
            'Referer': 'http://pub.alimama.com/promo/search/index.htm',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'zh,en-US;q=0.8,en;q=0.6,zh-CN;q=0.4,zh-TW;q=0.2',
        }
        res = self.get_url(url, headers)
        rj = json.loads(res.text)
        return rj['data']

    def get_real_url(self, url):
        # return "https://detail.tmall.com/item.htm?id=548726815314"
        try:
            headers = {
                'Host': url.split('http://')[-1].split('/')[0],
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Encoding': 'gzip, deflate, sdch',
                'Accept-Language': 'zh,en-US;q=0.8,en;q=0.6,zh-CN;q=0.4,zh-TW;q=0.2',
            }
            res = self.get_url(url, headers)
            if re.search(r'itemId\":\d+', res.text):
                item_id = re.search(r'itemId\":\d+', res.text).group().replace('itemId":', '').replace('https://', 'http://')
                r_url = "https://detail.tmall.com/item.htm?id=%s" % item_id
            elif re.search(r"var url = '.*';", res.text):
                r_url = re.search(r"var url = '.*';", res.text).group().replace("var url = '", "").replace("';",
                                                                                                           "").replace(
                    'https://', 'http://')
            else:
                r_url = res.url
            if 's.click.taobao.com' in r_url:
                r_url = self.handle_click_type_url(r_url)
            else:
                while ('detail.tmall.com' not in r_url) and ('item.taobao.com' not in r_url) and (
                            'detail.m.tmall.com' not in r_url):
                    headers1 = {
                        'Host': r_url.split('http://')[-1].split('/')[0],
                        'Upgrade-Insecure-Requests': '1',
                        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
                        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                        'Accept-Encoding': 'gzip, deflate, sdch',
                        'Accept-Language': 'zh,en-US;q=0.8,en;q=0.6,zh-CN;q=0.4,zh-TW;q=0.2',
                    }
                    res2 = self.get_url(r_url, headers1)
                    self.logger.debug("{},{},{}".format(res2.url, res2.status_code, res2.history))
                    r_url = res2.url

            self.logger.debug(r_url)
            return r_url
        except Exception as e:
            self.logger.warning(str(e))
            return url

    def handle_click_type_url(self, url):
        # step 1
        headers = {
            'method': 'GET',
            'authority': 's.click.taobao.com',
            'scheme': 'https',
            'path': '/t?%s' % url.split('/t?')[-1],
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'zh,en-US;q=0.8,en;q=0.6,zh-CN;q=0.4,zh-TW;q=0.2',
        }
        res = self.get_url(url, headers)
        self.logger.debug("{},{},{}".format(res.url, res.status_code, res.history))
        url2 = res.url

        # step 2
        headers2 = {
            'referer': url,
            'method': 'GET',
            'authority': 's.click.taobao.com',
            'scheme': 'https',
            'path': '/t?%s' % url2.split('/t?')[-1],
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'zh,en-US;q=0.8,en;q=0.6,zh-CN;q=0.4,zh-TW;q=0.2',
        }
        res2 = self.get_url(url2, headers2)
        self.logger.debug("{},{},{}".format(res2.url, res2.status_code, res2.history))
        url3 = urllib.unquote(res2.url.split('t_js?tu=')[-1])

        # step 3
        headers3 = {
            'referer': url2,
            'method': 'GET',
            'authority': 's.click.taobao.com',
            'scheme': 'https',
            'path': '/t?%s' % url3.split('/t?')[-1],
            'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'zh,en-US;q=0.8,en;q=0.6,zh-CN;q=0.4,zh-TW;q=0.2',
        }
        res3 = self.get_url(url3, headers3)
        self.logger.debug("{},{},{}".format(res3.url, res3.status_code, res3.history))
        r_url = res3.url

        return r_url


if __name__ == '__main__':
    al = Alimama()
    # al.login()
    # q = u'现货 RS版 树莓派3代B型 Raspberry Pi 3B 板载wifi和蓝牙'
    # q = u'蔻斯汀玫瑰身体护理套装沐浴露身体乳爽肤水滋润全身保湿补水正品'
    # q = u'DIY个性定制T恤 定做工作服短袖 男女夏季纯棉广告文化衫Polo印制'
    q = u'防晒衣女2017女装夏装新款印花沙滩防晒服薄中长款大码白色短外套'
    # res = al.get_detail(q)
    # auctionid = res['auctionId']
    # al.get_tk_link(auctionid)
    # url = 'http://c.b1wt.com/h.SQwr1X?cv=kzU8ZvbiEa8&sm=796feb'
    # al.get_real_url(url)
    # url = 'http://c.b1wt.com/h.S9fQZb?cv=zcNtZvbH4ak&sm=79e4be'
    # al.get_real_url(url)
    # url = 'http://c.b1wt.com/h.S9gdyy?cv=RW5EZvbuYBw&sm=231894'
    # al.get_real_url(url)
    # url = 'http://c.b1wt.com/h.S8ppn7?cv=ObUrZvZ3oH9&sm=1b02f8'
    # al.get_real_url(url)
    # url = 'http://c.b1wt.com/h.SQ70kv?cv=L5HpZv0w4hJ'
    # url = 'http://c.b1wt.com/h.S9A0pK?cv=8grnZvYkU14&sm=efb5b7'
    url = 'http://zmnxbc.com/s/nlO3j?tm=95b078'
    al.get_real_url(url)
