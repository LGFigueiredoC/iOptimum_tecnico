import environment
import pandas as pd
import numpy as np

def optimize (path):
    env = environment.Environment(path)
    allocated_orders = []
    flag = True
    finished = False

    while not finished:
        #print("not finished")
        first_allocated = None
        for day in env.days:
            #print("dia")
            #print(day.date)
            #print(day.resources)
            while True:
                #print("action_space", day.date-1)
                action_space = env.get_action_space(day.date-1)
                action_space.sort(key= lambda x: (x[1], x[2], len(env.state_space.states[x[0]].tasks)))
                #print(action_space)
                #print(action_space)
                
                if len(action_space) == 0:
                    if first_allocated == None:
                        finished = True
                    break   

                order = env.state_space.states[action_space[0][0]]
                
                if flag:
                    first_allocated = action_space[0]
                    flag = False

                ability, time = order.do_order(day.date-1)
                day.resources[ability] = day.resources[ability]-time
                #print(day.resources)

                if order.done:
                    allocated_orders.append([action_space[0], day.date])
        
        env.reset(allocated_orders, first_allocated)
    
                
    
    usage = [(day.total_resources[ability]-day.resources[ability])*100/day.total_resources[ability] for ability in day.resources]

    total_hours = {"Mecânico":0, "Elétrico":0, "Lubrificador":0, "Soldador":0}

    for day in env.days:
        for item, x in total_hours.items():
            total_hours[item] = total_hours[item] + day.resources[item]

    total_used_hours = {"Mecânico":0, "Elétrico":0, "Lubrificador":0, "Soldador":0}

    for info in allocated_orders:
        #print(order)
        order = env.state_space.states[info[0][0]]
        for task in order.tasks:
            for date in task.executed:
                total_used_hours[task.ability] = total_used_hours[task.ability]+task.time

    usage = {"Mecânico":0, "Elétrico":0, "Lubrificador":0, "Soldador":0}

    for item, x in total_hours.items():
        usage[item] = f"{int((total_hours[item]-total_used_hours[item])/total_hours[item]*100)}%"
        
    return allocated_orders, usage


def create_solution(path):
    allocated_orders, usage = optimize(path)
    allocated_orders.sort(key=lambda x: x[0][0])
    #print(allocated_orders, usage)

    n_Z = [order for order in allocated_orders if order[0][1] == 0]
    n_A = [order for order in allocated_orders if order[0][1] == 2]
    n_B = [order for order in allocated_orders if order[0][1] == 4]
    n_C = [order for order in allocated_orders if order[0][1] == 6]


    solution = {"solution": {order[0][0]: f"{order[1]}" for order in allocated_orders},
                 
                "metrics": {
                    "n_os": f"{len(allocated_orders)}",
                    "n_Z": f"{len(n_Z)}",
                    "n_A": f"{len(n_A)}",
                    "n_B": f"{len(n_B)}",
                    "n_C": f"{len(n_C)}",
                    "utilization": {
                        "mecanica": usage["Mecânico"],
                        "eletrica": usage["Elétrico"],
                        "solda": usage["Soldador"],
                        "lubrificacao": usage["Lubrificador"]
                        }
                    },

                "extras": {
                        "observations": None,
                        "plots": None,
                        "any_additional_information": None
                    }
                }
    
    return solution
    

