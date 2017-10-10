""" This file is used to create the graphs for ipv6 statistics """

import json
import matplotlib.pyplot as plt
from generate_graph_functions import current_dates, past_month_dates, create_graph

with open('archives/global-delegations.json') as json_data:
    data = json.load(json_data)

    dates = current_dates()
    past_dates = past_month_dates()

    ipv6_allocated = []
    ipv6_allocated_past = []
    ipv6_assigned = []
    ipv6_assigned_past = []
    ipv6_available = []
    ipv6_available_past = []
    ipv6_reserved = []
    ipv6_reserved_past = []

    for d in dates:
        ipv6_allocated.append(data[d]['ipv6']['allocated'])
        ipv6_assigned.append(data[d]['ipv6']['assigned'])
        ipv6_available.append(data[d]['ipv6']['available'])
        ipv6_reserved.append(data[d]['ipv6']['reserved'])

    for pd in past_dates:
        ipv6_allocated_past.append(data[pd]['ipv6']['allocated'])
        ipv6_assigned_past.append(data[pd]['ipv6']['assigned'])
        ipv6_available_past.append(data[pd]['ipv6']['available'])
        ipv6_reserved_past.append(data[pd]['ipv6']['reserved'])

    plt.figure(figsize=(10, 10), dpi=120)
    create_graph(
        'Allocated',
        ipv6_allocated,
        ipv6_allocated_past,
        'Number of block Allocated',
        221
    )

    create_graph(
        'Assigned',
        ipv6_assigned,
        ipv6_assigned_past,
        'Number of block Assigned',
        222
    )

    create_graph(
        'Available',
        ipv6_available,
        ipv6_available_past,
        'Number of block Available',
        223
    )

    create_graph(
        'Reserved',
        ipv6_reserved,
        ipv6_reserved_past,
        'Number of block Reserved',
        224
    )
    plt.savefig('graphs/figures/ipv6.png')
