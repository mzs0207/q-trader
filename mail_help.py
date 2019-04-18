#!/usr/bin/python
# coding:utf8
#
#  send message
#
#
import logging

import requests


def send_message(sub, text):
    """

    :param sub:
    :param text:
    :return:
    """
    url = u'https://sc.ftqq.com/SCU46932T92bd3bdc7a2185213d1731d0795a17ca5c94a4595f7b9.send?text={0}&desp={1}'.format(
        sub, text
    )
    try:
        resp = requests.get(url)
        print resp.text
    except Exception as ee:
        logging.exception(ee)
        print ee


if __name__ == '__main__':
    send_message(u'new trader', u'new trader')
