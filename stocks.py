#!/usr/bin/python

import sys
from pprint import pprint
from datetime import datetime

import ystockquote
from dateutil.relativedelta import relativedelta


for quote in sys.argv[1:]:
    print 'Finding quote for %s' % quote

    # First thing we want is some basic information on the quote.
    details = ystockquote.get_all(quote)

    last_trade = float(ystockquote.get_last_trade_price(str(quote)))

    print 'Last Open: $%s' % details.get('today_open'), 'Last Trade: $%s' % last_trade
    print 'Today\'s Change: %s' % ystockquote.get_todays_value_change(quote).split(' ')[2].rstrip('"')

    days = 71

    today = datetime.today().strftime("%Y-%m-%d")
    fifty_ago = (datetime.today() - relativedelta(days=days)).strftime("%Y-%m-%d")

    prices = ystockquote.get_historical_prices(str(quote), fifty_ago, today)

    total = 0
    for d, p in prices.iteritems():
        numerator = float(p.get('High')) - float(p.get('Low'))
        total += numerator / float(p.get('Open'))

    volatility = round(total / len(prices), 4) * 100
    optional = ' !!! ' if volatility >= 3.0 else u''

    print 'Volatility: %s%% %s' % (volatility, optional)

    print 'Last 50 days'
    last_open = None
    total_change = 0
    for d, p in prices.iteritems():
        day_open = float(p.get('Open'))

        # Calculate the percentage change
        if last_open:
            change = str(round(day_open / last_open, 3)) + '%'

            if day_open > last_open:
                change = '+' + change
                total_change += round(day_open / last_open, 3)
            else:
                change = '-' + change
                total_change -= round(day_open / last_open, 3)
        else:
            change = ''

        last_open = day_open

        print '%s: %s %s' % (d, day_open, change)

    print total_change / len(prices)


    print ''
