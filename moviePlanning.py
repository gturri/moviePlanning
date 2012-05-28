#!/usr/bin/python
from pulp import *
from datetime import datetime, timedelta

"""
Find a way to optimize the number of movies seen, given a list of Showings.

See the test file for examples.

In practice: 
- instantiate Showing objects, representing movies we want to see,
- give a list of such Showing to buid a Solver
- call Solver::whichShowingsShouldIAttend to get the list of showing to attend
"""

class Showing:
  def __init__(self, idxMovie, idxCinema, beginning, end):
    """
    :param idxMove: The movie projected during the showing
    :param idxCinema: The cinema where the showing takes place
    :param beginning: Time at which the showing begins
    :param end: Time at which the showing ends (should obviously by after beginning)
    """
    self.idxMovie   = idxMovie
    self.idxCinema  = idxCinema
    self.beginning  = beginning
    self.end        = end

  def __str__(self):
    return "Movie " + str(self.idxMovie) \
      + " in cinema " + str(self.idxCinema)   \
      + " from " + str(self.beginning)   \
      + " to "   + str(self.end)

  def strPLCompliant(self):
    """
    Convert to string, making sure we won't have ':' in the output
    """
    return "movie_" + str(self.idxMovie) \
        + "_cine_" + str(self.idxCinema) \
        + "_beginning_" + str(self.beginning.date()) \
        + "_" + str(self.beginning.hour) + "_" + str(self.beginning.minute)



class ShowingVariable:
  """
  This class associate a LpVariable to an actual showing.
  The LpVariable is binary, 1 meaning we should attend this showing
  """
  def __init__(self, showing):
    self.showing = showing
    strBeginning = str(showing.beginning.date()) + "-" + str(showing.beginning.hour) + "-" + str(showing.beginning.minute)
    self.lpVar = pulp.LpVariable(name="X_" + str(showing.idxMovie) + "_" + str(showing.idxCinema) + "_" + strBeginning
        , lowBound = 0
        , upBound = 1
        , cat = pulp.LpInteger)


class Solver:
  """
  This class represent our linear programming problem.
  In particular it contains every showings (and associated LpVariable),
  and it exposes the solver
  """
  def __init__(self, showings, timeBetweenTwoShowings = timedelta(0, 20*60), debug=False):
    self.__showingsVar = self.__buildShowingVars(showings)
    self.__timeBetweenTwoShowings = timeBetweenTwoShowings
    self.lp = pulp.LpProblem("MoviePlanning", pulp.LpMaximize)
    self.__addCteDontWatchAMovieMoreThanOnce()
    self.__addCteTime()
    self.__setObjective()
    self.debug = debug


  def __buildShowingVars(self, listShowings):
    listShowingVar = []
    for s in listShowings:
      lpVar = ShowingVariable(s)
      listShowingVar.append(lpVar)
    return listShowingVar

  def __addCteDontWatchAMovieMoreThanOnce(self):
    varsGroupedByMovie = {}
    for s in self.__showingsVar:
      if s.showing.idxMovie in varsGroupedByMovie:
        varsGroupedByMovie[s.showing.idxMovie][s.lpVar] = 1
      else:
        varsGroupedByMovie[s.showing.idxMovie] = {s.lpVar: 1}
  
    for movie in varsGroupedByMovie:
      name = "dontWatchAMovieMoreThanOnce_" + str(movie)
      e = pulp.LpAffineExpression(varsGroupedByMovie[movie])
      constraint = pulp.LpConstraint(sense=LpConstraintLE, e=e, name=name, rhs=1)
      self.lp.addConstraint(constraint)

  def __timeToChangeGoFromCine1ToCine2(self, idxCineFrom, idxCineTo):
    #TODO: will we be able to have this data?
    return timedelta(0, 0)

  def __addCteTime(self):
    # FIXME: if showings are sorted by beginning, this treatment could be done faster
    for s in self.__showingsVar:
      affineExp = {s.lpVar : 1}
  
      for s2 in self.__showingsVar:
        if s == s2:
          #the showing is already taken into account in this constraint
          continue
  
        if s2.showing.beginning < s.showing.beginning:
          #this relation is already taken into account in the constraint relative to s2
          continue
  
        if s2.showing.beginning >= s.showing.end + self.__timeBetweenTwoShowings + self.__timeToChangeGoFromCine1ToCine2(s.showing.idxCinema, s2.showing.idxCinema):
          #it's possible to attend both showings
          continue
  
        affineExp[s2.lpVar] = 1
  
      e = pulp.LpAffineExpression(affineExp)
      name = "respectEndOf_" + s.showing.strPLCompliant()
      constraint = pulp.LpConstraint(sense=LpConstraintLE, e=e, name=name, rhs=1)
      self.lp.addConstraint(constraint)

  def __setObjective(self):
    obj = pulp.LpConstraintVar()
    for s in self.__showingsVar:
      obj.addVariable(s.lpVar, 1)
    self.lp.setObjective(obj)

  def whichShowingsShouldIAttend(self):
    if self.debug:
      self.lp.writeLP("lp.lp")
    self.lp.solve()
  
    result = []
    for s in self.__showingsVar:
      if s.lpVar.value() == 1:
        result.append(s.showing)
    return result

