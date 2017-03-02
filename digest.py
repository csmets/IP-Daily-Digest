""" Global IP Daily Digest for historic keeping """

from datetime import datetime
import json
import subprocess
import requests
import argparse

# CLI argument parser for setting path of files to write to.
parser = argparse.ArgumentParser(description='Process some integers.')
parser.add_argument('--path', type=str, default='./', help='Path to project.')

dir_path = parser.parse_args()

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

    # Type of record from the set {available, allocated, assigned, reserved}
    status = values[6].replace('\n', '')
    status = values[6].replace("'", '') # LACNIC has a strange `'` in this value

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

def markdown_report(report):
    """ Create a lovely string in markdown format of the stats report """
    now = datetime.now()
    markdown = "```\n"
    markdown += now.strftime('%Y-%m-%d')
    markdown += "\n==========\n"
    markdown += "IPv4 |"
    markdown += " Allocated: " + ppnum(report['ipv4']['allocated'])
    markdown += " Assigned: " + ppnum(report['ipv4']['assigned'])
    markdown += " Available: " + ppnum(report['ipv4']['available'])
    markdown += " Reserved: " + ppnum(report['ipv4']['reserved'])
    markdown += " Hosts: " + ppnum(report['ipv4']['hosts'])
    markdown += "\n"
    markdown += "IPv6 |"
    markdown += " Allocated: " + ppnum(report['ipv6']['allocated'])
    markdown += " Assigned: " + ppnum(report['ipv6']['assigned'])
    markdown += " Available: " + ppnum(report['ipv6']['available'])
    markdown += " Reserved: " + ppnum(report['ipv6']['reserved'])
    markdown += "\n"
    markdown += "ASN  |"
    markdown += " Allocated: " + ppnum(report['asn']['allocated'])
    markdown += " Assigned: " + ppnum(report['asn']['assigned'])
    markdown += " Available: " + ppnum(report['asn']['available'])
    markdown += " Reserved: " + ppnum(report['asn']['reserved'])
    markdown += " Given: " + ppnum(report['asn']['given'])
    markdown += "\n"
    markdown += "```"

    return markdown

def write_daily_digest(filename, stats_results):
    with open(filename, 'r+') as f:
        digest_content = f.read()
        digest_split = digest_content.split('---')
        digest_header = digest_split[0]
        digest_body = digest_split[1]
        updated_digest_body = (
            markdown_report(stats_results) + digest_body)
        divider = "---\n\n"
        updated_digest = (
            digest_header + divider + updated_digest_body)
        f.seek(0)
        f.write(updated_digest)
        f.truncate()

def write_json(jsonfile, stats_data):
    with open(jsonfile, 'r+') as jf:
        json_content = jf.read()
        json_obj = json.loads(json_content)
        current_date = datetime.now()
        date_string = current_date.strftime('%Y-%m-%d')
        json_obj[date_string] = stats_data
        jf.seek(0)
        jf.write(json.dumps(json_obj, sort_keys=True, indent=4))
        jf.truncate()

rirs = gather_rir_stats()
global_results = global_stats(rirs)

# Write Global Stats
write_daily_digest(dir_path + 'README.md', global_results)
write_json(dir_path + 'archives/global-delegations.json', global_results)

# AFRINIC Digest
write_daily_digest(dir_path + 'archives/AFRINIC/README.md', rirs['afrinic'])
write_json(dir_path + 'archives/AFRINIC/afrinic-delegations.json', rirs['afrinic'])

# APNIC Digest
write_daily_digest(dir_path + 'archives/APNIC/README.md', rirs['apnic'])
write_json(dir_path + 'archives/APNIC/apnic-delegations.json', rirs['apnic'])

# ARIN Digest
write_daily_digest(dir_path + 'archives/ARIN/README.md', rirs['arin'])
write_json(dir_path + 'archives/ARIN/arin-delegations.json', rirs['arin'])

# LACNIC Digest
write_daily_digest(dir_path + 'archives/LACNIC/README.md', rirs['lacnic'])
write_json(dir_path + 'archives/LACNIC/lacnic-delegations.json', rirs['lacnic'])

# RIPE NCC Digest
write_daily_digest(dir_path + 'archives/RIPE_NCC/README.md', rirs['ripe'])
write_json(dir_path + 'archives/RIPE_NCC/ripencc-delegations.json', rirs['ripe'])

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
