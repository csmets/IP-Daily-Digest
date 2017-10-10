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
    plt.plot(current_data)
    plt.plot(past_data)
    plt.ylabel(y_label)
    plt.xlabel('Days in month')
    plt.legend(['current month', 'last month'])
    plt.title(graph_title)
    plt.grid(True)

with open('archives/global-delegations.json') as json_data:
    data = json.load(json_data)

    dates = current_dates()
    past_dates = past_month_dates()

    ipv4_allocated = []
    ipv4_allocated_past = []
    ipv4_assigned = []
    ipv4_assigned_past = []
    ipv4_available = []
    ipv4_available_past = []
    ipv4_reserved = []
    ipv4_reserved_past = []

    for d in dates:
        ipv4_allocated.append(data[d]['ipv4']['allocated'])
        ipv4_assigned.append(data[d]['ipv4']['assigned'])
        ipv4_available.append(data[d]['ipv4']['available'])
        ipv4_reserved.append(data[d]['ipv4']['reserved'])

    for pd in past_dates:
        ipv4_allocated_past.append(data[pd]['ipv4']['allocated'])
        ipv4_assigned_past.append(data[pd]['ipv4']['assigned'])
        ipv4_available_past.append(data[pd]['ipv4']['available'])
        ipv4_reserved_past.append(data[pd]['ipv4']['reserved'])

    plt.figure(1, figsize=(10, 10), dpi=120)
    create_graph(
        'Allocated',
        ipv4_allocated,
        ipv4_allocated_past,
        'Number of block Allocated',
        221
    )

    create_graph(
        'Assigned',
        ipv4_assigned,
        ipv4_assigned_past,
        'Number of block Assigned',
        222
    )

    create_graph(
        'Available',
        ipv4_available,
        ipv4_available_past,
        'Number of block Available',
        223
    )

    create_graph(
        'Reserved',
        ipv4_reserved,
        ipv4_reserved_past,
        'Number of block Reserved',
        224
    )
    plt.savefig('ipv4.png')
