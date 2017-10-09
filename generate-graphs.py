""" Generate graphs for digests """

import json
import datetime
import matplotlib.pyplot as plt

def current_date():
    today = datetime.date.today()
    return today

def generate_dates(date, num_of_days):
    past_month_dates = []
    days = 0
    while days < num_of_days:
        days = days + 1
        if days < 10:
            day = '0' + str(days)
        else:
            day = str(days)

        past_month_dates.append(date + day)

    return past_month_dates

def past_month_dates():
    today = current_date()
    first = today.replace(day=1)
    last_month = first - datetime.timedelta(days=1)
    num_of_days = int(last_month.strftime('%d'))
    date = last_month.strftime('%Y-%m-')
    dates = generate_dates(date, num_of_days)
    return dates

def current_dates():
    today = current_date()
    num_of_days = int(today.strftime('%d'))
    date = today.strftime('%Y-%m-')
    dates = generate_dates(date, num_of_days)
    return dates

dates = current_dates()
past_dates = past_month_dates()

with open('archives/global-delegations.json') as json_data:
    data = json.load(json_data)
    assigned = []
    assigned_past = []

    for d in dates:
        assigned.append(data[d]['ipv4']['available'])
    plt.plot(assigned)

    for pd in past_dates:
        assigned_past.append(data[pd]['ipv4']['available'])
    plt.plot(assigned_past)

    plt.ylabel('Number of IP blocks Assigned')
    plt.xlabel('Days in month')
    plt.legend(['current month', 'last month'])
    plt.savefig('test.png')
