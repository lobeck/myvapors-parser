class VapeRecord(object):
    def __init__(self, vape_date, resistance, voltage, duration):
        """

        :param datetime vape_date: datetime of vape
        :param float resistance: vaporizer resistance in ohm
        :param float voltage: voltage of this vape
        :param float duration:
        """
        self.vape_date = vape_date
        self.resistance = resistance
        self.voltage = voltage
        self.duration = duration

    def as_dict(self):
        """

        return object elements as dict - just for beauty (returns self.__dict__)
        :return: dict
        """
        return self.__dict__

    def csv(self):
        return ','.join([self.vape_date.date().isoformat(),
                         self.vape_date.time().isoformat(),
                         str(self.resistance),
                         str(self.voltage),
                         str(self.duration)
        ])