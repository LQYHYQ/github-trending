# -*- coding: utf-8 -*-
# @FileName    : main.py
# @Author  : LUOQIUYOU
# @Time    : 2023/12/15 17:05


import requests
from bs4 import BeautifulSoup
import json
import configparser
import os
import logging
from logging.handlers import RotatingFileHandler
from datetime import datetime
import pymysql

config = configparser.ConfigParser()
config.read(os.path.join(os.getcwd(), "config.ini"))


# 初始化日志
def loggging_init():
    # 创建一个logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)  # Log等级总开关  此时是INFO

    # 创建一个handler，用于写入日志文件
    # 拼接 log 文件夹的路径
    logfile = os.path.join(current_directory, "all_log.log")
    fh = logging.handlers.TimedRotatingFileHandler(logfile, encoding="utf-8")  # open的打开模式这里可以进行参考
    fh.setLevel(logging.DEBUG)  # 输出到file的log等级的开关

    # 定义handler的输出格式（时间，文件，行数，错误级别，错误提示）
    formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
    fh.setFormatter(formatter)

    # 将logger添加到handler里面
    logger.addHandler(fh)


# 使用pushplus服务推送
def pushplus(content):
    api_url = "http://www.pushplus.plus/send/"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        "Content-Type": "application/json",
    }
    token = config.get("pushplus", "token")
    data = {
        "token": token,
        "title": "获取Github Trending程序执行通知",
        "content": content,
        "channel": "wechat",
        "template": "json"
    }
    body = json.dumps(data).encode(encoding='utf-8')
    requests.post(api_url, headers=headers, data=body)


def request(url):
    try:
        header = {
            'User-Agent': 'Mozilla / 5.0(Windows NT 10.0;Win64;x64) AppleWebKit / 537.36(KHTML, likeGecko) Chrome / 115.0.0.0Safari / 537.36'
        }
        response = requests.get(url, headers=header, timeout=10)
        if response.status_code == 200:
            parse(response.text)
    except requests.RequestException as e:
        pushplus("Github Trending请求异常：{}".format(e))
        return None


def parse(html):
    soup = BeautifulSoup(html, 'lxml')
    article_list = soup.findAll("article", attrs={'class': 'Box-row'})
    project_list = list()
    for article in article_list:
        project_name = article.find("h2").text.strip().replace("\n\n      ", " ")
        project_url = article.find("h2").find("a")['href']
        project_about = None
        if article.find("p") is not None:
            project_about = article.find("p").text.strip()
        project_programming_language = None
        if article.find("span", attrs={'itemprop': 'programmingLanguage'}) is not None:
            project_programming_language = article.find("span", attrs={'itemprop': 'programmingLanguage'}).text.strip()
        project_star = int(
            article.findChildren("a", attrs={'class': 'Link Link--muted d-inline-block mr-3'})[0].text.strip().replace(
                ",", ""))
        project_fork = int(
            article.findChildren("a", attrs={'class': 'Link Link--muted d-inline-block mr-3'})[1].text.strip().replace(
                ",", ""))
        item_dict = {
            'project_name': project_name,
            'project_url': project_url,
            'project_about': project_about,
            'project_programming_language': project_programming_language,
            'project_star': project_star,
            'project_fork': project_fork
        }
        project_list.append(item_dict)
    save_md(project_list)
    save_db(project_list)


# 保存markdown文件
def save_md(item_list):
    # 指定路径下按年分开保存
    current_time = datetime.now().strftime("%Y")
    path = os.path.join(current_directory, "data", current_time)
    if not os.path.exists(path) and not os.path.isdir(path):
        os.makedirs(path)
    date_str = datetime.now().strftime("%Y-%m-%d")
    try:
        file_path = os.path.join(path, "GithubTrending" + date_str + ".md")
        with open(file_path, 'w', encoding="utf-8") as f:
            f.write("# {} Github Trending \n\n--- \n".format(date_str))
            for item in item_list:
                project_name = item['project_name']
                project_url = "https://github.com{}".format(item['project_url'])
                project_about = item['project_about']
                project_programming_language = item['project_programming_language']
                project_star = item['project_star']
                project_fork = item['project_fork']

                row = "+ **[{}]({})**  \n".format(project_name, project_url)
                if project_about is not None:
                    row += "**About**: {}  \n".format(project_about)
                if project_programming_language is not None:
                    row += "**Language**: {}  \n".format(project_programming_language)
                row += "**Star**: {}  \n".format(project_star)
                row += "**Fork**: {}  \n".format(project_fork)
                row += "--- \n"
                f.write(row)

    except FileNotFoundError:
        logging.exception("无法打开指定的文件!" + file_path)
    except LookupError:
        logging.exception("指定了未知的编码!" + file_path)
    except UnicodeDecodeError:
        logging.exception("读取文件时解码错误!" + file_path)


# 保存数据进数据库
def save_db(item_list):
    con = configparser.ConfigParser()
    con.read("config.ini", encoding="utf-8")
    items = con.items("mysql")
    items = dict(items)
    host = items.get("host")
    user = items.get("user")
    password = items.get("password")

    # 当前天时间 yyyy-MM-dd格式
    date = datetime.now().date()
    try:
        db = pymysql.connect(host=host, user=user, password=password, db="github")
        cursor = db.cursor()
        for item in item_list:
            sql = "INSERT INTO github_trending_daily(name,url,about,language,star,fork,date) values(%s,%s,%s,%s,%s,%s,%s)"
            cursor.execute(sql, (
                item['project_name'], "https://github.com{}".format(item['project_url']), item['project_about'], item['project_programming_language'], item['project_star'], item['project_fork'], date))
        db.commit()
        cursor.close()
    except pymysql.MySQLError as e:
        # 捕获 pymysql 异常
        logging.error("pymysql error:" + e)
    finally:
        # 确保关闭连接，无论是否发生异常
        if db:
            db.close()


def run():
    try:
        url = 'https://github.com/trending'
        request(url)
    except Exception as e:
        logging.exception(e)
        pushplus("Github Trending程序执行异常：{}".format(e))


if __name__ == '__main__':
    # 获取当前脚本所在的目录
    current_directory = os.path.dirname(os.path.abspath(__file__))

    # 初始化日志
    loggging_init()

    # 执行主程序
    run()

