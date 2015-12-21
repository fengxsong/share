#!/usr/bin/env python3
# coding:utf-8
#2014-06-26

import re, urllib.parse, urllib.request, http.cookiejar, time


class NoExceptionCookieProcesser(urllib.request.HTTPCookieProcessor):
    def http_error_403(self, req, fp, code, msg, hdrs):
        return fp

    def http_error_400(self, req, fp, code, msg, hdrs):
        return fp

    def http_error_500(self, req, fp, code, msg, hdrs):
        return fp

#封装另外一个request.HTTPCookieProcessor类，使用默认类会直接403错误

cj = http.cookiejar.LWPCookieJar()
cookie_support = NoExceptionCookieProcesser(cj)
opener = urllib.request.build_opener(cookie_support, urllib.request.HTTPHandler)
urllib.request.install_opener(opener)
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Connection': 'keep-alive',
    'Host': 'www.smzdm.com'
}


def postData(url, data):
    data = urllib.parse.urlencode(data).encode('utf-8')
    request = urllib.request.Request(url, data, headers)
    response = urllib.request.urlopen(request)
    text = response.read().decode('utf-8')
    return text


def getData(url):
    request = urllib.request.Request(url)
    request.add_header('User-Agent',
                       'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36')
    request.add_header('Accept', 'text/html, application/xhtml+xml, */*')
    request.add_header('Referer', 'http://www.smzdm.com/user/')
    request.add_header('Host', 'www.smzdm.com')
    response = urllib.request.urlopen(request)
    text = response.read().decode('utf-8')
    return text


def postComment(referer, content):
    param = {
        'type': 'comment_show',
        'pid': 51693,
        'parentid': 0,
        'content': content
    }  #pid:url最后的数字;type:晒物广场=comment_show,优惠=comment_post,content=留言内容
    data = urllib.parse.urlencode(param).encode('utf-8')
    request = urllib.request.Request('http://show.smzdm.com/ajax_set_comment', data, headers, method='POST')
    request.add_header('Referer', referer)
    request.add_header('X-Requested-With', 'XMLHttpRequest')
    response = urllib.request.urlopen(request)
    text = response.read().decode('utf-8')
    return text


if __name__ == '__main__':
    #smzdm的登陆过程不是使用的post而是jquery
    #登陆时抓包得到http://www.smzdm.com/user/login/jsonp_check?后边的数据
    query_param = {
        'callback': 'jQuery数字_数字',
        'user_login': '用户',
        'user_pass': '加密密码',
        'rememberme': '0',
        'is_third': '',
        'is_pop': '1',
        'captcha': '',
        '_': '数字'
    }
    #从点击签到按钮抓包分析get http://www.smzdm.com/user/qiandao/jsonp_checkin?的一段url得到签到所需要的data
    query_qiandao = {
        'callback': 'jQuery数字_数字',
        '_': '数字'
    }
    login = postData('http://www.smzdm.com/user/login/jsonp_check', query_param)
    userinfo = getData('http://www.smzdm.com/user/')
    qiandao = postData('http://www.smzdm.com/user/qiandao/jsonp_checkin', query_qiandao)
    #脚本又被值得买和谐掉了……
