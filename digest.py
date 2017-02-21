""" Global IP Daily Digest for historic keeping """

def read_lines(func, lines, return_val, start_at=0):

    relevant_lines = lines[start_at:]

    for line in relevant_lines:
        return_val = func(line, return_val)

    return return_val

def get_line_values(line, line_values):
    """ Calculate the values found in the line """
    values = line.split('|')
    # Get type (ipv4, ipv6 or asn)
    stat_type = values[2]

    # Type of record from the set {available, allocated, assigned, reserved}
    status = values[6].replace('\n', '')

    # Count number of same status under the specific type
    summed = line_values[stat_type][status] + 1
    line_values[stat_type][status] = summed

    if stat_type == 'ipv4':
        line_values[stat_type]['hosts'] = (
            line_values[stat_type]['hosts'] + int(values[4])
        )

    if stat_type == 'asn':
        line_values[stat_type]['given'] = (
            line_values[stat_type]['given'] + int(values[4])
        )

    return line_values

def make_stats_dict():
    """ Create a dictionary to hold the stats data """

    ipv4_stats = (
        {
            'available': 0,
            'allocated': 0,
            'assigned': 0,
            'reserved': 0,
            'hosts': 0
        }
    )

    ipv6_stats = (
        {
            'available': 0,
            'allocated': 0,
            'assigned': 0,
            'reserved': 0
        }
    )

    asn_stats = (
        {
            'available': 0,
            'allocated': 0,
            'assigned': 0,
            'reserved': 0,
            'given': 0
        }
    )

    stats_dict = (
        {
            'ipv4': ipv4_stats,
            'ipv6': ipv6_stats,
            'asn': asn_stats
        }
    )

    return stats_dict

def gather_rir_stats():
    """ Fetch all 5 RIR data and return them as a dictionary """
    rirs_results = {}
    rirs_results['afrinic'] = collect_stats(
        'delegated-afrinic-extended.txt', 4)

    rirs_results['apnic'] = collect_stats(
        'delegated-apnic-extended.txt', 31)

    rirs_results['arin'] = collect_stats(
        'delegated-arin-extended.txt', 4)

    rirs_results['lacnic'] = collect_stats(
        'delegated-lacnic-extended.txt', 4)

    rirs_results['ripe'] = collect_stats(
        'delegated-ripencc-extended.txt', 4)

    return rirs_results

def collect_stats(url, start_pos):
    delegated_raw = open(url, 'r+')
    delegated_lines = delegated_raw.readlines()
    stat_dict = make_stats_dict()
    return read_lines(get_line_values, delegated_lines, stat_dict, start_pos)

def global_stats(rirs_dict):
    global_dict = make_stats_dict()

    result = merge_rir_stats_to_global(rirs_dict, global_dict)

    return result

def sum_items(obj1, obj2, key, item):
    obj1[key][item] = obj1[key][item] + obj2[key][item]
    return obj1

def merge_rir_stats_to_global(r, g, i=0):
    """ merge the data from the rir into the global stats dict """

    rir_list = ['afrinic', 'apnic', 'arin', 'lacnic', 'ripe']

    if i < len(r):
        g = sum_items(g, r[rir_list[i]], 'ipv4', 'allocated')
        g = sum_items(g, r[rir_list[i]], 'ipv4', 'available')
        g = sum_items(g, r[rir_list[i]], 'ipv4', 'assigned')
        g = sum_items(g, r[rir_list[i]], 'ipv4', 'reserved')
        g = sum_items(g, r[rir_list[i]], 'ipv4', 'hosts')

        g = sum_items(g, r[rir_list[i]], 'ipv6', 'allocated')
        g = sum_items(g, r[rir_list[i]], 'ipv6', 'available')
        g = sum_items(g, r[rir_list[i]], 'ipv6', 'assigned')
        g = sum_items(g, r[rir_list[i]], 'ipv6', 'reserved')

        g = sum_items(g, r[rir_list[i]], 'asn', 'allocated')
        g = sum_items(g, r[rir_list[i]], 'asn', 'available')
        g = sum_items(g, r[rir_list[i]], 'asn', 'assigned')
        g = sum_items(g, r[rir_list[i]], 'asn', 'reserved')
        g = sum_items(g, r[rir_list[i]], 'asn', 'given')

        return merge_rir_stats_to_global(r, g, i + 1)

    return g

rirs = gather_rir_stats()
global_results = global_stats(rirs)
print('GLOBAL: ', global_results)
