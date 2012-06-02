#!/usr/bin/python
import unittest
from moviePlanning import *
from datetime import datetime, timedelta

class TestPlanning(unittest.TestCase):
  def test_std(self):
    showings = []
    showings.append(Showing(1, 1, datetime(2012, 1, 20,  8, 00), datetime(2012, 1, 20,  9, 00)))
    showings.append(Showing(2, 1, datetime(2012, 1, 20,  8, 00), datetime(2012, 1, 20,  9, 00)))
    showings.append(Showing(2, 1, datetime(2012, 1, 20, 10, 00), datetime(2012, 1, 20, 11, 00)))
    showings.append(Showing(3, 1, datetime(2012, 1, 20, 10, 00), datetime(2012, 1, 20, 11, 00)))
    showings.append(Showing(3, 1, datetime(2012, 1, 20, 12, 00), datetime(2012, 1, 20, 13, 00)))
    solver = Solver(showings)
    showingsToAttend = solver.whichShowingsShouldIAttend()

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
    solver = Solver(showings)
    showingsToAttend = solver.whichShowingsShouldIAttend()

    #It's possible to see movie 0 or 1, and movie 2, but not all the three
    self.assertEqual(len(showingsToAttend), 2)
    self.assertTrue(showings[2] in showingsToAttend)
    seeMovie0ButNot1 = showings[0] in showingsToAttend and showings[1] not in showingsToAttend
    seeMovie1ButNot0 = showings[0] not in showingsToAttend and showings[1] in showingsToAttend
    self.assertTrue(seeMovie0ButNot1 or seeMovie1ButNot0)
    self.assertFalse(seeMovie0ButNot1 and seeMovie1ButNot0)

  def _gimmeMyFourShowingInARow(self):
    showings = []
    showings.append(Showing(1, 1, datetime(2012, 1, 20,  8, 00), datetime(2012, 1, 20,  8, 30)))
    showings.append(Showing(1, 1, datetime(2012, 1, 20,  9, 00), datetime(2012, 1, 20,  9, 30)))
    showings.append(Showing(1, 1, datetime(2012, 1, 20, 10, 00), datetime(2012, 1, 20, 10, 30)))
    showings.append(Showing(1, 1, datetime(2012, 1, 20, 11, 00), datetime(2012, 1, 20, 11, 30)))
    return showings

  def test_finishLate(self):
    showings = self._gimmeMyFourShowingInARow()
    solver = Solver(showings)
    solver.addObjEndingTime(wantToFinishLate = True)
    showingsToAttend = solver.whichShowingsShouldIAttend()

    self.assertEqual(len(showingsToAttend), 1)
    self.assertTrue(showings[3] in showingsToAttend)

  def test_finishEarly(self):
    showings = self._gimmeMyFourShowingInARow()
    solver = Solver(showings)
    solver.addObjEndingTime(wantToFinishLate = False)
    showingsToAttend = solver.whichShowingsShouldIAttend()

    self.assertEqual(len(showingsToAttend), 1)
    self.assertTrue(showings[0] in showingsToAttend)

  def test_startLate(self):
    showings = self._gimmeMyFourShowingInARow()
    solver = Solver(showings)
    solver.addObjStartingTime(wantToStartLate = True)
    showingsToAttend = solver.whichShowingsShouldIAttend()

    self.assertEqual(len(showingsToAttend), 1)
    self.assertTrue(showings[3] in showingsToAttend)

  def test_startEarly(self):
    showings = self._gimmeMyFourShowingInARow()
    solver = Solver(showings)
    solver.addObjStartingTime(wantToStartLate = False)
    showingsToAttend = solver.whichShowingsShouldIAttend()

    self.assertEqual(len(showingsToAttend), 1)
    self.assertTrue(showings[0] in showingsToAttend)

  def test_timeBetweenShowings(self):
    showings = []
    showings.append(Showing(1, 1, datetime(2012, 1, 20,  8, 00), datetime(2012, 1, 20,  9, 00)))
    showings.append(Showing(2, 1, datetime(2012, 1, 20, 10, 00), datetime(2012, 1, 20, 11, 00)))
    showings.append(Showing(3, 1, datetime(2012, 1, 20, 12, 00), datetime(2012, 1, 20, 13, 00)))

    solverForAFastSpectator = Solver(showings, timedelta(0, 30*60))
    solverForASlowSpectator = Solver(showings, timedelta(0, 90*60))

    showingsOfTheFastOne = solverForAFastSpectator.whichShowingsShouldIAttend()
    showingsOfTheSlowOne = solverForASlowSpectator.whichShowingsShouldIAttend()

    #Needing only 30 minutes between the end of a showings and the beginning of the next one, it is possible to see every movies
    self.assertTrue(showings[0] in showingsOfTheFastOne)
    self.assertTrue(showings[1] in showingsOfTheFastOne)
    self.assertTrue(showings[2] in showingsOfTheFastOne)

    #Needing 90 minutes between the end of a showings and the beginning of the next one, it is possible to see only movies 0 and 2
    self.assertTrue(showings[0] in showingsOfTheSlowOne)
    self.assertFalse(showings[1] in showingsOfTheSlowOne)
    self.assertTrue(showings[2] in showingsOfTheSlowOne)


if __name__ == '__main__':
  unittest.main()
