# -*- coding: utf-8 -*-
"""
Created on Wed Feb  3 08:20:18 2016

@author: ruinanzhang
"""

from __future__ import division
from pyomo.environ import *
from pyomo.opt import *

model = ConcreteModel()
model.name = 'Project Problem 2 version 2.0'

Profit = {}
Profit[1]=100
Profit[2] = 120
Profit[3] = 150
Profit[4] = 140
Profit[5] = 130


weekdays = [1,3,5,7,9,11]
model.teams = RangeSet(1,5)
model.weeks = RangeSet(1,6)
model.days = RangeSet(1,12)
model.weekdays = Set(initialize = weekdays)

model.profit = Param(model.teams, initialize = Profit)

model.v =0 

model.x = Var(model.teams, model.teams, model.days, within = Binary)

# a team cannot play it self
def SelfConflict(model,a):
    return sum(model.x[a,a,c] for c in model.days) ==0
model.conSelfConflict = Constraint(model.teams,rule = SelfConflict)

# each team can only play one team on each day
def OneGameLimit(model,a,c):
    return sum(model.x[a,b,c] for b in model.teams) <=1
model.conOneGame = Constraint(model.teams, model.days, rule = OneGameLimit)

# each team can only play each opponents twice
def TwoGameEachOpponent(model,a,b):
    if (a!=b):
        return sum(model.x[a,b,c] for c in model.days) >=2
    else:
        return sum(model.x[a,b,c] for c in model.days) ==0
model.conTwoGameEachOpponent = Constraint(model.teams,model.teams,rule = TwoGameEachOpponent)

def Total4HomeGame(model,a):
    return sum(model.x[a,b,c] for b in model.teams for c in model.days) >=4
model.conTotal8Game = Constraint(model.teams, rule = Total4HomeGame)

#G1
def G1 (model,a,c):
    return sum(model.x[a,b,c] for b in model.teams) >=1
#model.conG1a = Constraint(model.teams, [1,2], rule = G1)
model.conG1b = Constraint(model.teams, [11,12], rule = G1)

def G1Penalty(model,a):
    if (sum(model.x[a,b,c] for b in model.teams for c in [1,2]) <=1):
        model.v = model.v+1
#model.build = BuildAction([1,2,3],rule = G1Penalty)


#G2
def G2Home(model,a,i):
    return sum(model.x[a,b,i+k] for k in [0,1,2]  for b in model.teams) <= 3
model.conG2a = Constraint(model.teams,RangeSet(1,10),rule = G2Home)
def G2Away(model,b,i):
    return sum(model.x[a,b,i+k] for k in [0,1,2]  for a in model.teams) <= 3
model.conG2b = Constraint(model.teams, RangeSet(1,10),rule = G2Away)

#G3
def G3Home(model,a,i):
    return sum(model.x[a,b,i+k] for k in [0,2] for b in model.teams) <=1
model.conG3a = Constraint(model.teams,[2,4,6,8,10], rule = G3Home)
def G3Away(model,b,i):
    return sum(model.x[a,b,i+k] for k in [0,2] for a in model.teams) <=1
#model.conG3b = Constraint(model.teams,[2,4,6,8,10], rule = G3Away)

#G4
def G4a(model,a):
    return sum(model.x[a,b,c] for b in model.teams for c in  [2,4,6,8]) >=1
def G4b(model,a):
    return sum(model.x[a,b,c] for b in model.teams for c in  [2,4,6,8]) \
    + sum(model.x[b,a,c] for b in model.teams for c in  [2,4,6,8]) >=2
model.conG4a = Constraint(model.teams,rule = G4a)
model.conG4b = Constraint(model.teams, rule = G4b)

#G5
def G5a(model,a,b,c):
    return sum(model.x[a,b,c+i] + model.x[b,a,c+i] for i in [0,1]) <=2
model.conG5 = Constraint(model.teams,model.teams,RangeSet(1,11),rule = G5a)


# the followings are some teams' own requirements
# No1
def con1ab(model,a,b):
    return sum(model.x[a,b,c] + model.x[b,a,c] for c in [1,2,3,4]) <=0    
model.con1a = Constraint([1],[2],rule = con1ab)
model.con1b = Constraint([4],[5], rule = con1ab)
def con1cd(model,a,b) :
    return (model.x[a,b,12] + model.x[b,a,12]) >=1
model.con1c = Constraint([1],[2],rule = con1cd)
model.con1d = Constraint([4],[5], rule = con1cd)

# No2 
def con2(model,c):
    return model.x[3,4,c] + model.x[4,3,c] ==\
    model.x[1,5,c] + model.x[5,1,c]
model.con2 = Constraint(model.days,rule = con2)

# No3
def con3a(model):
    return sum(model.x[2,b,c] for b in model.teams for c in [10,11,12]) \
    + sum(model.x[a,2,c] for a in model.teams for c in [10,11,12]) <=2
model.con3a = Constraint(rule = con3a)
def con3b(model):
    return sum(model.x[5,b,c] for b in model.teams for c in [1,2,3,4])\
    + sum(model.x[a,5,c] for a in model.teams for c in [1,2,3,4]) <=3
model.con3b = Constraint(rule = con3b)

# No4
def con4(model):
    return sum(model.x[4,b,c] for b in model.teams for c in [3,7]) >=2
model.con4 = Constraint(rule = con4)

# No5 
def con5(model):
    return sum(model.x[a,5,4] + model.x[a,5,8] for a in model.teams) >=2
model.con5 = Constraint(rule = con5)



def calculate_profit (model):
    return sum(model.profit[a]*model.x[a,b,c] for a in model.teams for b in model.teams\
    for c in model.days)
model.obj = Objective(rule = calculate_profit, sense = maximize)





instance = model.create_instance()



# Indicate which solver to use
Opt = SolverFactory("glpk")

# Generate a solution
Soln = Opt.solve(instance)

# Load solution to instance then Display the solution
instance.solutions.load_from(Soln)
display(instance)


#print(model.v)