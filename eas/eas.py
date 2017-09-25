"""
XDU education administration system helper

provide auto-evaluate-teaching and report download

created at 2017-04 by broholens
"""

import time
import logging
from collections import defaultdict

import pandas as pd
from selenium import webdriver
from lxml import etree

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s'
)


class AutoEAS:

    logger = logging.getLogger(__name__)

    def __init__(self, username, password):
        self.host = 'http://jwxt.xidian.edu.cn/'
        self.login_url = 'http://ids.xidian.edu.cn/authserver/login?service=http%3A%2F%2Fjwxt.xidian.edu.cn%2Fcaslogin.jsp'
        self.evaluate_url = 'http://jwxt.xidian.edu.cn/jxpgXsAction.do?oper=listWj'
        self.report_url = 'http://jwxt.xidian.edu.cn/gradeLnAllAction.do?type=ln&oper=fainfo&fajhh=1488'
        self.driver = webdriver.PhantomJS()
        self.username = username
        self.password = password
        self.login()

    def login(self):
        self.logger.debug('%s login....', self.username)
        try:
            self.driver.get(self.login_url)
            # username
            name = self.driver.find_element_by_xpath('//*[@id="username"]')
            name.clear()
            name.send_keys(self.username)
            # password
            pwd = self.driver.find_element_by_xpath('//*[@id="password"]')
            pwd.clear()
            pwd.send_keys(self.password)
            # login
            btn = self.driver.find_element_by_xpath('//input[@type="submit"]')
            btn.click()
            self.driver.implicitly_wait(2)
            if 'authserver' not in self.driver.current_url:
                self.logger.debug('login successfully!')
        except:
            self.logger.error('login error!')
            self.driver.close()

    def evaluate(self):
        self.logger.debug('%s evaluating...', self.username)
        try:
            self.driver.get(self.evaluate_url)
            trs = self.driver.find_element_by_xpath(
                '//*[@id="user"]/tbody'
            ).find_elements_by_tag_name('tr')
            self.logger.debug('Totally: %d pages', len(trs))
        except:
            self.logger.error('cannot find total pages!')
            raise Exception('error occurs when get and parse %s', self.evaluate_url)

        for index1 in range(len(trs)):
            try:
                # pass evaluated
                if self.driver.find_element_by_xpath(
                        f'//*[@id="user"]/tbody/tr[{str(index1+1)}]/td[4]'
                ).text == u'是':
                    continue

                self.logger.debug('still: %s pages', len(trs)-index1)
                self.driver.find_element_by_xpath(
                    f'//*[@id="user"]/tbody/tr[{str(index1+1)}]/td[5]/img'
                ).click()

                for btn_id in range(17, 32):
                    self.driver.find_element_by_name(
                        f'00000000{str(btn_id)}'
                    ).click()

                self.driver.find_element_by_xpath(
                    '/html/body/form/table[4]/tbody/tr/td/table[4]/tbody/tr/td/img[1]'
                ).click()
                time.sleep(3)
                self.driver.get(self.evaluate_url)
            except:
                self.logger.error('failed to evaluate teacher %d', index1)

        self.logger.debug('evaluation finished!')

    def download_report(self):
        self.logger.debug('printing report of %s ...', self.username)

        try:
            self.driver.get(self.report_url)
            # self.driver.get_screenshot_as_file(self.username+'_report.png')

            tree = etree.HTML(self.driver.page_source)

            score = defaultdict(list)

            for course in tree.xpath('//table[@id="user"]/tbody/tr'):
                course_info = course.xpath('./td/text()')
                score['course_no'].append(course_info[0])
                score['course_name'].append(course_info[2])
                score['credit'].append(course_info[4])
                score['course_type'].append(course_info[5])
                score['score'].append(course.xpath('./td/p/text()')[0])

            df = pd.DataFrame(score)
            df.to_csv(self.username+'_report.csv')
        except:
            self.logger.error('failed to download report!')

        self.logger.debug('report downloader finished!')
