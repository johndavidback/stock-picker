#!/usr/bin/python

import sys
from pprint import pprint
from datetime import datetime

import ystockquote
from dateutil.relativedelta import relativedelta
from urllib2 import HTTPError

def ben_graham(eps, next_eps, bond_yield=4.24):
    """
    Gets, or tries to get, the intrinsic value of a stock based on it's ttm EPS and the corporate
    bond yield.
    """
    # growth_rate = (next_eps - eps) / eps
    # growth_rate *= 100
    growth_rate = next_eps

    # The top part of the fraction: EPS x (8.5 + 2g) x 4.4
    numerator = eps * (8.5 + (2 * growth_rate)) * 4.4
    iv = numerator / bond_yield

    return round(iv, 3)


def get_volatility(quote, days=70):
    """
    Get the volatility based on this fun formula from Brandon
    """
    today = datetime.today().strftime("%Y-%m-%d")
    fifty_ago = (datetime.today() - relativedelta(days=days)).strftime("%Y-%m-%d")
    
    try:
        prices = ystockquote.get_historical_prices(str(quote), fifty_ago, today)
    except HTTPError:
        return 0

    total = 0
    for d, p in prices.iteritems():
        numerator = float(p.get('High')) - float(p.get('Low'))
        total += numerator / float(p.get('Open'))

    volatility = round(total / len(prices), 4) * 100

    return volatility

undervalued_stocks = []
ignore_dividend_stocks = []

for quote in sys.argv[1:]:
    # Let's set up some basic criteria to see if this is a stock that
    # warrants further inspection. These will be boolean markers we'll flip on 
    # if it makes sense.
    DIVIDEND_YIELD = False  # Let's say we want this >= %1
    DESIRED_DIVIDEND_RATE = 1

    # Relative Intrinsic value
    RIV_RATIO = False  # Let's say we want this > 1.00
    DESIRED_RIV_RATE = 1

    VOLATILITY = False  # Let's say we want this > 2.0%
    DESIRED_VOLATILITY_RATE = 2

    PE_RATIO = False  # We want it at 15 or less.
    DESIRED_PE_RATIO = 15

    AAA_BOND_RATE = 3.96

    print 'Finding quote for %s' % quote

    # First thing we want is some basic information on the quote.
    details = ystockquote.get_all(quote)

    last_trade = float(ystockquote.get_last_trade_price(str(quote)))

    print 'Prev Close: %s' % details.get('previous_close'), 'Today Open: $%s' % details.get('today_open'), 'Last Trade: $%s' % last_trade
    print 'Today\'s Change: %s' % ystockquote.get_todays_value_change(quote).split(' ')[2].rstrip('"')

    # Get the past ~50 BIZ days of trading.
    volatility = get_volatility(quote)
    print 'Volatility: %s%%' % (volatility)
    VOLATILITY = True if volatility > DESIRED_VOLATILITY_RATE else False

    # Get Ben grahams formula
    try:
        eps = float(ystockquote.get_eps(quote))
    except ValueError:
        # Likely returned N/A
        eps = 0
    try:
        next_eps = float(ystockquote.get_eps_estimate_next_year(quote))
    except ValueError:
        next_eps = 0

    # IV stands for Intrinsic Value.  What the stock is possibly really worth.
    iv = ben_graham(eps, next_eps, AAA_BOND_RATE)

    if iv != 0:
        # Get the relative intrinsic value, RIV
        riv = round(iv / last_trade, 4)
        print 'RIV: %s' % riv  # We want RIV to be better than 1.00, which would mean it's undervalued.
        RIV_RATIO = True if riv > DESIRED_RIV_RATE else False
    else:
        riv = 0

    # Add to our list if applicable
    if riv > 1.0:
        undervalued_stocks.append(quote)

    # Check out the PE ratio.
    try:
        pe = float(ystockquote.get_pe(quote))
        print 'P/E ratio: %s' % pe
        PE_RATIO = True if pe <= DESIRED_PE_RATIO else False
    except ValueError:
        pe = 'Check Research'
        pass

    # Check out the dividends on this babe
    try:
        div_yield = float(ystockquote.get_dividend_yield(quote))
        print 'Dividend yield: %s%%' % div_yield
        DIVIDEND_YIELD = True if div_yield >= DESIRED_DIVIDEND_RATE else False 
    except ValueError:
        print 'Dividend yield: %s' % ystockquote.get_dividend_yield(quote)

    # days = 71
    # print 'Last 50 days'
    # last_open = None
    # total_change = 0
    # for d, p in prices.iteritems():
    #     day_open = float(p.get('Open'))

    #     # Calculate the percentage change
    #     if last_open:
    #         change = str(round(day_open / last_open, 3)) + '%'

    #         if day_open > last_open:
    #             change = '+' + change
    #             total_change += round(day_open / last_open, 3)
    #         else:
    #             change = '-' + change
    #             total_change -= round(day_open / last_open, 3)
    #     else:
    #         change = ''

    #     last_open = day_open

    #     print '%s: %s %s' % (d, day_open, change)

    # print total_change / len(prices)

    if DIVIDEND_YIELD and RIV_RATIO and VOLATILITY and PE_RATIO:
        print '***** Check out: %s *****' % quote
    elif DIVIDEND_YIELD and RIV_RATIO and VOLATILITY:
        print '***** Check out: %s, mind the PE (%s) *****' % (quote, pe)
    elif RIV_RATIO and VOLATILITY:
        ignore_dividend_stocks.append(quote)

    print ''

print 'The undervalued stocks are:', str(undervalued_stocks)
print 'Ignoring dividends, these warrant a look:', str(ignore_dividend_stocks)
