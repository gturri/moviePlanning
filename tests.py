#!/usr/bin/python
import unittest
from moviePlanning import *
from datetime import datetime

class TestPlanning(unittest.TestCase):
  def test_std(self):
    showings = []
    showings.append(Showing(1, 1, datetime(2012, 1, 20,  8, 00), datetime(2012, 1, 20,  9, 00)))
    showings.append(Showing(2, 1, datetime(2012, 1, 20,  8, 00), datetime(2012, 1, 20,  9, 00)))
    showings.append(Showing(2, 1, datetime(2012, 1, 20, 10, 00), datetime(2012, 1, 20, 11, 00)))
    showings.append(Showing(3, 1, datetime(2012, 1, 20, 10, 00), datetime(2012, 1, 20, 11, 00)))
    showings.append(Showing(3, 1, datetime(2012, 1, 20, 12, 00), datetime(2012, 1, 20, 13, 00)))
    showingsToAttend = whichShowingsShouldIAttend(showings)

    #Only one possibility to see the 3 movies: attend showings 0, 2 and 4
    self.assertTrue(showings[0] in showingsToAttend)
    self.assertTrue(showings[2] in showingsToAttend)
    self.assertTrue(showings[4] in showingsToAttend)
    self.assertTrue(showings[1] not in showingsToAttend)
    self.assertTrue(showings[3] not in showingsToAttend)

  def test_CantSeeEveryMovie(self):
    showings = []
    showings.append(Showing(1, 1, datetime(2012, 1, 20,  8, 00), datetime(2012, 1, 20,  9, 00)))
    showings.append(Showing(2, 1, datetime(2012, 1, 20,  8, 00), datetime(2012, 1, 20,  9, 00)))
    showings.append(Showing(3, 1, datetime(2012, 1, 20, 12, 00), datetime(2012, 1, 20, 13, 00)))
    showingsToAttend = whichShowingsShouldIAttend(showings)

    #It's possible to see movie 0 or 1, and movie 2, but not all the three
    self.assertEqual(len(showingsToAttend), 2)
    self.assertTrue(showings[2] in showingsToAttend)
    seeMovie0ButNot1 = showings[0] in showingsToAttend and showings[1] not in showingsToAttend
    seeMovie1ButNot0 = showings[0] not in showingsToAttend and showings[1] in showingsToAttend
    self.assertTrue(seeMovie0ButNot1 or seeMovie1ButNot0)
    self.assertFalse(seeMovie0ButNot1 and seeMovie1ButNot0)



if __name__ == '__main__':
  unittest.main()