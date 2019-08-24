#!/usr/bin/python

from requests_html import HTMLSession
import urllib.parse
import datetime
import yaml

# Путь к файлу для сохранения последнего id и к конфигу

path_id = 'last_id.txt'  # для ручного запуска
path_config = 'config.yaml'  # для ручного запуска

# path_id = '/home/bystrov/bin/edinstvo/last_id.txt'  # для запуска в linux по crone
# path_config = '/home/bystrov/bin/edinstvo/config.yaml' # для запуска в linux по crone

# количество новостей, которое будет приходить с сообщении
count_of_news = 5


# Простой метод, для формирования лога
def write_to_console(text):
    print(f'{current_time} - {text}')


def get_news():
    """
    Основной метод получения новостей с сайта https://edinstvo62.ru/
    Парсим блок с новостями со страницы, и формируем из него словарь
    Далее из словарей собираем массив
    :return: Кортеж из массива count_of_news последних новостей и id верхней новости,
    который потом пишется в файл last_id.txt
    """
    write_to_console('get news')
    last_news = []
    url = 'https://edinstvo62.ru/info'
    session = HTMLSession()
    resp = session.get(url)
    if resp.status_code == 200:
        # получаем и парсим блок с новостями со страницы
        blocks = resp.html.xpath('//ul[@class = "search_list"]//li')
        for number, block in enumerate(blocks, 1):
            if number <= count_of_news:
                name = block.xpath('//a[1]')[0].text
                link = block.xpath('//a[1]/@href')[0]
                id = link.split('/')[4]
                desc = block.xpath('//p[1]')[0].text
                last_news.append({'id': id, 'name': name, 'link': link, 'desc': desc})
    return last_news, last_news[0]['id']


# метод для записи id в файл
def write_id(id):
    write_to_console('write file')
    with open(path_id, "w", encoding='utf-8') as f:
        f.write(id)


# метод для чтения id из файла
def read_id():
    write_to_console('read file')
    with open(path_id, "r", encoding='utf-8') as f:
        return f.read()


# метод для получения alarmerbot key из config.yaml
def get_key():
    with open(path_config, 'r', encoding='utf-8') as stream:
        data = yaml.safe_load(stream)
    return data['telegram']['alarmerbot_key']


# метод для отправки сообщения в телергамм, через alarmerbot
def send_to_telegram(data):
    write_to_console('send to telegram')
    text = "Есть новые новости на сайте ГК Единство!\n\n"
    for line in data:
        text += f"{line['name']}\n{line['desc']}\n{line['link']}\n\n"
    # обезапашиваем наш url
    safe_text = urllib.parse.quote(text)
    url = f'https://alarmerbot.ru/?key={get_key()}&message={safe_text}'
    session = HTMLSession()
    return session.get(url)


if __name__ == '__main__':

    now = datetime.datetime.now()
    current_time = now.strftime("%d-%m-%Y %H:%M")

    last_news_id = read_id()
    # Получаем текущие новости с сайта
    current_news, current_news_id = get_news()

    # Если есть новые новости на сайте - перезаписываем и шлем сообщение в телегу
    if current_news_id != last_news_id:
        write_id(current_news_id)
        send_to_telegram(current_news)
    else:
        write_to_console('no new news')

