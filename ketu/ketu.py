"""Ketu is a python library to generate time series and calendars based on
planetary aspects"""

from functools import lru_cache
from itertools import combinations as combs

import numpy as np
import swisseph as swe

# Structured array of astronimical bodies: Sun, Moon, Mercury, Venus, Mars,
# Jupiter, Saturn, Uranus, Neptune, Pluto and mean Node aka Rahu,
# their id's and their orb of influence.
# Inspired by Abu Ma’shar (787-886) and Al-Biruni (973-1050)
bodies = np.array([('Sun', 0, 12), ('Moon', 1, 12), ('Mercury', 2, 8),
                   ('Venus', 3, 8), ('Mars', 4, 10), ('Jupiter', 5, 10),
                   ('Saturn', 6, 10), ('Uranus', 7, 6), ('Neptune', 8, 6),
                   ('Pluto', 9, 4), ('Rahu', 10, 0)],
                  dtype=[('name', 'S12'), ('id', 'i4'), ('orb', 'f4')])

# Structured array of major aspects (harmonics 2 and 3) and their coefficient
# for calculation of the orb
aspects = np.array([('Conjunction', 0, 1), ('Sextile', 60, 1/3),
                    ('Square', 90, 1/2), ('Trine', 120, 2/3),
                    ('Opposition', 180, 1)],
                   dtype=[('name', 'S12'), ('value', 'f4'), ('coef', 'f4')])

# List of signs for body position
signs = ['Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo', 'Libra',
         'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces']


def dd_to_dms(deg):
    """Return degrees, minutes, seconds from degrees decimal"""
    mins, secs = divmod(deg * 3600, 60)
    degs, mins = divmod(mins, 60)
    return np.array((degs, mins, secs), dtype='i4')


def distance(pos1, pos2):
    """Return the angular distance from two bodies positions"""
    angle = abs(pos2 - pos1)
    return angle if angle <= 180 else 360 - angle


@lru_cache()
def get_orb(body1, body2, aspect):
    """Calculate the orb for two bodies and aspect"""
    return ((bodies['orb'][body1] + bodies['orb'][body2])/2 *
            aspects['coef'][np.where(aspects['value'] == aspect)])[0]


# --------- interface functions with pyswisseph ---------

# TODO: Refactor with datetime and timezone object
def local_to_utc(year, month, day, hour, minute, second, offset):
    """Convert local time to  UTC time"""
    return swe.utc_time_zone(year, month, day, hour, minute, second, offset)


# TODO: Refactor with datetime object
def utc_to_julian(year, month, day, hour, minute, second):
    """Convert UTC time to Julian date"""
    return swe.utc_to_jd(year, month, day, hour, minute, second, 1)[1]


def body_name(b_id):
    """Return the body name"""
    if swe.get_planet_name(b_id) == 'mean Node':
        return 'Rahu'
    return swe.get_planet_name(b_id)


@lru_cache()
def body_properties(jdate, b_id):
    """
    Return the body properties (longitude, latitude, distance to Earth in AU,
    longitude speed, latitude speed, distance speed) as a Numpy array
    """
    return np.array(swe.calc_ut(jdate, b_id)[0])

# --------------------------------------------------------


def body_id(b_name):
    """Return the body id"""
    return bodies['id'][np.where(bodies['name'] == b_name.encode())]


def body_long(jdate, body):
    """Return the body longitude"""
    return body_properties(jdate, body)[0]


def body_lat(jdate, body):
    """Return the body latitude"""
    return body_properties(jdate, body)[1]


def body_distance(jdate, body):
    """Return distance of the body to Earth in AU"""
    return body_properties(jdate, body)[2]


def body_vlong(jdate, body):
    """Return the body longitude speed"""
    return body_properties(jdate, body)[3]


def body_vlat(jdate, body):
    """Return the body latitude speed"""
    return body_properties(jdate, body)[4]


def body_vdistance(jdate, body):
    """Return the distance speed of the body"""
    return body_properties(jdate, body)[5]


def is_retrograde(jdate, body):
    """Return True if a body is retrograde"""
    return body_vlong(jdate, body) < 0


def is_ascending(jdate, body):
    """Return True if a body latitude is rising"""
    return body_vlat(jdate, body) > 0


def body_sign(long):
    """Return the body position in sign, degrees, minutes and seconds"""
    dms = dd_to_dms(long)
    sign, degs = divmod(dms[0], 30)
    mins, secs = dms[1], dms[2]
    return np.array((sign, degs, mins, secs))


def positions(jdate, bodies_id):
    """Return an array of bodies longitude"""
    return np.array([body_long(jdate, int(body))
                     for body in np.nditer(bodies_id)])


def get_aspects(jdate, bodies_id):
    """
    Return a dictionnary of aspects and orb between bodies for a certain date
    Return None if there's no aspect
    """
    d_aspects = {}
    for comb in combs(bodies_id, 2):
        dist = distance(body_long(jdate, comb[0]),
                        body_long(jdate, comb[1]))
        for aspect in aspects['value']:
            orb = get_orb(*comb, aspect)
            if aspect == 0 and dist <= orb:
                d_aspects[frozenset(comb)] = np.array([aspect, dist])
            elif aspect - orb <= dist <= aspect + orb:
                d_aspects[frozenset(comb)] = np.array([aspect, aspect - dist])
    return d_aspects if d_aspects else None


def print_positions(jdate):
    """Function to format and print positions of the bodies for a date"""
    print('\n')
    print('------------- Bodies Positions -------------')
    pos_it = np.nditer(positions(jdate, bodies['id']), flags=['f_index'])
    for pos in pos_it:
        sign, degs, mins, secs = body_sign(float(pos))
        retro = ', R' if is_retrograde(jdate, pos_it.index) else ''
        print(f"{body_name(pos_it.index):10}: "
              f"{signs[sign]:15}{degs:>2}º{mins:>2}'{secs:>2}\"{retro}")


def print_aspects(jdate):
    """Function to format and print aspects between the bodies for a date"""
    print('\n')
    print('------------- Bodies Aspects -------------')
    for key, item in get_aspects(jdate, bodies['id']).items():
        body1, body2 = key
        index = np.searchsorted(aspects['value'], item[0])
        degs, mins, secs = dd_to_dms(item[1])
        print(f"{body_name(body1):7} - {body_name(body2):8}: "
              f"{aspects['name'][index].decode():12} "
              f"{degs:>2}º{mins:>2}'{secs:>2}\"")


def main():
    """Entry point of the programm"""
    year, month, day = map(int, input(
        'Give a date with iso format, ex: 2020-12-21\n').split('-'))
    hour, mins = map(int, input(
        'Give a time (hour, minute), with iso format, ex: 18:30\n').split(':'))
    offset = float(input('Give the offset with UTC, ex: 1 for France\n'))
    jday = utc_to_julian(*local_to_utc(year, month, day, hour, mins, 0, offset))
    print_positions(jday)
    print_aspects(jday)


if __name__ == '__main__':
    main()
