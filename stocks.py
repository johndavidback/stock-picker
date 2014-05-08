#!/usr/bin/python

import sys
from pprint import pprint

import ystockquote
from dateutil.relativedelta import relativedelta


for quote in sys.argv[1:]:
    print 'Finding quote for %s' % quote

    # First thing we want is some basic information on the quote.
    details = ystockquote.get_all(quote)

    print 'Last Open: $%s' % details.get('today_open')
    print 'Today\'s Change: %s' % ystockquote.get_todays_value_change(quote).split(' ')[2].rstrip('"')






    print ''
