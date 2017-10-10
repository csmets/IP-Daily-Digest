""" This file is used to create the graphs for ipv4 statistics """

import json
import matplotlib.pyplot as plt
from generate_graph_functions import current_dates, past_month_dates, create_graph

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

    plt.figure(figsize=(10, 10), dpi=120)
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
    plt.savefig('graphs/figures/ipv4.png')
