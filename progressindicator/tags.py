"""This module contains all the built-in tags for progressindicator package.

.. data:: TAG_VALUE

   Refers to value passed via publish

.. data:: TAG_MIN_VALUE

   Refers to max_value attribute of the Progress bar

.. data:: TAG_MAX_VALUE

   Refers to min_value attribute of the Progress bar

.. data:: TAG_BEGIN_TIME

   Refers to the time at which begin was called

.. data:: TAG_END_TIME

   Refers to the time at which end was called

.. data:: TAG_ITERATIONS

   Refers to the number of calls that have been made to publish

.. data:: TAG_PERCENTAGE

   Refers to how much of the task has been completed in percentage

.. data:: TAG_TIME_SINCE_BEGIN

   Refers to the time(sec) since begin was called

.. data:: TAG_DELTATIME

   Refers to the time(sec) since publish was called

.. data:: TAG_LAST_UPDATED_AT

   Refers to the time at which Progress bar was last updated on screen.

.. data:: TAG_TIME_SINCE_UPDATE

   Refers to the time(sec) since the Progress bar was last updated on screen.

.. data:: TAG_ETA

   Refers to the expected time(s) the task would need to complete

.. data:: TAG_ETA_NEW

   Refers to an alternate implementation of expected time(s)
   the task would need to complete

.. data:: TAG_RATE

   Refers to current rate of calls to publish
"""
#Tags for built-in stats

TAG_VALUE = 'value'
TAG_MIN_VALUE = 'min_value'
TAG_MAX_VALUE = 'max_value'
TAG_BEGIN_TIME = 'begin_time'
TAG_END_TIME = 'end_time'
TAG_ITERATIONS = 'iterations'
TAG_PERCENTAGE = 'percentage'
TAG_TIME_SINCE_BEGIN = 'time_since_begin'
TAG_DELTATIME = 'deltatime'
TAG_LAST_UPDATED_AT = 'last_updated_at'
TAG_TIME_SINCE_UPDATE = 'time_since_update'

#Tags for built-in providers
TAG_ETA = 'eta'
TAG_ETA_NEW = 'eta_new'
TAG_RATE = 'rate'
