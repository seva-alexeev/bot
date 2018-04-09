import urllib.request
from bs4 import BeautifulSoup
from telegram.ext import Updater, MessageHandler, Filters, CommandHandler
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove
import random
import time


class FlowParser:
    def __init__(self):
        self.NEWS_URL = 'http://the-flow.ru/news'
        self.SUPER_BASE_URL = 'http://the-flow.ru'
        self.ALB_URL = 'http://the-flow.ru/releases'
        self.INTER_URL = 'http://the-flow.ru/features'
        self.BATLE_URL = 'http://the-flow.ru/battles'
        self.CLIP_URL = 'http://the-flow.ru/videos'
        self.BASE_URL = 'http://the-flow.ru/'
        self.REPRU_URL = 'http://www.rap.ru'
        self.READ_URL = 'http://www.rap.ru/reading'
        self.what_is = 'Что такое хип-хоп? Читай википедию:\nhttps://ru.wikipedia.org/wiki/Хип-хоп_(музыкальный_жанр)'
        self.BILL_URL = 'https://www.billboard.com/charts/hot-100'
        self.BILL_ALB_URL = 'https://www.billboard.com/charts/billboard-200'
        self.BILL_ART_URL = 'https://www.billboard.com/charts/artist-100'
        self.REP_URL = 'https://www.hotnewhiphop.com/artists/'

    def get_html(self, url):
        response = urllib.request.urlopen(url)
        return response.read()

    def parse_flow(self, html):
        hrefs = []
        soup = BeautifulSoup(html)
        table = soup.find('div', class_='items')
        news = table.find_all('div')
        for new in news:
            dicct = {
                'name': None,
                'link': None,
                'descript': None
            }
            a = new.find('a', class_='bold')
            if a:
                dicct['link'] = self.SUPER_BASE_URL + str(a).split(' ')[2].split('"')[1] + '/'
                dicct['name'] = str(a).split('<')[-2].split('>')[-1]
                div_desc = new.find('div', class_='publication__item-text')
                if div_desc:
                    dicct['descript'] = str(div_desc).split('>')[1].split('<')[0].strip()
                    hrefs.append(dicct)
        return hrefs

    def hottest_news(self, html):
        hrefs = []
        soup = BeautifulSoup(html)
        cont = soup.find('div', class_='content')
        div = cont.find_all('div', class_='fix')
        news = div[-1].find_all('div')
        for new in news[2:]:
            dicct = {
                'name': None,
                'link': None,
                'descript': None
            }
            div = new.find('div', class_='publication__item-title')
            if div:
                a = div.find('a')
                dicct['link'] = self.SUPER_BASE_URL + str(a).split(' ')[1].lstrip('href="').split('"')[0]
                dicct['name'] = a.text
                dicct['descript'] = new.find('div', class_='publication__item-text').text.strip()
                hrefs.append(dicct)
        return hrefs

    def repruparser(self, html):
        hrefs = []
        soup = BeautifulSoup(html)
        table = soup.find('div', class_='view grid clearfix')
        for new in table:
            if new != '\n':
                dicct = {
                    'name': str(new.find('a', class_='title').text),
                    'link': self.REPRU_URL+(str(new.find('a', class_='title'))).split()[2].split('"')[1]
                }
                hrefs.append(dicct)
        return hrefs

    def bill_board_parser(self,html):
        hrefs = []
        soup = BeautifulSoup(html)
        date = soup.find('time').text
        table = soup.find_all('div', class_='chart-row__title')
        for new in table:
            dicct = {
                'name': None,
                'title': None
            }
            if new.find('a'):
                dicct['name'] =  new.find('a').text.strip()
                dicct['title'] = new.find('h2').text
                hrefs.append(dicct)
            else:
                dicct['name'] = new.find('span').text.strip()
                dicct['title'] = new.find('h2').text
                hrefs.append(dicct)
        return date, hrefs

    def get_artist_info(self, artist):
        name = str(artist).strip()
        first_char = str(artist.strip())[0].lower()
        if not first_char.isalpha():
            first_char = '_'
        link = self.REP_URL + first_char + '/'
        html = self.get_html(link)
        soup = BeautifulSoup(html)
        table = soup.find('div', class_='gridItems-flex-wrap artist pull-left')
        a = table.find('a', title=name, class_='cover-title')
        href = self.REP_URL.rstrip('/artists') + str(a).split()[2].lstrip('href="').rstrip('"')
        soup = BeautifulSoup(self.get_html(href))
        table = soup.find('div', class_='col-hnhh-left no-padding-mobile')
        hrefs = []
        dicct = {
            'descript': None,
            'facts': None,
            'top_s': None,
        }
        strinfo = ''
        info = table.find('div', class_='artist-bio artistBio-block') #доделать блин
        for p in info.find_all('p'):
            strinfo += ' '.join(str(p.text).split())
        dicct['descript'] = strinfo
        info = table.find('ul', class_='artist-facts-ul artistFacts-listBlock-ul')
        facts = []
        if info:
            for div in info:
                for li in div:
                    facts.append(str('# ' + li.text))
            if len(facts) > 0:
                dicct['facts'] = facts
        top = []
        info = table.find('ul', class_='dropDown-listBlock')
        for li in info:
            if li.find('div', class_='cover-title topSongs-item-title'):
                top.append(' '.join(li.find('div', class_='cover-title topSongs-item-title').text.strip().split()))
        if len(top):
            dicct['top_s'] = top
        return dicct


