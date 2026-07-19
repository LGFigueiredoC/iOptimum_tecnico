import environment
import pandas as pd
import numpy as np
import json


def optimize (path):
    env = environment.Environment(path)
    allocated_orders = []

    for day in env.days:
        while True:
            action_space = env.get_action_space(day.date)
            action_space.sort(key= lambda x: (x[1], x[2]))

            order = env.state_space[action_space[0]]

            ability, time = order.do_order()
            day.resources[ability] -= time

            if order.done:
                allocated_orders.append([action_space[0], day.date])
    
            if len(action_space) > 0:
                break
    
    usage = [(day.total_resources[ability]-day.resources[ability])/day.total_resources[ability] for ability in day.resources]

    return allocated_orders, usage


def create_solution(path):
    allocated_orders, usage = optimize(path)
    
