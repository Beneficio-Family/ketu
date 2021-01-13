"""This modules is in pre-version"""

#  MIT License
#
#  Copyright (c) 2020 loc
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.
#

from itertools import combinations_with_replacement as combs

# from datetime import date, time, timedelta, timezone, datetime
import numpy as np
import pandas as pd
import swisseph as swe

body_orbs = np.array([12, 12, 8, 8, 8, 10, 10, 6, 6, 4])

aspects = np.array([0, 30, 60, 90, 120, 150, 180])

aspects_coeff = np.array([1, 1 / 6, 1 / 3, 1 / 2, 2 / 3, 5 / 6, 1])

aspects_name = ['Conjunction', 'Semisextile', 'Sextile',
                'Square', 'Trine', 'Quincunx', 'Opposition']

signs = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 'Libra',
         'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']

swe.set_ephe_path(path='/home/loc/workspace/ketu/ephe')


# TODO: Refactor with datetime and timezone object
def local_to_utc(year, month, day, hour, minute, second, offset):
    """Return UTC time from local time"""
    return swe.utc_time_zone(year, month, day, hour, minute, second, offset)


# TODO: Refactor with datetime object
def utc_to_julian(year, month, day, hour, minute, second):
    """Return Julian date from UTC time"""
    return swe.utc_to_jd(year, month, day, hour, minute, second, 1)[1]


def dd_to_dms(dd):
    """Return degrees, minutes, seconds from decimal longitude"""
    minutes, seconds = divmod(dd * 3600, 60)
    degrees, minutes = divmod(minutes, 60)
    return tuple(map(int, (degrees, minutes, seconds)))


def distance(pos1, pos2):
    """Return the angular distance from two bodies positions"""
    angle = abs(pos2 - pos1)
    return angle if angle <= 180 else 360 - angle


def get_orb(body1, body2, aspect):
    """Calculate the orb for two bodies and aspect"""
    return ((body_orbs[body1] + body_orbs[body2]) / 2) * aspects_coeff[aspect]


# Data Structure for the list of orbs, by couple of bodies and aspect
# We first use a dictionnary, with a frozenset of couple of bodies as key,
# and a numpy array of the orbs, indexed by aspect as value
# We build the dictionnary by comprehension
aspect_dict = {
    comb: np.array([get_orb(*comb, n) for n in range(len(aspects))])
    for comb in combs([i for i in range(len(body_orbs))], 2)}

# Test with a Pandas DataFrame
# TODO: Change the data structure for the pandas DataFrame?
aspect_df = pd.DataFrame.from_dict(aspect_dict, 'index', columns=aspects_name)


# --------- interface functions with pyswisseph ---------
# TODO: move swisseph functions to a module
def body_name(body):
    """Return the body name"""
    if swe.get_planet_name(body) == 'mean Node':
        return 'Rahu'
    return swe.get_planet_name(body)


def body_properties(jdate, body):
    pass


def body_longitude(jdate, body):
    """Return the body longitude"""
    return swe.calc_ut(jdate, body)[0][0]


def body_speed(jdate, body):
    """Return the body longitude speed"""
    return swe.calc_ut(jdate, body)[0][3]


# --------------------------------------------------------


def is_retrograde(jdate, body):
    """Return True if a body is retrograde"""
    return body_speed(jdate, body) < 0


def body_sign(jdate, body):
    """Return the body position in sign"""
    position = body_longitude(jdate, body)
    dms = dd_to_dms(position)
    sign, degrees = divmod(dms[0], 30)
    return sign, degrees, dms[1], dms[2]


def get_aspect(jdate, body1, body2):
    """
    Return the aspect and orb between two bodies for a certain date
    Return None and distance betwween the two bodies if there's no aspect
    """
    dist = distance(body_longitude(jdate, body1),
                    body_longitude(jdate, body2))
    dist = round(dist, 2)
    for i, n in enumerate(aspect_dict[frozenset([body1, body2])]):
        orb = round(get_orb(body1, body2, i), 2)
        if i == 0 and dist <= n:
            return aspects[i], dist
        elif aspects[i] - orb <= dist <= aspects[i] + orb:
            return aspects[i], abs(aspects[i] - dist)
    return None, dist


def print_positions(jdate):
    """Function to format and print positions of the bodies for a date"""
    print('\n')
    print('-------- Bodies Positions --------')
    for i in range(len(body_orbs)):
        sign, d, m, s = body_sign(jdate, i)
        retro = 'R' if is_retrograde(jdate, i) else ''
        print(body_name(i) + ': ' + signs[sign] + ', ' + str(d) +
              'º' + str(m) + "'" + str(s) + '", ' + retro)


def print_aspects(jdate):
    """Function to format and print aspects between the bodies for a date"""
    print('\n')
    print('-------- Bodies Aspects ---------')
    for key in aspect_dict.keys():
        if len(key) == 2:
            aspect = get_aspect(jdate, *key)
            if aspect[0] is not None and aspect[0] != 30 and aspect[0] != 150:
                body1, body2 = key
                d, m, s = dd_to_dms(aspect[1])
                print(body_name(body1) + '-' + body_name(body2) + ': ' +
                      aspects_name[np.where(aspects == aspect[0])[
                          0].item()] + ', orb = ' + str(d) +
                      'º' + str(m) + "'" + str(s) + '", ')


if __name__ == '__main__':
    """year, month, day = map(int, input(
        'Give a date with iso format, ex: 2020-12-21\n').split('-'))
    hour, minute = map(int, input(
        'Give a time (hour, minute), with iso format, ex: 15:10\n').split(':'))
    tz = int(input('Give the offset with UTC, ex: 1 for France\n'))
    jday = utc_to_julian(*local_to_utc(year, month, day, hour, minute, 0, tz))
    print_positions(jday)
    print_aspects(jday)"""

    for i, row in aspect_df.iterrows():
        if i == (0, 0):
            print(row)
