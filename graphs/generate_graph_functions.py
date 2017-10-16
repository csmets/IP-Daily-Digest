""" Generate graphs for digests """

import json
import datetime
import matplotlib.pyplot as plt

def current_date():
    today = datetime.date.today()
    return today

def generate_dates(date, num_of_days):
    """ Using given date and number of days, enumerate through to produce a
    list of dates """

    dates_list = []
    days = 0
    while days < num_of_days:
        days = days + 1
        if days < 10:
            day = '0' + str(days)
        else:
            day = str(days)

        dates_list.append(date + day)

    return dates_list

def past_month_dates():
    today = current_date()
    first = today.replace(day=1)
    last_month = first - datetime.timedelta(days=1)
    num_of_days = int(last_month.strftime('%d'))
    date = last_month.strftime('%Y-%m-')
    past_dates_list = generate_dates(date, num_of_days)
    return past_dates_list

def current_dates():
    today = current_date()
    num_of_days = int(today.strftime('%d'))
    date = today.strftime('%Y-%m-')
    current_dates_list = generate_dates(date, num_of_days)
    return current_dates_list

def create_graph(graph_title, current_data, past_data, y_label, position):
    plt.subplot(position)
    plt.plot(current_data, label='Current month')
    plt.plot(past_data, label='Last month')
    plt.ylabel(y_label)
    plt.xlabel('Days in month')
    plt.legend(fancybox=True, prop={'size': 6})
    plt.title(graph_title)
    plt.grid(True)
