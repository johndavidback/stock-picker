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

    days = 70

    today = datetime.today().strftime("%Y-%m-%d")
    fifty_ago = (datetime.today() - relativedelta(days=days)).strftime("%Y-%m-%d")

    prices = ystockquote.get_historical_prices(str(arg), fifty_ago, today)

    total = 0
    for d, p in prices.iteritems():
        numerator = float(p.get('High')) - float(p.get('Low'))
        total += numerator / float(p.get('Open'))

    volatility = round(total / len(prices), 4) * 100
    optional = ' !!! ' if volatility >= 3.0 else u''

    last_trade = float(ystockquote.get_last_trade_price(str(arg)))
    print '%s: %s%% ($%s) %s' % (arg, volatility, last_trade, optional)


    print ''
