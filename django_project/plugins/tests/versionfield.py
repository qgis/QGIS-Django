#!/usr/bin/env python
#-*- coding:utf-8 -*-

"""
    Tests for version comparison field

    DESCRIPTION

    @copyright: 2014 by Alessandro Pasotti - ItOpen (http://www.itopen.it) <apasotti@gmail.com>
    @license: GNU GPL, see COPYING for details.



"""

import re


VERSION_RE=r'(^|(?<=\.))0+(?!\.)|\.#+'

TEST_CASES=(
    '1.0.0',
    '1.0.1',
    '0.0.0',
    '1.0',
    '1.10',
    '1.2',
    '1.9',
    '1.0.a',
    'a.0.a',
    'b.a.c',
    'a.b',
    '0.a.0.1',
    '1.0.rc1',
    '1.1a',
    '1.1b',
    '1.9.0',
)

def vjust(str, level=4, delim='.', bitsize=4, fillchar=' ', force_zero=False):
    """
    Normalize a dotted version string.

    1.12 becomes : 1.    12
    1.1  becomes : 1.     1


    if force_zero=True and level=2:

    1.12 becomes : 1.    12.     0
    1.1  becomes : 1.     1.     0


    """
    if not str:
        return str
    nb = str.count(delim)
    if nb < level:
        if force_zero:
            str += (level-nb) * (delim+'0')
        else:
            str += (level-nb) * delim
    parts = []
    for v in str.split(delim)[:level+1]:
        if not v:
            parts.append(v.rjust(bitsize,'#'))
        else:
            parts.append(v.rjust(bitsize,fillchar))
    return delim.join(parts)




def test():
    transformed = []
    for v in TEST_CASES:
        vj = vjust(v, level=5, fillchar='0')
        transformed.append(vj)
        ck = re.sub(VERSION_RE, '', vj)
        print "Testing\t %s (%s)\t\t %s" % (v, ck, vj)
        if v != ck:
            print "!!! failed !!!"

    # Test sorting
    transformed.sort()
    print "Sorted:"
    for v in transformed:
        print v





if __name__ == "__main__":
    test()

