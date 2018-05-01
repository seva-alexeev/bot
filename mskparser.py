import urllib.request
from bs4 import BeautifulSoup
import http.client
import urllib.parse
import requests

urlya = 'https://lms.yandexlyceum.ru/accounts/profile'


def get_html(url):
    response = urllib.request.urlopen(url)
    return response.read()


def parse(html):
    soup = BeautifulSoup(html)
    table = soup.find('div', _class='card-block')
    spanish = soup.find('span', _class='label label-status overflow-ellipsis')
    return table


user_data = {'username': 'v.alekseev74@yandex.ru', 'password': 'aprel19'}
response = requests.post('https://lms.yandexlyceum.ru/accounts/profile/', data=user_data)

print(response.text)
