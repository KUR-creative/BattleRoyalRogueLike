#-*- coding: utf-8 -*-

def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    reverse = dict((value, key) for key, value in enums.iteritems())
    enums['reverse_mapping'] = reverse
    return type('Enum', (), enums)

'''
출처:
http://stackoverflow.com/questions/36932/how-can-i-represent-an-enum-in-python
Thank you Alec Thomas!

사용예
>>> Numbers = enum('ZERO', 'ONE', 'TWO')
>>> Numbers.ONE
1
>>> Numbers.TWO
2

>>> Numbers.reverse_mapping[1]
'ONE'

Numbers = enum('ZERO', 'ONE', 'TWO', FIVE=5, SIX=6)
'''