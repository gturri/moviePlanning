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
  This class associates a LpVariable to an actual showing.
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
  This class represents our linear programming problem.
  In particular it contains every showings (and associated LpVariable),
  and it exposes the solver
  """
  def __init__(self, showings, timeBetweenTwoShowings = timedelta(0, 20*60), debug=False, name = ""):
    self.debug = debug
    self.name = name
    self.showingsVar = self.__buildShowingVars(showings)
    self.__timeBetweenTwoShowings = timeBetweenTwoShowings
    self.lp = pulp.LpProblem("MoviePlanning", pulp.LpMaximize)
    self.__addCteDontWatchAMovieMoreThanOnce()
    self.__addCteTime()
    self.__setObjective()
    self._timeObjHelper = TimeObjectivesHelper()

  def addObjEndingTime(self, wantToFinishLate = False):
    self._timeObjHelper.addObjEndingTime(self, wantToFinishLate)

  def addObjStartingTime(self, wantToStartLate = False):
    self._timeObjHelper.addObjStartingTime(self, wantToStartingLate)

  def __buildShowingVars(self, listShowings):
    listShowingVar = []
    for s in listShowings:
      lpVar = ShowingVariable(s)
      listShowingVar.append(lpVar)
    return listShowingVar

  def __addCteDontWatchAMovieMoreThanOnce(self):
    varsGroupedByMovie = {}
    for s in self.showingsVar:
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
    for s in self.showingsVar:
      affineExp = {s.lpVar : 1}
  
      for s2 in self.showingsVar:
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
    for s in self.showingsVar:
      obj.addVariable(s.lpVar, 1)
    self.objective = obj

  def whichShowingsShouldIAttend(self):
    self.lp.setObjective(self.objective)
    if self.debug:
      self.lp.writeLP(self.name + "_lp.lp")
    self.lp.solve()

    if self.debug:
      f = open(self.name + "_solLP.txt", "w")
      for s in self.lp.variables():
        f.write(s.name + " = " + str(s.value()) + "\n")
      f.close()


  
    result = []
    for s in self.showingsVar:
      if s.lpVar.value() == 1:
        result.append(s.showing)
    return result


class TimeObjectivesHelper:
  """
  This class adds needed variables and constraints to let add objectives of the form
  'I'd rather start/finish my day early/late'
  Using a separate class instead of putting everything in Solver, to let the possibility
  to easily try (and bench) different mathematical strategies
  """

  def addObjEndingTime(self, solver, wantToFinishLate):
    if wantToFinishLate:
      objSenseMult = 1
    else:
      objSenseMult = -1

    endingHours = {}
    for showingVar in solver.showingsVar:
      end = showingVar.showing.end
      if end not in endingHours:
        name = "notStrictlyFinishedAt_" + str(end.date()) + "_" + str(end.hour) + "_" + str(end.minute)
        endingHours[end] = pulp.LpVariable(name = name, lowBound=0, upBound=1, cat = pulp.LpInteger)

    for end in endingHours:
      affineExpSum = {endingHours[end]: 1}
      for s in solver.showingsVar:
        if s.showing.end >= end:
          affineExpSum[s.lpVar] = -1

          #Add constraint to make sure the new variables are 1 if we're not strictly done yet
          affineExp = {endingHours[end] : 1, s.lpVar : -1}
          name = "endVar_" + endingHours[end].name + "_isOneIfWeAttend_" + s.lpVar.name
          e = pulp.LpAffineExpression(affineExp)
          constraint = pulp.LpConstraint(sense=LpConstraintGE, e=e, name=name, rhs=0)
          solver.lp.addConstraint(constraint)

      #Add constraint to make sure the new variables are 0 if we're strictly done
      #(uneeded is we want to finish early, because it will be set to 0 by the objective.
      # However, need if we want to finish late)
      name = "endVar_" + endingHours[end].name + "_isZeroIfWereDone"
      e = pulp.LpAffineExpression(affineExpSum)
      constraint = pulp.LpConstraint(sense=LpConstraintLE, e=e, name=name, rhs=0)
      solver.lp.addConstraint(constraint)

    sortedEndingHours = sorted(endingHours)
    earliestEnd = sortedEndingHours[0]
    largestDelta = sortedEndingHours[-1] - sortedEndingHours[0]
    largestInMinutes  = 24*60.0 * largestDelta.days + largestDelta.seconds/60.0 #Convert to minutes
    obj = pulp.LpConstraintVar()
    for idx in range(1, len(sortedEndingHours)):
      end = sortedEndingHours[idx]
      delta = end - sortedEndingHours[idx-1]
      cost = objSenseMult * (24*60.0*delta.days + delta.seconds/60.0) / largestInMinutes
      solver.objective.addVariable(endingHours[end], cost)



  def addObjStartingTime(self, solver, wantToFinishEarly):
    pass
