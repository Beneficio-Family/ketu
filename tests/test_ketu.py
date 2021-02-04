from unittest import TestCase

from ketu.ketu import *

jday = utc_to_julian(*local_to_utc(1975, 6, 6, 15, 10, 0, 1))
zero_day = utc_to_julian(-4713, 11, 24, 12, 0, 0)


class KetuTest(TestCase):

    def test_local_to_utc(self):
        self.assertAlmostEqual(local_to_utc(1975, 6, 6, 15, 10, 0, 1)[-1] % -60,
                               (1975, 6, 6, 14, 10, 0)[-1])

    def test_utc_to_julian(self):
        self.assertEqual(zero_day, 0)

    def test_dd_to_dms(self):
        self.assertEqual(dd_to_dms(271.45), (271, 27, 0))

    def test_distance(self):
        # Test reflexivity of distance
        self.assertEqual(
            distance(body_long(jday, 0), body_long(jday, 1)),
            distance(body_long(jday, 1), body_long(jday, 0)))
        self.assertAlmostEqual(distance(body_long(jday, 3),
                                        body_long(jday, 10)),
                               120, delta=1)

    def test_get_orb(self):
        self.assertEqual(get_orb(0, 1, 3), 8)

    def test_body_name(self):
        self.assertEqual('Sun', body_name(0))

    def test_body_properties(self):
        self.assertAlmostEqual(body_properties(jday, 0)[0], 75, delta=1)

    def test_body_long(self):
        self.assertAlmostEqual(body_long(jday, 0), 75, delta=1)

    def test_body_lat(self):
        self.assertAlmostEqual(body_lat(jday, 1), 2, delta=0.2)

    def test_body_distance(self):
        self.assertAlmostEqual(body_distance(jday, 4), 1.5, delta=0.1)

    def test_body_vlong(self):
        self.assertAlmostEqual(body_vlong(jday, 0), 1, delta=0.05)

    def test_body_vlat(self):
        self.assertAlmostEqual(body_vlat(jday, 1), -1, delta=0.1)

    def test_body_vdistance(self):
        self.assertAlmostEqual(body_vdistance(jday, 0), 0, delta=0.1)

    def test_is_retrograde(self):
        self.assertTrue(is_retrograde(jday, 7))
        self.assertTrue(is_retrograde(jday, 10))

    def test_is_ascending(self):
        self.assertFalse(is_ascending(jday, 1))

    def test_body_sign(self):
        self.assertEqual(signs[body_sign(jday, 0)[0]], 'Gemini')

    def test_get_aspects(self):
        bodies = np.arange(11)
        d_aspects = get_aspects(jday, bodies)
        aspect, orb = d_aspects[frozenset([3, 10])]
        self.assertEqual(aspect, 120)
        self.assertAlmostEqual(orb, 0, delta=1)

    def test_bodies_positions(self):
        pass

    def test_get_all_aspects(self):
        pass
