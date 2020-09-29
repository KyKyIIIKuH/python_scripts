# -*- coding: utf-8-*-

import re
from bs4 import BeautifulSoup

import urllib3
urllib3.disable_warnings()

import requests
import sys

# ID VK пользователя, за которым хотим наблюдать
uid_select = "ID VK"

# Ссылка на розыгрыш smmninja
url_page_event = "https://smmninja.ru/game-field/?event=ID"

# Список пользователей
list_users = list()
list_users_ticket = list()

# Ищем данные в массиве
def build_dict(seq, key):
    return dict((d[key], dict(d, index=index)) for (index, d) in enumerate(seq))

# Список участников
def count_users(tr):
	global list_users
	for row_tr in tr:
		td = row_tr.find_all("td")

		name = td[2].getText().split("@")[0]
		uid = td[2].find_all("a", href=True)[0]["href"].split("https://vk.com/id")[1].lstrip()
		name = name.replace("<br>", "")
		name = name.replace("\n", "")

		if( next((item for item in list_users if item["uid"] == uid), None) == None):
			list_users.append( {'name': name, 'uid': uid, 'tickets': 0} )

# Считаем сколько у пользователей билетов
def count_users_tickets(tr):
	global list_users
	for row_tr in tr:
		td = row_tr.find_all("td")

		uid = td[2].find_all("a", href=True)[0]["href"].split("https://vk.com/id")[1].lstrip()

		info_ = build_dict(list_users, key="uid")
		user_info = info_.get(uid)["index"]

		if( next((item for item in list_users if item["uid"] == uid), None) != None):
			list_users[int(user_info)]["tickets"] = int(list_users[int(user_info)]["tickets"])+1

# Считаем сколько билетов у указанного пользователя по ID
def count_users_tickets_sel(uid):
	global list_users

	info_ = build_dict(list_users, key="uid")
	user_info = info_.get(uid)

	return user_info

# Get a copy of the default headers that requests would use
headers = requests.utils.default_headers()

headers.update(
    {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Safari/537.36',
    }
)

session_requests = requests.session()

result = session_requests.post(
	url_page_event, 
	headers = headers,
	timeout=10, allow_redirects=True,
)

soup = BeautifulSoup(result.content, "html.parser")

table = soup.find_all("table", {"class": "table-striped"})[0]
tr = table.find_all("tr", {"class": "show"})

# Считаем сколько пользователей в таблице
count_users(tr)

# Считаем сколько у пользователя билетов
count_users_tickets(tr)

# Считаем сколько билетов у указанного пользователя по ID
uid_select_ticket = count_users_tickets_sel(uid_select)

# Выводим всех пользователей
for row in list_users:
	if(int(row["tickets"]) > int(uid_select_ticket["tickets"])):
		list_users_ticket.append( {'name': row["name"], 'uid': row["uid"], 'tickets': row["tickets"]} )

print("Кол-во участников: %s\n" % (len(list_users)))

print("У этих пользователей больше билетов чем у %s | Билетов: %s" % (uid_select_ticket["name"], uid_select_ticket["tickets"]))
for row in list_users_ticket:
	print("Имя: %s | Билетов: %s" % (row["name"], row["tickets"]))