def get_new(link):
    obj = FlowParser()
    new = random.choice(obj.parse_flow(obj.get_html(link)))
    return str(new['name'] + '\n' + new['link'] + '\n' + new['descript'])


def get_hottest_news():
    obj = FlowParser()
    block = obj.hottest_news(obj.get_html(obj.BASE_URL))
    string = ''
    string += 'Главные хип-хоп новости этой недели:\n\n'
    for new in block:
        string += str(new['name'] + '\n' + new['link'] + '\n' + new['descript'] + '\n\n')
    return string


def get_list_of_news(link):
    obj = FlowParser()
    news = obj.parse_flow(obj.get_html(link))
    string = ''
    for new in news:
        string += str(str(news.index(new)+1) + '. ' + new['name'] + '\n' + new['link'] + '\n' + new['descript']
                      + '\n\n')
    return string


def get_educ():
    obj = FlowParser()
    block = random.choice(obj.repruparser(obj.get_html(obj.READ_URL)))
    return str(block['name'] + '\n' + block['link'])


def get_list_of_educ():
    obj = FlowParser()
    block = obj.repruparser(obj.get_html(obj.READ_URL))
    string = ''
    for new in block:
        string += str(block.index(new)+1) + '. ' + new['name'] + '\n' + new['link'] + '\n\n'
    return string


def get_knowlage():
    obj = FlowParser()
    return obj.what_is


def get_top(top, link):
    obj = FlowParser()
    string = ''
    string += obj.bill_board_parser(obj.get_html(link))[0]+'\n'
    string += 'Billboard hot 100\n\n'
    for i in range(top):
        if i == 0:
            string += '🥇 '+ obj.bill_board_parser(obj.get_html(link))[1][i]['name'] + '\n' + \
                      obj.bill_board_parser(obj.get_html(link))[1][i]['title'] + '\n'
        if i == 1:
            string += '🥈 ' + obj.bill_board_parser(obj.get_html(link))[1][i]['name'] + '\n' + \
                      obj.bill_board_parser(obj.get_html(link))[1][i]['title'] + '\n'
        if i == 2:
            string += '🥉 '+ obj.bill_board_parser(obj.get_html(link))[1][i]['name'] + '\n' + \
                      obj.bill_board_parser(obj.get_html(link))[1][i]['title'] + '\n'
        if i > 2:
            string += (str(i+1)+'. ') + obj.bill_board_parser(obj.get_html(link))[1][i]['name']+'\n'+\
            obj.bill_board_parser(obj.get_html(link))[1][i]['title']+'\n'
    string += link
    return string


