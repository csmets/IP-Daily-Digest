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

ipv4_stats = (
    {'available': 0, 'allocated': 0, 'assigned': 0, 'reserved': 0, 'hosts': 0}
)
ipv6_stats = {'available': 0, 'allocated': 0, 'assigned': 0, 'reserved': 0}
asn_stats = (
    {'available': 0, 'allocated': 0, 'assigned': 0, 'reserved': 0, 'given': 0}
)
stats = {'ipv4': ipv4_stats, 'ipv6': ipv6_stats, 'asn': asn_stats}

afrinic_delegated_raw = open('delegated-afrinic-extended.txt', 'r+')
afrinic_delegated_lines = afrinic_delegated_raw.readlines()
afrinic = read_lines(get_line_values, afrinic_delegated_lines, stats, 4)
print('AFRINIC: ', afrinic)

apnic_delegated_raw = open('delegated-apnic-extended.txt', 'r+')
apnic_delegated_lines = apnic_delegated_raw.readlines()
apnic = read_lines(get_line_values, apnic_delegated_lines, stats, 31)
print('APNIC: ', apnic)

arin_delegated_raw = open('delegated-arin-extended.txt', 'r+')
arin_delegated_lines = arin_delegated_raw.readlines()
arin = read_lines(get_line_values, arin_delegated_lines, stats, 4)
print('ARIN: ', arin)

lacnic_delegated_raw = open('delegated-lacnic-extended.txt', 'r+')
lacnic_delegated_lines = lacnic_delegated_raw.readlines()
lacnic = read_lines(get_line_values, lacnic_delegated_lines, stats, 4)
print('LACNIC: ', lacnic)

ripe_delegated_raw = open('delegated-ripencc-extended.txt', 'r+')
ripe_delegated_lines = ripe_delegated_raw.readlines()
ripe = read_lines(get_line_values, ripe_delegated_lines, stats, 4)
print('RIPENCC: ', ripe)
