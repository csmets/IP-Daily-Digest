""" Global IP Daily Digest for historic keeping """

import datetime
import json
import subprocess
import argparse
import requests

# CLI argument parser for setting path of files to write to.
parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--path', type=str, default='./', help='Path to project.')

dir_path = parser.parse_args().path

def get_ipv4_prefix(addresses):
    """ Get the prefix from the count of IP Addresses allocated """
    cidr = {
        '1': '/32',
        '2': '/31',
        '4': '/30',
        '8': '/29',
        '16': '/28',
        '32': '/27',
        '64': '/26',
        '128': '/25',
        '256': '/24',
        '512': '/23',
        '1024': '/22',
        '2048': '/21',
        '4096': '/20',
        '8192': '/19',
        '16384': '/18',
        '32768': '/17',
        '65536': '/16',
        '131072': '/15',
        '262144': '/14',
        '524288': '/13',
        '1048576': '/12',
        '2097152': '/11',
        '4194304': '/10',
        '8388608': '/9',
        '16777216': '/8',
        '33554432': '/7',
        '67108864': '/6',
        '134217728': '/5',
        '268435456': '/4',
        '536870912': '/3',
        '1073741824': '/2',
        '2147483648': '/1',
        '4294967296': '/0'
    }
    if addresses in cidr:
        return cidr[addresses]
    else:
        return 'other'

def read_lines(func, lines, return_val, start_at=0):

    relevant_lines = lines[start_at:]

    for line in relevant_lines:
        return_val = func(str(line), return_val)

    return return_val

def get_line_values(line, line_values):
    """ Calculate the values found in the line """

    values = line.split('|')

    # Get type (ipv4, ipv6 or asn)
    stat_type = values[2]

    # Get number of addresses allocated
    addresses = values[4]

    # Type of record from the set {available, allocated, assigned, reserved}
    status = values[6].replace('\n', '')
    status = values[6].replace("'", '') # LACNIC has a strange `'` in this value

    # Count number of same status under the specific type
    if stat_type == 'ipv4' or stat_type == 'ipv6':
        summed = line_values[stat_type][status]['total'] + 1
        line_values[stat_type][status]['total'] = summed
    else:
        summed = line_values[stat_type][status] + 1
        line_values[stat_type][status] = summed

    if stat_type == 'ipv4':

        v4prefix = get_ipv4_prefix(addresses)

        # Count the number of same prefixes
        prefix_summed = line_values[stat_type][status][v4prefix] + 1
        line_values[stat_type][status][v4prefix] = prefix_summed

    elif stat_type == 'ipv6':
        # IPv6 extended data shows prefix rather than number of addresses
        v6prefix = '/' + addresses

        if v6prefix in line_values[stat_type][status]:
            v6prefix_sum = line_values[stat_type][status][v6prefix] + 1
            line_values[stat_type][status][v6prefix] = v6prefix_sum
        else:
            other_sum = line_values[stat_type][status]['other'] + 1
            line_values[stat_type][status]['other'] = other_sum


    # Get specific stats
    if stat_type == 'ipv4':
        line_values[stat_type]['hosts'] = (
            line_values[stat_type]['hosts'] + int(addresses)
        )

    if stat_type == 'asn':
        line_values[stat_type]['given'] = (
            line_values[stat_type]['given'] + int(addresses)
        )

    return line_values

def make_ipv4_prefix_count():
    """ create a dictionary for ipv4 prefix. It's stored in a function to
    prevent python from instancing """

    ipv4_prefix_count = {
        'total': 0,
        'other': 0,
        '/32': 0,
        '/31': 0,
        '/30': 0,
        '/29': 0,
        '/28': 0,
        '/27': 0,
        '/26': 0,
        '/25': 0,
        '/24': 0,
        '/23': 0,
        '/22': 0,
        '/21': 0,
        '/20': 0,
        '/19': 0,
        '/18': 0,
        '/17': 0,
        '/16': 0,
        '/15': 0,
        '/14': 0,
        '/13': 0,
        '/12': 0,
        '/11': 0,
        '/10': 0,
        '/9': 0,
        '/8': 0,
        '/7': 0,
        '/6': 0,
        '/5': 0,
        '/4': 0,
        '/3': 0,
        '/2': 0,
        '/1': 0,
        '/0': 0
    }
    return ipv4_prefix_count