def return_artist(name):
    obj = FlowParser()
    string = ''
    string += name + '\n'
    if obj.get_artist_info(name)['descript']:
        string += 'About:\n'
        string += '\t'+obj.get_artist_info(name)['descript']+'\n\n'
    if obj.get_artist_info(name)['facts']:
        string += 'Facts:\n'
        list = obj.get_artist_info(name)['facts']
        for fact in list:
            string += '\t'+fact+'\n'
        string += '\n'
    if obj.get_artist_info(name)['top_s']:
        string += 'Top songs:\n'
        list = obj.get_artist_info(name)['top_s']
        for song in list:
            string += '\t'+song+'\n'
    return string


reply_keyboard = [['Рандомные новости ⁉️', 'Свежие новости 📣'],
                  ['Что такое хип-хоп 🎵🎶🎵', 'Образовачи 🙇‍♀️🙇'],
                  ['Billboard 💽', 'Узнать про репера 🕺'],
                  ['закрыть']]


def main_answer(bot, update):
    t = update.message.text.lower().strip()
    flow = FlowParser()
    if t == 'случайная новость':
        update.message.reply_text(get_new(flow.NEWS_URL))
    if t == 'случайная новость про релизы':
        update.message.reply_text(get_new(flow.ALB_URL))
    if t == 'случайная новость про интервью':
        update.message.reply_text(get_new(flow.INTER_URL))
    if t == 'случайная новость про батлы':
        update.message.reply_text(get_new(flow.BATLE_URL))
    if t == 'случайная новость про клипы':
        update.message.reply_text(get_new(flow.CLIP_URL))
    if t == 'главные новости недели':
        update.message.reply_text(get_hottest_news())
    if t == 'свежие новости из мира хип-хопа':
        update.message.reply_text(get_list_of_news(flow.NEWS_URL))
    if t == 'свежие новости про релизы':
        update.message.reply_text(get_list_of_news(flow.ALB_URL))
    if t == 'свежие новости про интервью':
        update.message.reply_text(get_list_of_news(flow.INTER_URL))
    if t == 'свежие новости про батлы':
        update.message.reply_text(get_list_of_news(flow.BATLE_URL))
    if t == 'свежие новости про клипы':
        update.message.reply_text(get_list_of_news(flow.CLIP_URL))
    if t == 'что такое хип-хоп 🎵🎶🎵':
        update.message.reply_text(get_knowlage())
    if t == 'случайный образовач':
        update.message.reply_text(get_educ())
    if t == 'последние образовачи':
        update.message.reply_text(get_list_of_educ())
    if ' '.join(t.split()[:2]) == 'биллборд хот':
        update.message.reply_text(get_top(int(t.split()[-1]), flow.BILL_URL))
    if str(t.split()[0]) == 'биллборд' and len(t.split()) == 2:
        update.message.reply_text(get_top(int(t.split()[-1]), flow.BILL_ALB_URL))
    if ' '.join(t.split()[:2]) == 'биллборд артисты':
        update.message.reply_text(get_top(int(t.split()[-1]), flow.BILL_ART_URL))
    if t.split()[0] == 'репер':
        name = ' '.join(str(update.message.text).split()[1:])
        update.message.reply_text(return_artist(name))
    if t == 'закрыть':
        update.message.reply_text('Ты только что закрыл клавиатуру!\
        Что бы открыть снова напиши "открыть" или команду /open!', reply_markup=ReplyKeyboardRemove())
    if t == 'открыть':
        reply_keyboard = [['Рандомные новости ⁉️', 'Свежие новости 📣'],
                          ['Что такое хип-хоп 🎵🎶🎵', 'Образовачи 🙇‍♀️🙇'],
                          ['Billboard 💽', 'Узнать про репера 🕺'],
                          ['закрыть']]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
        update.message.reply_text('Ты только что открыл клавиатуру!\
        Что бы закрыть напиши "закрыть" или команду /close!', reply_markup=markup)
    if t == 'назад':
        update.message.reply_text('открываем главное меню...',reply_markup=ReplyKeyboardRemove())
        reply_keyboard = [['Рандомные новости ⁉️', 'Свежие новости 📣'],
                          ['Что такое хип-хоп 🎵🎶🎵', 'Образовачи 🙇‍♀️🙇'],
                          ['Billboard 💽', 'Узнать про репера 🕺'],
                          ['закрыть']]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
        update.message.reply_text('Главное меню:', reply_markup=markup)
    if t == 'рандомные новости ⁉️':
        update.message.reply_text('открываем рандомные новости...', reply_markup=ReplyKeyboardRemove())
        reply_keyboard = [['Случайная новость', 'Случайная новость про релизы'],
                          ['Случайная новость про интервью', 'Случайная новость про батлы'],
                          ['Случайная новость про клипы', 'Назад']]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
        update.message.reply_text('Рандомные новости:', reply_markup=markup)
    if t == 'свежие новости 📣':
        update.message.reply_text('открываем свежие новости...', reply_markup=ReplyKeyboardRemove())
        reply_keyboard = [['Свежие новости из мира хип-хопа', 'Свежие новости про релизы'],
                          ['Свежие новости про интервью', 'Свежие новости про батлы'],
                          ['Свежие новости про клипы', 'Назад']]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
        update.message.reply_text('Свежие новости:', reply_markup=markup)
    if t == 'образовачи 🙇‍♀️🙇':
        update.message.reply_text('открываем образовачи...', reply_markup=ReplyKeyboardRemove())
        reply_keyboard = [['Случайный образовач', 'Последние образовачи'],
                          ['Назад']]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
        update.message.reply_text('Образовачи:', reply_markup=markup)
    if t == 'billboard 💽':
        update.message.reply_text('открываем биллборды...', reply_markup=ReplyKeyboardRemove())
        reply_keyboard = [['Billboard hot 100', 'Billboard 200', 'Artists 100'],
                          ['Назад']]
        markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
        update.message.reply_text('Биллборды:', reply_markup=markup)
    if t == 'узнать про репера 🕺':
        update.message.reply_text('Просто напиши мне "репер ИМЯ АРТИСТА". \n\n\
        Если ты не получил ответ, то возможно его нет в базе данных или ты совершил ошибку.')
    if t == 'billboard hot 100':
        update.message.reply_text('Напиши мне "биллборд хот КОЛЛИЧЕСТВО МЕСТ"')
    if t == 'billboard 200':
        update.message.reply_text('Напиши мне "биллборд КОЛЛИЧЕСТВО МЕСТ"')
    if t == 'artists 100':
        update.message.reply_text('Напиши мне "биллборд артисты КОЛЛИЧЕСТВО МЕСТ"')


