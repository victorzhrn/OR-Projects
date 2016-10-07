# -*- coding: utf-8 -*-
"""
Created on Fri Jan 29 15:38:00 2016

@author: ruinanzhang
"""

from __future__ import division
from pyomo.environ import *
from pyomo.opt import *


#model = AbstractModel()
model = ConcreteModel()
model.name = 'Project Problem 2'

Days = ['weekday','weekend']
GameType = ['home','away']

model.teams = RangeSet(1,5)
model.days = Set(initialize = Days)
model.gametype = Set(initialize = GameType )
model.weeks = RangeSet(1,6)


model.x = Var(model.teams, model.teams, model.days, model.gametype, model.weeks, within =Binary)

def home_away(model,a,b,c,d):
    return model.x[a,b,c,'home',d] == model.x[b,a,c,'away',d]
  
model.conHomeAway = Constraint(model.teams,model.teams,model.days,model.weeks,rule = home_away)

# a team cannot play it self
def selfconflict(model,a):
    return sum(model.x[a,a,c,d,e] for c in model.days for d in model.gametype \
    for e in model.weeks)==0
    
model.conSelfConflict= Constraint(model.teams, rule = selfconflict)

# a team has to play 1 game per day either home or away
def OneGame(model,a,c,e):
    return sum(model.x[a,b,c,d,e] for b in model.teams for d in model.gametype) <=1
#constraint suspended   
#model.conOneGame1 = Constraint(model.teams,model.days,model.weeks, rule = OneGame)
#model.conOneGame2 = Constraint(model.teams,['weekend'],model.weeks, rule = OneGame)
model.conOneGame3 = Constraint(model.teams,['weekday'],model.weeks, rule = OneGame)

# a team has to play other 4 team twice
def EightGame(model,a):
    return sum(model.x[a,b,c,d,e] for b in model.teams for c in model.days \
    for e in model.weeks for d in model.gametype) >=8 
        
model.conEightGame = Constraint(model.teams, rule = EightGame)




#Each team can only play the other team twice, one home game , one away game
def OneTeamTwice(model,a,b):
    return sum(model.x[a,b,c,d,e] for c in model.days \
    for d in model.gametype for e in model.weeks) <=2
        
model.conOneTeamTwice = Constraint(model.teams,model.teams,rule=OneTeamTwice)

# No 1
# one home game in 1st and 5th week
def FirstFinalWeekHomeGame(model,a,e):
    return sum(model.x[a,b,c,'home',e] for b in model.teams for c in model.days ) >=1
        
model.conFirstFinalHome = Constraint(model.teams,[1,6], rule = FirstFinalWeekHomeGame) 

# No 4
# the following 2 constraints makes sure 
#for first 4 weekends a team has to have at least one weekend game and one homegame
def OneWeekendHome(model,a):
    return sum(model.x[a,b,'weekend','home',e] for b in model.teams for e in [1,2,3,4]) >=1
# make sure that there is 2 weekend game for the first 4 weekend
def TwoGameWeekend(model,a):
    return sum(model.x[a,b,'weekend',d,e] for b in model.teams for d in model.gametype\
    for e in [1,2,3,4]) >=2
model.conOneWeekendHome = Constraint(model.teams,rule = OneWeekendHome) 
model.conTwoGameWeekend = Constraint(model.teams, rule = TwoGameWeekend)    
        

def dummy_obj(model):
    return sum(model.x[a,b,c,d,e]*100 for a in model.teams for b in model.teams\
    for c in model.days for d in model.gametype for e in model.weeks)
    
model.obj = Objective(rule = dummy_obj,sense = maximize)


## the followings are individual teams requriements

# No1 
# 1,2 and 4,5 must play in the final time slot
def con1a (model):
    return sum(model.x[1,2,'weekend',d,6] for d in model.gametype)==1
model.con1a = Constraint(rule = con1a)
def con1b (model):
    return sum(model.x[4,5,'weekend',d,6] for d in model.gametype)==1
model.con1b = Constraint(rule = con1b)
def con1c(model,a,b):
    return sum(model.x[a,b,c,d,e] for c in model.days\
    for d in model.gametype for e in [1,2]) ==0
model.con1c = Constraint([1],[2],rule = con1c)
model.con1d = Constraint([4],[5],rule = con1c)         

# No2 
# 3,4 play the same time as 1,5
def con2(model,c,e):
    return sum(model.x[3,4,c,d,e] for d in model.gametype) \
    == sum(model.x[1,5,c,d,e] for d in model.gametype)
model.con2 = Constraint(model.days,model.weeks, rule = con2)

# No 3
# team 2 has a bye during the final 3 game days
def con3a(model):
    return sum(model.x[3,b,'weekend',d,5]+model.x[3,b,'weekday',d,6]\
    +model.x[3,b,'weekend',d,6] for b in model.teams for d in model.gametype) <=2
model.con3a = Constraint(rule = con3a)
# team 5 wants a bye during the first 4 games
def con3b(model):
    return sum(model.x[5,b,c,d,e] for b in model.teams for c in model.days\
    for d in model.gametype for e in [1,2]) <=2
model.con3b = Constraint(rule = con3b)   

# No 4
# team 4 must have home games on day 3 and 7
def con4(model):
    return sum(model.x[3,b,'weekday','home',2] + model.x[3,b,'weekday','home',4]\
    for b in model.teams) ==2
model.con4 = Constraint(rule = con4)

# No 5
# team 5 must have away games on days 4 and 8
def con5(model):
    return sum(model.x[5,b,'weekend','away',e] for b in model.teams\
    for e in [2,4]) ==2
model.con5 = Constraint(rule = con5)
    




instance = model

instance.pprint()

# Indicate which solver to use
Opt = SolverFactory("glpk")

# Generate a solution
Soln = Opt.solve(instance)

# Load solution to instance then Display the solution
instance.solutions.load_from(Soln)
display(instance)