def make_ipv6_prefix_count():
    """ create a dictionary for ipv6 prefix. It's stored in a function to
    prevent python from instancing """

    ipv6_prefix_count = {
        'total': 0,
        'other': 0,
        '/24': 0,
        '/25': 0,
        '/26': 0,
        '/27': 0,
        '/28': 0,
        '/29': 0,
        '/30': 0,
        '/31': 0,
        '/32': 0,
        '/33': 0,
        '/34': 0,
        '/35': 0,
        '/36': 0,
        '/37': 0,
        '/38': 0,
        '/39': 0,
        '/40': 0,
        '/41': 0,
        '/42': 0,
        '/43': 0,
        '/44': 0,
        '/45': 0,
        '/46': 0,
        '/47': 0,
        '/48': 0,
        '/49': 0,
        '/50': 0,
        '/51': 0,
        '/52': 0,
        '/53': 0,
        '/54': 0,
        '/55': 0,
        '/56': 0,
        '/57': 0,
        '/58': 0,
        '/59': 0,
        '/60': 0,
        '/61': 0,
        '/62': 0,
        '/63': 0,
        '/64': 0
    }
    return ipv6_prefix_count

def make_stats_dict():
    """ Create a dictionary to hold the stats data """

    ipv4_stats = (
        {
            'available': make_ipv4_prefix_count(),
            'allocated': make_ipv4_prefix_count(),
            'assigned': make_ipv4_prefix_count(),
            'reserved': make_ipv4_prefix_count(),
            'hosts': 0
        }
    )

    ipv6_stats = (
        {
            'available': make_ipv6_prefix_count(),
            'allocated': make_ipv6_prefix_count(),
            'assigned': make_ipv6_prefix_count(),
            'reserved': make_ipv6_prefix_count()
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
        'https://ftp.apnic.net/stats/afrinic/delegated-afrinic-extended-latest', 4)

    rirs_results['apnic'] = collect_stats(
        'https://ftp.apnic.net/stats/apnic/delegated-apnic-extended-latest', 31)

    rirs_results['arin'] = collect_stats(
        'https://ftp.apnic.net/stats/arin/delegated-arin-extended-latest', 4)

    rirs_results['lacnic'] = collect_stats(
        'https://ftp.apnic.net/stats/lacnic/delegated-lacnic-extended-latest', 4)

    rirs_results['ripe'] = collect_stats(
        'https://ftp.apnic.net/stats/ripe-ncc/delegated-ripencc-extended-latest', 4)

    return rirs_results

def collect_stats(url, start_pos):
    req = requests.get(url, stream=True, timeout=900)
    delegated_lines = list(req.iter_lines())
    stat_dict = make_stats_dict()
    return read_lines(get_line_values, delegated_lines, stat_dict, start_pos)

def global_stats(rirs_dict):
    global_dict = make_stats_dict()

    result = merge_rir_stats_to_global(rirs_dict, global_dict)

    return result

def sum_items(obj1, obj2, key, item):
    if isinstance(obj1[key][item], dict):
        for k in obj1[key][item]:
            obj1[key][item][k] = obj1[key][item][k] + obj2[key][item][k]
    else:
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

def ppnum(value):
    """ pretty print number """
    pp = "{:,}".format(value)
    return pp

def compare_results(value1, value2):
    """ Compare results and return a string showing the difference """
    if value1 is not None and value2 is not None:
        difference = value1 - value2

        if difference > 0:
            result = " ▲ +" + str(difference)
        elif difference < 0:
            result = " ▼ " + str(difference)
        else:
            result = ""
    else:
        result = ""

    return result

def create_slash_range(start, end, result):
    if start >= end:
        result.append('/' + str(start))
        start = start - 1
        return create_slash_range(start, end, result)

    else:
        return result

def markdown_summed_report(report):
    """ Create quick summary report """
    now = datetime.datetime.now()
    markdown = ""
    markdown += "```\n"
    markdown += now.strftime('%Y-%m-%d')
    markdown += "\n==========\n"
    markdown += "IPv4 |"
    markdown += " Allocated: " + ppnum(report['ipv4']['allocated']['total'])
    markdown += " Assigned: " + ppnum(report['ipv4']['assigned']['total'])
    markdown += " Available: " + ppnum(report['ipv4']['available']['total'])
    markdown += " Reserved: " + ppnum(report['ipv4']['reserved']['total'])
    markdown += " Hosts: " + ppnum(report['ipv4']['hosts'])
    markdown += "\n"
    markdown += "IPv6 |"
    markdown += " Allocated: " + ppnum(report['ipv6']['allocated']['total'])
    markdown += " Assigned: " + ppnum(report['ipv6']['assigned']['total'])
    markdown += " Available: " + ppnum(report['ipv6']['available']['total'])
    markdown += " Reserved: " + ppnum(report['ipv6']['reserved']['total'])
    markdown += "\n"
    markdown += "ASN  |"
    markdown += " Allocated: " + ppnum(report['asn']['allocated'])
    markdown += " Assigned: " + ppnum(report['asn']['assigned'])
    markdown += " Available: " + ppnum(report['asn']['available'])
    markdown += " Reserved: " + ppnum(report['asn']['reserved'])
    markdown += " Given: " + ppnum(report['asn']['given'])
    markdown += "\n"
    markdown += "```\n"

    return markdown

def create_report_table(stats, previous_stats, slash_range):
    """ Create a report table for a stat type i.e. ipv4 / ipv6 """

    markdown = "| Prefix | Allocated | Assigned | Available | Reserved |\n"
    markdown += "| ----- | ----- | ----- | ----- | ----- |\n"

    report_types = ['allocated', 'assigned', 'available', 'reserved']

    for slash in slash_range:
        markdown += "| " + slash
        for rt in report_types:
            if previous_stats is not None:
                result = compare_results(
                    stats[rt][slash],
                    previous_stats[rt][slash]
                )
            else:
                result = ""

            markdown += " | " + ppnum(stats[rt][slash]) + result

        markdown += " |\n"

    # create row for totals
    markdown += "| **Total**"
    for rt in report_types:
        if previous_stats is not None:
            result = compare_results(
                stats[rt]['total'],
                previous_stats[rt]['total']
            )
        else:
            result = ""

        markdown += " | **" + ppnum(stats[rt]['total']) + result + "**"
    markdown += " |\n"

    return markdown

def markdown_report(report, previous_report):
    """ Create a lovely string in markdown format of the stats report """
    now = datetime.datetime.now()
    markdown = "## Digest for " + now.strftime('%Y-%m-%d') + "\n"
    markdown += markdown_summed_report(report)
    markdown += "\n### Detailed Report\n\n"
    markdown += "### IPv4\n\n"

    if previous_report is not None:
        hosts_difference = (
            compare_results(report['ipv4']['hosts'],
                            previous_report['ipv4']['hosts']))
    else:
        hosts_difference = ""

    markdown += (
        "#### Hosts: **" + ppnum(report['ipv4']['hosts']) +
        hosts_difference + "**\n\n")

    ipv4_slash_range = create_slash_range(30, 8, [])

    markdown += create_report_table(
        report['ipv4'],
        previous_report['ipv4'] if previous_report is not None else None,
        ipv4_slash_range)

    markdown += "\n### IPv6\n\n"
    ipv6_slash_range = create_slash_range(64, 24, [])

    markdown += create_report_table(
        report['ipv6'],
        previous_report['ipv6'] if previous_report is not None else None,
        ipv6_slash_range)

    return markdown

def get_previous_report(filename):
    with open(filename, 'r+') as f:
        content = f.read()
        json_obj = json.loads(content)
        yesterday = str(datetime.date.today() - datetime.timedelta(days=1))
        if yesterday in json_obj:
            return json_obj[yesterday]
        else:
            return None

def write_daily_digest(filename, stats_results, previous_report):
    with open(filename, 'r+') as f:
        digest_content = f.read()
        digest_split = digest_content.split('---')
        digest_header = digest_split[0]
        updated_digest_body = markdown_report(stats_results, previous_report)
        divider = "---\n\n"
        updated_digest = (
            digest_header + divider + updated_digest_body)
        f.seek(0)
        f.write(updated_digest)
        f.truncate()

def make_non_extended_stats(stats_data):
    """ Simple, non-elaborate stats for graphs """
    result = {}
    result['asn'] = stats_data['asn']

    ipv4_totals = {}
    ipv4_totals['allocated'] = stats_data['ipv4']['allocated']['total']
    ipv4_totals['assigned'] = stats_data['ipv4']['assigned']['total']
    ipv4_totals['available'] = stats_data['ipv4']['available']['total']
    ipv4_totals['hosts'] = stats_data['ipv4']['hosts']
    ipv4_totals['reserved'] = stats_data['ipv4']['reserved']['total']

    result['ipv4'] = ipv4_totals

    ipv6_totals = {}
    ipv6_totals['allocated'] = stats_data['ipv6']['allocated']['total']
    ipv6_totals['assigned'] = stats_data['ipv6']['assigned']['total']
    ipv6_totals['available'] = stats_data['ipv6']['available']['total']
    ipv6_totals['reserved'] = stats_data['ipv6']['reserved']['total']

    result['ipv6'] = ipv6_totals

    return result

def write_json(jsonfile, stats_data):
    with open(jsonfile, 'r+') as jf:
        json_content = jf.read()
        json_obj = json.loads(json_content)
        current_date = datetime.datetime.now()
        date_string = current_date.strftime('%Y-%m-%d')
        json_obj[date_string] = stats_data
        jf.seek(0)
        jf.write(json.dumps(json_obj, sort_keys=True, indent=4))
        jf.truncate()

rirs = gather_rir_stats()
global_results = global_stats(rirs)

# Write Global Stats
write_daily_digest(
    dir_path + 'README.md',
    global_results,
    get_previous_report('archives/global-delegations-extended.json'))

write_json(dir_path + 'archives/global-delegations-extended.json', global_results)
write_json(
    dir_path + 'archives/global-delegations.json',
    make_non_extended_stats(global_results)
)


# AFRINIC Digest
write_daily_digest(
    dir_path + 'archives/AFRINIC/README.md',
    rirs['afrinic'],
    get_previous_report('archives/AFRINIC/afrinic-delegations-extended.json'))

write_json(dir_path + 'archives/AFRINIC/afrinic-delegations-extended.json', rirs['afrinic'])
write_json(
    dir_path + 'archives/AFRINIC/afrinic-delegations.json',
    make_non_extended_stats(rirs['afrinic']))

# APNIC Digest
write_daily_digest(
    dir_path + 'archives/APNIC/README.md',
    rirs['apnic'],
    get_previous_report('archives/APNIC/apnic-delegations-extended.json'))

write_json(dir_path + 'archives/APNIC/apnic-delegations-extended.json', rirs['apnic'])
write_json(
    dir_path + 'archives/APNIC/apnic-delegations.json',
    make_non_extended_stats(rirs['apnic']))

# ARIN Digest
write_daily_digest(
    dir_path + 'archives/ARIN/README.md',
    rirs['arin'],
    get_previous_report('archives/ARIN/arin-delegations-extended.json'))

write_json(dir_path + 'archives/ARIN/arin-delegations-extended.json', rirs['arin'])
write_json(
    dir_path + 'archives/ARIN/arin-delegations.json',
    make_non_extended_stats(rirs['arin']))

# LACNIC Digest
write_daily_digest(
    dir_path + 'archives/LACNIC/README.md',
    rirs['lacnic'],
    get_previous_report('archives/LACNIC/lacnic-delegations-extended.json'))

write_json(dir_path + 'archives/LACNIC/lacnic-delegations-extended.json', rirs['lacnic'])
write_json(
    dir_path + 'archives/LACNIC/lacnic-delegations.json',
    make_non_extended_stats(rirs['lacnic']))

# RIPE NCC Digest
write_daily_digest(
    dir_path + 'archives/RIPE_NCC/README.md',
    rirs['ripe'],
    get_previous_report('archives/RIPE_NCC/ripencc-delegations-extended.json'))

write_json(dir_path + 'archives/RIPE_NCC/ripencc-delegations-extended.json', rirs['ripe'])
write_json(
    dir_path + 'archives/RIPE_NCC/ripencc-delegations.json',
    make_non_extended_stats(rirs['ripe']))

# Add updated daily digest
print("Git adding new digest...")
proc = subprocess.Popen(
    ["/usr/bin/git", "add", "."],
    stdout=subprocess.PIPE
)
print(proc.stdout.read())

# Commit updates
print("Git committing new world order...")
proc = subprocess.Popen(
    ["/usr/bin/git", "commit", '-m "Added new IP daily digest"'],
    stdout=subprocess.PIPE
)
print(proc.stdout.read())

# Push them to the fans
print("Git pushing boulders...")
proc = subprocess.Popen(
    ["/usr/bin/git", "push"],
    stdout=subprocess.PIPE
)
print(proc.stdout.read())
