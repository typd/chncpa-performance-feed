#!/usr/bin/env python3
"""
Usage:
  feed.py [-p=<port>]
  feed.py -h

Options:
  -p=<port>  port [default: 80]
  -h --help  show this
"""

import datetime
from urllib.parse import urljoin

from docopt import docopt
from flask import Flask
from flask import request
from flask import render_template
from werkzeug.contrib.atom import AtomFeed
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/feed')
def feed():
    feed = AtomFeed('China National Center of Performing Arts performances',
            feed_url=request.url,
            url=request.url_root,
            author={'name': 'typd', 'email': 'othertang@gmail.com'})
    list = get_performance_list()
    for title, link, content in list:
        feed.add(title, content, url=link, updated=datetime.datetime.now())
    return feed.get_response()

def get_performance_list():
    url = 'http://ticket.chncpa.org/search/all?pagenum=1&price=200&orderstype=update'
    html = None
    try:
        html = requests.get(url, timeout=5).text
    except:
        print('fail to access {}'.format(url))
        return []
    soup = BeautifulSoup(html)
    list = soup.find('div', attrs={'class': 'order-list'})
    shows = list.find_all('div', class_='order-list-show')
    items = []
    for show in shows:
        h4 = show.find('h4')
        title = h4.get_text()
        link = h4.find('a').get('href')
        items.append((title, link, show.get_text()))
    return items

if __name__ == '__main__':
    args = docopt(__doc__)
    app.debug = True
    app.run(host='0.0.0.0', port=int(args['-p'] or 80))
