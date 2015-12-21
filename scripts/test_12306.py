#!/usr/bin/env python
# -*- coding: utf-8 -*-

import arrow
from time import sleep
from splinter.browser import Browser

init_url = "https://kyfw.12306.cn/otn/leftTicket/init"
initMy12306_url = "https://kyfw.12306.cn/otn/index/initMy12306"
login_url = "https://kyfw.12306.cn/otn/login/init"

SZ = '%u6DF1%u5733%2CSZQ',
GZ = '%u5E7F%u5DDE%2CGZQ'

from_station = GZ
to_station = '%u666E%u5B81%2CPEQ'
datetime = arrow.now().replace(days=+59).format('YYYY-MM-DD')
username = ""
password = ""
passengers = [u'冯旭松', ]

auth = {
    "loginUserDTO.user_name": username,
    "userDTO.password": password
}


def test_12306():
    client = Browser(driver_name='chrome')
    client.visit(init_url)
    while client.is_element_present_by_id('login_user'):
        client.find_by_id('login_user').click()
        client.fill_form(auth)
        print "Select captcha!"
        sleep(8)
        if client.url == initMy12306_url:
            break
    print "Start!"

    try:
        client.visit(init_url)
        client.cookies.add({'_jc_save_fromDate': datetime,
                            '_jc_save_fromStation': from_station,
                            '_jc_save_toStation': to_station})
        client.reload()
        while client.url == init_url:
            client.find_by_id('query_ticket').click()
            if client.find_by_text(u'预订'):
                for url in client.find_by_text(u'预订'):
                    url.click()
                    sleep(0.5)
                    for passenger in passengers:
                        client.find_by_text(passenger)[-1].click()
                    print "Select captcha!"
                    sleep(10)
    except Exception as e:
        print e

if __name__ == "__main__":
    test_12306()
