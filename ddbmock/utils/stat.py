# -*- coding: utf-8 -*-

from time import time, ctime
from collections import namedtuple
import atexit, logging

null_logger = logging.getLogger(__name__)
null_logger.addHandler(logging.NullHandler())


def average(data):
    return sum(data)/len(data)

class Stat(object):
    def __init__(self, name, resolution_interval=1, aggregation_interval=5*60, logger=null_logger):
        """
        :param name: name of the measured parameter
        :param resolution_interval: all data accumulated in this slot are part of the same point
        :param aggregation_interval: aggregates data on this period. Must be bigger than ``resolution_interval``
        """

        # Load params
        self.name=name
        self.resolution_interval = resolution_interval
        self.aggregation_interval = aggregation_interval
        self.log = logger

        # Set internal state
        self.current_point_time = int(time())
        self.current_point_list = []
        self.current_point_value = 0
        self.last_aggregation_time = self.current_point_time

        # goodbye
        atexit.register(self.flush)

    def _macro_aggregate(self):
        """Perform aggregation every aggregation_interval"""
        # aggregate
        points = self.current_point_list

        interval = (self.current_point_time - self.last_aggregation_time) / 60.0
        self.log.info("%s: interval=%s min=%s max=%s average=%s",
                       self.name,
                       round(interval),
                       min(points),
                       max(points),
                       average(points))

        #reset
        self.current_point_list = []
        self.last_aggregation_time = int(time())

    def _aggregate(self):
        """Trigger aggregation and reset current data"""
        # aggregate
        self.current_point_list.append(self.current_point_value)

        # reset
        self.current_point_value = 0
        self.current_point_time = int(time())


    def push(self, value):
        """Push a data point

        :param value: value to push
        """
        current_time = int(time())

        # aggregate ?
        if self.current_point_time + self.current_point_time <= current_time:
            self._aggregate()
        if self.last_aggregation_time + self.aggregation_interval <= current_time:
            self._macro_aggregate()

        # update value
        self.current_point_value += value

    def flush(self):
        """Force all aggregations, reset internal state and print the results
        """

        self._aggregate()
        self._macro_aggregate()
