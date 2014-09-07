import re
import logging
import datetime
from myVaporsRecords import VapeRecord


def parse_record(record):
    """
    Parse a single record

    The .dat file contains all imported records
    A record is 8 byte - there is no separator between records (records have fixed length)

    Record Format Documentation:
    in groups of 4 (just for readability)

    Duuy yyyy mmmm dddd HHHH HHHH MMMM MMMM xyss ssss rrrr rrrr vvvv vvvv zzzz zzzz

    D = 'dayBit' - day is only 4 bits (0 - 15) so the dayBit adds another 16 days to complete a month
    u = unknown (maybe they belong to year, but i'm not sure, so they are unknown for now
    y = year (5 bits)
    m = month (4 bits)
    d = day (4 bits)
    H = hour (8 bits)
    M = minute (8 bits)
    x = MvrVV
    y = MvrVW
    s = seconds (6 bits)
    r = resistance * 10 (8 bits) - handled as int - divide by 10 for float value
    v = voltage * 10 (8 bits) - handled as int - divide by 10 for float value
    z = duration * 10 (8 bits) - handled as int - divide by 10 for float value

    :param record: single 8 byte record
    :rtype: VapeRecord
    """
    _log = logging.getLogger('myVaporsRecords.parser')

    if len(record) < 8:  # fail if less than 8 bytes remaining (handles EOF)
        raise ValueError('record less than 8 bytes')

    record_bin = ''.join(['{0:08b}'.format(ord(c)) for c in record])  # convert record to a 64 char bit string

    _log.debug(record_bin)

    # regex to read all known values into a dict
    # for those who are unfamiliar with pythons re syntax:
    #
    # ?P<resistance>\d{8}) => take 8 digits and save them as named key 'resistance'
    #
    regex = r'(?P<dayBit>\d)' \
            '(?P<unknown>\d{2})' \
            '(?P<year>\d{5})' \
            '(?P<month>\d{4})' \
            '(?P<day>\d{4})' \
            '(?P<hour>\d{8})' \
            '(?P<minute>\d{8})' \
            '(?P<MvrVV>\d)' \
            '(?P<MvrVW>\d)' \
            '(?P<second>\d{6})' \
            '(?P<resistance>\d{8})' \
            '(?P<voltage>\d{8})' \
            '(?P<duration>\d{8})'

    record_dict = re.match(regex, record_bin).groupdict()

    # convert binary values to integers
    # voltage, duration and resistance will be divided by 10 to get their actual values
    for key, value in record_dict.iteritems():
        if key in ['voltage', 'duration', 'resistance']:
            record_dict[key] = float(int(value, 2)) / 10
        else:
            record_dict[key] = int(value, 2)

    # add 16 days if dayBit is set
    # day is only 4 bits (0 - 15) so the 'dayBit' adds another 16 days to complete a month
    if record_dict['dayBit'] == 1:
        record_dict['day'] += 16
    record_dict.pop('dayBit', None)

    # year is starting at 2000 - so we have to add 2000 years for the actual date
    record_dict['year'] += 2000

    vape_date = datetime.datetime(record_dict['year'], record_dict['month'], record_dict['day'], record_dict['hour'],
                                  record_dict['minute'], record_dict['second'])

    return VapeRecord(vape_date, record_dict['resistance'], record_dict['voltage'], record_dict['duration'])


def parse_file(database_file):
    """
    read a file containing records without any separator (like myVapors .dat file)

    the returned records are sorted by date (this is done by myVapors after import)

    :param file filename:
    :rtype: list[VapeRecord]
    """

    record_list = []

    while True:
        record = database_file.read(8)  # one record is 8 bytes

        if len(record) < 8:
            break

        record_list.append(parse_record(record))

    return record_list