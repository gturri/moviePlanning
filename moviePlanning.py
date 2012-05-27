#!/usr/bin/python
from pulp import *
from datetime import datetime, timedelta

#TODO Use a kind of configuration manager instead
#minimum time delta between two successive showings
safetyMarginBetweenTwoShowings = timedelta(0, 20*60)

class Showing:
  def __init__(self, idxMovie, idxCinema, beginning, end):
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
    return "movie_" + str(self.idxMovie) \
        + "_cine_" + str(self.idxCinema) \
        + "_beginning_" + str(self.beginning.date()) \
        + "_" + str(self.beginning.hour) + "_" + str(self.beginning.minute)



class ShowingVariable:
  def __init__(self, showing):
    self.showing = showing
    strBeginning = str(showing.beginning.date()) + "-" + str(showing.beginning.hour) + "-" + str(showing.beginning.minute)
    self.lpVar = pulp.LpVariable(name="X_" + str(showing.idxMovie) + "_" + str(showing.idxCinema) + "_" + strBeginning
        , lowBound = 0
        , upBound = 1
        , cat = pulp.LpInteger)

def addCteDontWatchAMovieMoreThanOnce(lp, listShowingVar):
  varsGroupedByMovie = {}
  for s in listShowingVar:
    if s.showing.idxMovie in varsGroupedByMovie:
      varsGroupedByMovie[s.showing.idxMovie][s.lpVar] = 1
    else:
      varsGroupedByMovie[s.showing.idxMovie] = {s.lpVar: 1}

  for movie in varsGroupedByMovie:
    name = "dontWatchAMovieMoreThanOnce_" + str(movie)
    e = pulp.LpAffineExpression(varsGroupedByMovie[movie])
    constraint = pulp.LpConstraint(sense=LpConstraintLE, e=e, name=name, rhs=1)
    lp.addConstraint(constraint)

def timeToChangeGoFromCine1ToCine2(idxCineFrom, idxCineTo):
  #TODO: will we be able to have this data?
  return timedelta(0, 0)

def addCteTime(lp, listShowingVar):
  # FIXME: if showings are sorted by beginning, this treatment could be done faster
  for s in listShowingVar:
    affineExp = {s.lpVar : 1}

    for s2 in listShowingVar:
      if s == s2:
        #the showing is already taken into account in this constraint
        continue

      if s2.showing.beginning < s.showing.beginning:
        #this relation is already taken into account in the constraint relative to s2
        continue

      if s2.showing.beginning >= s.showing.end + safetyMarginBetweenTwoShowings + timeToChangeGoFromCine1ToCine2(s.showing.idxCinema, s2.showing.idxCinema):
        #it's possible to attend both showings
        continue

      affineExp[s2.lpVar] = 1

    e = pulp.LpAffineExpression(affineExp)
    name = "respectEndOf_" + s.showing.strPLCompliant()
    constraint = pulp.LpConstraint(sense=LpConstraintLE, e=e, name=name, rhs=1)
    lp.addConstraint(constraint)

def setObjective(lp, listShowingVar):
  obj = pulp.LpConstraintVar()
  for s in listShowingVar:
    obj.addVariable(s.lpVar, 1)
  lp.setObjective(obj)

def buildShowingVars(listShowings):
  listShowingVar = []

  for s in listShowings:
    lpVar = ShowingVariable(s)
    listShowingVar.append(lpVar)
  return listShowingVar

def buildLP(listShowingVar):
  lp = pulp.LpProblem("MoviePlanning", pulp.LpMaximize)
  addCteDontWatchAMovieMoreThanOnce(lp, listShowingVar)
  addCteTime(lp, listShowingVar)
  setObjective(lp, listShowingVar)
  return lp

def whichShowingsShouldIAttend(listShowings):
  showingVars = buildShowingVars(listShowings)
  lp = buildLP(showingVars)
  lp.writeLP("lp.lp")
  lp.solve()

  result = []
  for s in showingVars:
    if s.lpVar.value() == 1:
      result.append(s.showing)
  return result

