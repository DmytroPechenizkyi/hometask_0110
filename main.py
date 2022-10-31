# Написать парсер, использовать многопоточность
import json
import re
from threading import Thread
from multiprocessing import Queue
import requests
from lxml import html
from bs4 import BeautifulSoup
import sqlite3
import time

URL = 'https://amf.ua/kresla/konferenckresla/'


def get_one_chair_info(url, counter: int, li: list):
    chair_dict = Queue()
    response = requests.get(url)
    name_xpath = f'/html/body/div[3]/section/article/div/section/div/div/div[2]/div[{counter}]/div/div[2]/div/div[2]/strong/text()'
    price_xpath = f'/html/body/div[3]/section/article/div/section/div/div/div[2]/div[{counter}]/div/a/span[2]/text()'
    img_xpath = f'/html/body/div[3]/section/article/div/section/div/div/div[2]/div[{counter}]/div/a/span[1]/img'
    if response.status_code == 200:
        tree = html.fromstring(response.text)
        name = str(tree.xpath(name_xpath))
        price = str(tree.xpath(price_xpath))
        img = str(tree.xpath(img_xpath))
        chair_dict.put({'имя':  name, 'цена(грн)': price, 'изображение': img})
        content = chair_dict.get()
        li.append(content)
        print(content)
    return chair_dict


def get_all_chairs(url=URL):
    chairs_list = []
    for i in range(1, 3):
        threads = []
        response = requests.get(url+f'page{i}/')
        soup = BeautifulSoup(response.content, 'lxml')
        chairs = soup.find_all('div', class_='product-block')
        for chair in chairs:
            t = Thread(target=get_one_chair_info, args=(url, chairs.index(chair), chairs_list, ))
            t.start()
            threads.append(t)
        for t in threads:
            t.join()
    return chairs_list


def serialize_to_json(something):
    with open('chairs.json', 'w', encoding='utf-8') as file:
        json.dump(something, file, indent=4, ensure_ascii=False)


def json_to_db():
    connection = sqlite3.connect('chairs.db')
    with open('chairs.json', 'r', encoding='utf-8') as file:
        chairs_info = json.load(file)
    cursor = connection.cursor()
    for chair in chairs_info:
        cursor.execute("INSERT INTO CHAIRS(name, price, image)"
                       f"VALUES ('{chair['имя']}', '{chair['цена(грн)']}', '{chair['изображение']}')")
    connection.commit()

#1.
# start = time.perf_counter()
# get_all_chairs()
# end = time.perf_counter()
# print(end - start)

#2
# start = time.perf_counter()
# res = requests.get(URL).content
# so = BeautifulSoup(res, 'lxml')
# div_list = so.find_all('div', class_='product-block-container')
# src_list = []
# title_list = []
# price_list = []
# for div in div_list:
#     img = div.find('span', class_='image')
#     title = div.find('span', class_='title').text
#     price = div.find('strong').text
#     src = 'https:' + img.find('img').get('src')
#     if re.search('gif', src):
#         src = 'https:' + img.find('img').get('data-src')
#     elif re.search('newtop', src):
#         continue
#     src_list.append(src)
#     title_list.append(title)
#     price_list.append(price)
#
# li = []
# for i in range(len(title_list)):
#     li.append({'имя':  title_list[i], 'цена(грн)': price_list[i], 'изображение': src_list[i]})
# print(li)
# end = time.perf_counter()
# print(end - start)