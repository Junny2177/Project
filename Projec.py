#!/usr/bin/env python
# coding: utf-8

# In[1]:
pip install bs4

import re
import requests
import random
import string 
import json
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium import webdriver 
from selenium.webdriver.edge.service import Service 
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium import webdriver 
import streamlit as st
import time
import sympy


# In[2]:


def ignore_details (words):
    string_return = str(words)
    table = str.maketrans("", "", string.punctuation)
    string_return = string_return.translate(table)
    string_return = string_return.lower()
    return (string_return)
    
            


# In[3]:


#Получение конкретного адреса книги по названию
def name_to_link_lab (name, author, number):
    product_name = str(name)
    Author = str(author)
    product_name_2 = product_name + ' ' + Author
    product_name_to_check = ignore_details(product_name)
    
    url_1 = f"https://www.labirint.ru/search/{product_name}/?stype=0"
    url_2 = f"https://www.labirint.ru/search/{product_name_2}/?stype=0"
    
    response_1 = requests.get(url_1)
    response_2 = requests.get(url_2)
    
    list_of_books = []
    
    if response_2.status_code == 200:
        books = BeautifulSoup(response_2.text, "html.parser")
        products = books.find_all("div", class_="product")
        for product in products:
            if len(list_of_books) < int(number):
                title = product['data-name']
                if ignore_details(title) == product_name_to_check:
                    classes = product.find('a', class_="product-title-link" )
                    link = 'https://www.labirint.ru' + classes['href']
                    list_of_books.append([title, link])
    else: 
        list_of_books.append('Такой книжи не найдено,')
        list_of_books.append('попробуйте другое название')
    
    if response_1.status_code == 200:
        books = BeautifulSoup(response_1.text, "html.parser")
        products = books.find_all("div", class_="product")
        for product in products:
            if len(list_of_books) < int(number):
                title = product['data-name']
                if  product_name_to_check in ignore_details(title):
                    classes = product.find('a', class_="product-title-link")
                    link = 'https://www.labirint.ru' + classes['href']
                    list_of_books.append([title, link])
    else: 
        list_of_books.append('Такой книжи не найдено,')
        list_of_books.append('попробуйте другое название')
    if len(list_of_books) ==0:
        list_of_books.append('Такой книжи не найдено,')
        list_of_books.append('попробуйте другое название')
    
    list_of_books_upd = []
    for i in list_of_books:
        if i not in list_of_books_upd:
            list_of_books_upd.append(i)
    if len(list_of_books_upd) > 2 :
        if 'Такой книжи не найдено,' in list_of_books_upd:
            list_of_books_upd.remove('Такой книжи не найдено,')
        if 'попробуйте другое название' in list_of_books_upd:
            list_of_books_upd.remove('попробуйте другое название')
             
    return (list_of_books_upd)


# In[4]:


def link_to_info_lab (name, url):
    data = {'Название': name, 'Наличие':'','Цена без скидки':'', 'Цена со скидкой': '','Издатель': '','Автор': '','Рейтинг': '','Кол-во страниц': '','Ссылка': url ,'Описание':'' }
    # Делаем запрос к сайту и получаем ответ
    response = requests.get(str(url))

    # Проверяем статус ответа
    if response.status_code == 200:
        # Создаем объект BeautifulSoup для разбора HTML-кода
        product = BeautifulSoup(response.text, "html.parser")
        availability = product.find('div', class_="prodtitle-availibility rang-available")
        if availability == None:
            availability = 'Нет информации'
        else: 
            availability = availability.text
        data.update({"Наличие":availability})
        if availability == 'На складе':
            price = product.find(id="product-info")
            dis_price = price['data-discount-price']
            price = price['data-price']
            data.update({"Цена без скидки": price})
            data.update({"Цена со скидкой": dis_price})
        else: data.update({"Цена без скидки": 'Товар отсутствует'})
        publisher = product.find("a", attrs={"data-event-label": "publisher"}).text #издатель
        data.update({"Издатель": publisher})
        author = product.find("div", class_="authors")
        if author == None:
            author = 'Нет информации'
        else: 
            author = author.text  
            delete = r"\Авт.*?\:"
            author = re.sub(delete, "", author)
        data.update({"Автор": author})
        rating = product.find("div", id="rate").text.strip() # оценка книги
        data.update({"Рейтинг": rating})
        pages = product.find('div', class_='pages2')
        if pages == None:
            pages = 'Нет информации'
        else: 
            pages = pages.text
            delete = r"\—.*?\ей"
            pages = re.sub(delete, "", pages) 
            delete = r"\—.*?\я"
            pages = re.sub(delete, "", pages) 
            delete = r"\Стра.*?\ниц:"
            pages = re.sub(delete, "", pages)
        data.update({"Кол-во страниц": pages})
        description = product.find(id="product-about") 
        description = description.find('noindex')
        if description == None:
            description = 'Нет информации'
        else: 
            description = description.text# описание книги
        data.update({"Описание": description})
        data = pd.DataFrame(data, index = ['1'])
    else:
        # Выводим сообщение об ошибке, если статус ответа не 200
        data = 'Ошибка запроса'
    
    return (data)


# In[23]:


def book_search_lab (name, author, number):
    book_lab = name_to_link_lab(name, author, number) 
    if 'Такой книжи не найдено,' in book_lab:
        string_to_print = ''
        for i in book_lab:
            string_to_print_1 = string_to_print + i + ' '
        return (string_to_print_1)
    else:
        df = link_to_info_lab(book_lab[0][0], book_lab[0][1])
        if len(book_lab) > 1:
            for j in range(len(book_lab)-1):
                df_j = link_to_info_lab(book_lab[j+1][0], book_lab[j+1][1])
                df = pd.concat([df, df_j])
            df.reset_index(drop=True, inplace= True)
    return (df)


# In[25]:


name, author, number = st.text_input('Название книги: '), st.text_input('Автор: '), st.text_input('Количество результатов: ')
if number.isnumeric():
    number = int(number)
    results = book_search_lab(name, author, number)
    if type (results) == str:
        print (results)
    else:
        print(results)
    st.write(results)
else: 
    st.write('Вы ввели не число в строке кол-во результатов, введите заново')

