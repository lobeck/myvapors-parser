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

    D = 'dayBit' - day is only 4 bits (0 - 15) so the dayBit adds another 16 days to handle a full month
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
    if len(record) < 8:  # fail if less than 8 bytes remaining (handles EOF)
        raise ValueError('record less than 8 bytes')

    # split the record in 8 byte/integers
    _record = [ord(byte) for byte in record]

    # the year is in the least significant 5 bits of the first byte
    year = _record[0] & 31  # AND with 00011111
    year += 2000  # year is only 5 bits (max. 32 years), so add the missing 2000 years

    # the month is in the most significant 4 bits of the second byte
    month = (_record[1] & 240) >> 4  # AND with 11110000, then shift 4 bit to the right (will make 00001111)

    # day is a bit tricky, since the MSB of the first byte is an additional bit (see 'dayBit' above)
    # in python: if dayBit == 1: day += 16
    #
    # first AND with 15 = 00001111 to get the 4 day bits
    #
    # then get the 'dayBit', which is the highest bit in the first byte of a record 128 = 10000000 using AND
    # next shift it 3 bits to the right to set it as the 5th bit
    # finally OR both values to make the day 5 bits (32 days)
    day = (_record[1] & 15) | ((_record[0] & 128) >> 3)

    # the hour is in the third byte
    hour = _record[2]

    # the minute is the fourth byte
    minute = _record[3]

    # MvrVV is the MSB of the fifth byte
    mvrvv = _record[4] & 128 == 128  # AND with 10000000 (128 when set, 0 when unset)

    # MvrVW is the second bit of the fifth byte
    mvrvw = _record[4] & 64 == 64  # AND with 01000000 (64 when set, 0 when unset)

    # seconds are in the 6 LSB of the fifth byte
    second = _record[4] & 63  # AND with 00111111

    # resistance is the sixth byte and multiplied by 10 to allow 1/10 ohm accuracy
    resistance = float(_record[5]) / 10

    # voltage is the seventh byte and multiplied by 10 to allow 1/10 volt accuracy
    voltage = float(_record[6]) / 10

    # duration is the eighth byte and multiplied by 10 to allow 1/10 second accuracy
    duration = float(_record[7]) / 10

    vape_date = datetime.datetime(year, month, day, hour, minute, second)

    return VapeRecord(vape_date, resistance, voltage, duration)


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

        if record == '\xff\xff\xff\xff\xff\xff\xff\xff':
            break

        if record == '\x00\x00\x00\x00\x00\x00\x00\x00':
            break

        record_list.append(parse_record(record))

    return record_list
