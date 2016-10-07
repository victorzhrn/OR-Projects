# -*- coding: utf-8 -*-
"""
Created on Tue Dec 22 16:21:09 2015

@author: Ruinan
""" 

from __future__ import division
from pyomo.environ import *
from pyomo.opt import *

model = AbstractModel()
model.name = 'ebola'


model.airplane_cost = Param(within = NonNegativeReals)
model.ground_cost = Param(within = NonNegativeReals)
model.number_locations = Param(within = NonNegativeIntegers)
model.budget_limit = Param(within = NonNegativeReals)
model.location_range = RangeSet(model.number_locations)
model.medicine_cost = Param(within = NonNegativeReals)

model.location_distance = Param(model.location_range, within = NonNegativeReals)
model.location_population = Param(model.location_range, within = NonNegativeReals)

model.amount_to_location = Var(model.location_range, within = NonNegativeReals)

def air_cost(model):
    return sum(model.amount_to_location[i] for i in model.location_range)*model.airplane_cost

def ground_cost(model):
    return sum(model.amount_to_location[i]*model.ground_cost*model.location_distance[i] for i in model.location_range)

def med_cost(model):
    return sum(model.amount_to_location[i] for i in model.location_range)*model.medicine_cost
    
def money_con(model):
    return ground_cost(model)+air_cost(model)+med_cost(model) <= model.budget_limit
    
def population_con(model,i):
    return model.amount_to_location[i] <= model.location_population[i] 
    
def total_amount(model):
    return sum(model.amount_to_location[i] for i in model.location_range)
    
model.con1 = Constraint(rule = money_con )
model.con2 = Constraint(model.location_range, rule = population_con)

model.obj = Objective(rule = total_amount, sense = maximize)


instance = model.create_instance('ebola.dat')
instance.pprint() 

Opt = SolverFactory("glpk")
Soln = Opt.solve(instance)
instance.solutions.load_from(Soln)
display(instance) 
