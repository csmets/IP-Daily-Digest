""" This file is used to create the graphs for the 4 different stats """

import json
import matplotlib.pyplot as plt
from graphs.generate_graph_functions import current_dates, past_month_dates, create_graph

def generate_graphs(category, rir, path, filename):
    """ Function that will create 4 different graphs """

    delegations_file = ""

    rirs = [
        'global',
        'afrinic',
        'apnic',
        'arin',
        'lacnic',
        'ripencc'
    ]

    if rir in rirs:
        if rir == 'global':
            delegations_file = path + 'archives/' + rir + '-delegations.json'
        else:
            delegations_file = path + rir + '-delegations.json'
    else:
        return False

    with open(delegations_file) as file_data:

        data = json.load(file_data)

        dates = current_dates()
        past_dates = past_month_dates()

        allocated = []
        allocated_past = []
        assigned = []
        assigned_past = []
        available = []
        available_past = []
        reserved = []
        reserved_past = []

        for d in dates:
            allocated.append(data[d][category]['allocated'])
            assigned.append(data[d][category]['assigned'])
            available.append(data[d][category]['available'])
            reserved.append(data[d][category]['reserved'])

        for pd in past_dates:
            allocated_past.append(data[pd][category]['allocated'])
            assigned_past.append(data[pd][category]['assigned'])
            available_past.append(data[pd][category]['available'])
            reserved_past.append(data[pd][category]['reserved'])

        plt.figure(figsize=(10, 10), dpi=120)

        if category == 'ipv4':
            plt.suptitle('IPv4 Delegation Stats')
        elif category == 'ipv6':
            plt.suptitle('IPv6 Delegation Stats')

        create_graph(
            'Allocated',
            allocated,
            allocated_past,
            'Number of block Allocated',
            221
        )

        create_graph(
            'Assigned',
            assigned,
            assigned_past,
            'Number of block Assigned',
            222
        )

        create_graph(
            'Available',
            available,
            available_past,
            'Number of block Available',
            223
        )

        create_graph(
            'Reserved',
            reserved,
            reserved_past,
            'Number of block Reserved',
            224
        )
        plt.savefig(path + filename)
