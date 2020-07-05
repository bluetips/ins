# -*- coding: utf-8 -*-
"""
@Time : 2020/6/9 16:20
@Author : keith wx:bluetips
@File : login_tool.py
@Software: PyCharm 
@desc: 借助selenium用于登录账户，获取cookie
"""
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class Tool:
    def __init__(self, user_list):
        self.user_list = user_list

    def get_email_verify(self, driver, user, pwd):
        driver.find_element_by_id("TANGRAM__22__select_show_arrow").click()
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="TANGRAM__22__select_email"]'))
        ).click()
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@id="TANGRAM__22__button_send_email"]'))
        ).click()
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[@class="email_url"]'))
        ).click()
        print('跳转到邮箱登录')
        time.sleep(5)
        handles = driver.window_handles
        driver.switch_to_window(handles[1])
        driver.find_element_by_class_name()
        driver.switch_to.frame(0)
        driver.find_element_by_name("email").clear()
        driver.find_element_by_name("email").send_keys(user)
        driver.find_element_by_name("password").clear()
        driver.find_element_by_name("password").send_keys(pwd)
        driver.find_element_by_id("dologin").click()
        pass

    def gen_cookie(self, user):
        _user = user.replace('\n','')
        _pwd = 'God2012'
        driver = webdriver.Chrome()
        driver.get('https://www.instagram.com/accounts/login/?next=/devonwindsor/tagged/')
        try:
            element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@class="gr27e "]'))
            )
            print("账户密码登录")
            driver.find_element_by_name("username").send_keys(_user)
            driver.find_element_by_name("password").send_keys(_pwd)
            driver.find_element_by_class_name("sqdOP  L3NKy   y3zKF     ").click()
            print('输入账户密码完成')
            while 'Sucess' not in driver.current_url:
                if '身份验证' in driver.page_source:
                    print('请滑动验证码')
                if '您的帐号可能存在安全风险，为了确保为您本人操作，请先进行安全验证' in driver.page_source:
                    self.get_email_verify(driver, _user)
                time.sleep(2)

        except Exception:
            print('登录错误')
            driver.quit()
            return None
        finally:
            print('结束操作')
            cookies = driver.get_cookies()
            cookie_str = ''
            for i in cookies:
                cookie_str = cookie_str + i['name'] + '=' + i['value'] + ';'
            open('./capters/cookie_file', 'a').write(cookie_str + '\n')
            print('存cookie', cookie_str)
            quit_flag = input('是否退出？1,2: ')
            if quit_flag == 1:
                driver.quit()
            else:
                time.sleep(6000)
                pass
            return cookie_str

    def run(self):
        for user in user_pwd_list:
            cookie_str = self.gen_cookie(user=user)


if __name__ == '__main__':
    user_pwd_list = open('./user_pwd_file', 'r').readlines()
    tool = Tool(user_list=user_pwd_list)
    tool.run()
