#!/usr/bin/python

import sys
from pprint import pprint

import ystockquote


for quote in sys.argv[1:]:
    print 'Finding quote for %s' % quote

    # First thing we want is some basic information on the quote.
    details = ystockquote.get_all(quote)

    