def start(bot, update):
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    update.message.reply_text("Привет! Я ходячая энциклопедия хип-хопа! (или не совсем...)\n\n\
    Общайся со мной через удобную клавиатуру или присылай мне сообщения, если тебе так будет удобнее)\n\n\
    Если тебе не нужна клавиатура, то можешь её выключить командой '/close' или написать 'закрыть', а открыть снова - \
    командой '/open' или написав 'открыть'. \n\n\
    Для того, что бы узнать про все команды, напиши 'помощь' или команду '/help'", reply_markup=markup)


def close(bot, update):
    update.message.reply_text('Ты только что закрыл клавиатуру!\
    Что бы открыть снова напиши "открыть" или команду /open!', reply_markup=ReplyKeyboardRemove())


def open(bot, update):
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    update.message.reply_text('Ты только что открыл клавиатуру!\
    Что бы закрыть напиши "закрыть" или команду /close!', reply_markup=markup)


def help(bot, update):
    update.message.reply_text('потом напишу')


def main():
    flow = FlowParser()
    updater = Updater("593099290:AAFCDXE1FvqvQ55ArutQKTVv3_wG08lQzjE")
    dp = updater.dispatcher

    text_handler = MessageHandler(Filters.text, main_answer)
    dp.add_handler(text_handler)
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("close", close))
    dp.add_handler(CommandHandler("open", open))

    print('бот стартанул')

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
