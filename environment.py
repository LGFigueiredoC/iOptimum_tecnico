import pandas as pd
import numpy as np


priority = {'Z': 0,
            'Z1': 1, 
            'A': 2,
            'A1': 3,
            'B': 4,
            'B1': 5,
            'C': 6,
            'C1': 7}
inv_priority = {v:k for k, v in priority.items()}

class Environment ():
    def __init__(self, path):
        orders, tasks, resources, stops = self.backlog_read(path)
        orders["Predecessora"] = orders["Predecessora"].fillna(False)
        n_orders = orders["OS"].nunique()
        #print(n_orders)
        #print(orders)
        #print(tasks)

        self.days = []
        stops = stops["Dia"].tolist()
        n_days = resources["Dia"].nunique()

        for i in range(1, n_days+1):
            day = resources.loc[resources["Dia"] == f"Dia_{i}"]
            abilities = day["Habilidade"].tolist()
            hours = day["HH_Disponivel"].tolist()
            stop = False

            if i in stops:
                stop = True
            self.days.append(self.Day(i, abilities, hours, stop))


        self.state_space = self.State_space(orders=orders, tasks=tasks)

        self.adjust_priorities()

        for i in range(1, n_orders+1):
            os_name = f"OS_{i}"
            os_tasks = tasks.loc[tasks["OS"] == os_name]
            #print(os_tasks)
            order = self.state_space.states[os_name]

            abilities = os_tasks["Habilidade"].tolist()
            hours = os_tasks["Duração"].tolist()
            quantities = os_tasks["Quantidade"].tolist()

            for i in range(len(abilities)):
                #print(abilities[i], hours[i], quantities[i])
                order.add_task(abilities[i], hours[i], quantities[i])

            order.tasks.reverse()




    def adjust_priorities(self):
        states = list(self.state_space.states.items())
        #print(teste)
        states.sort(key = lambda x: priority[x[1].priority])

        for state in states:
            order = state[1]
            pred = order.predecessor
            if pred and (priority[self.state_space.states[pred].priority] < priority[order.priority]):
                self.state_space.states[pred].priority = order.priority


    def backlog_read(self, path):
        backlog = pd.ExcelFile(path)
        sheets = []

        for sheet in backlog.sheet_names:
            df = pd.read_excel(backlog, sheet_name=sheet)
            sheets.append(df)

        return sheets
    

    class State_space ():
        def __init__(self, orders, tasks):
            self.states = {}
            for i in range(len(orders)):
                name, condition, prio, predecessor = orders.iloc[i]
                order = self.Order(condition, prio, predecessor)
                self.states[name] = order

            #for state in self.states:
                #self.states[state].print_order(state)


        class Order ():
            def __init__(self, condition, prio, predecessor):
                self.condition = condition
                self.priority = prio
                self.predecessor = predecessor
                self.done = False
                self.tasks = []

            def add_task(self, ability, time, quantity):
                new_task = self.Task(ability, time, quantity)
                self.tasks.append(new_task)

            def print_order(self, name):
                print(f"name: {name}, condition: {self.condition}, priority: {self.priority}, predecessor: {self.predecessor}")

            def do_order(self):
                task = self.tasks[-1]
                ability, time = task.do_task()

                if task.done:
                    self.tasks.pop()

                if len(self.tasks) == 0:
                    self.done = True

                return ability, time


            class Task ():
                def __init__(self, ability, time, quantity):
                    self.ability = ability
                    self.time = time
                    self.quantity = quantity
                    self.done = False

                def do_task(self):
                    self.quantity -= 1
                    if self.quantity == 0:
                        self.done = True
                    
                    return self.ability, self.time
                

    class Day ():
        def __init__(self, date, abilities, hours, stop):
            self.date = date
            self.resources = {abilities[i]: hours[i] for i in range(len(abilities))}
            #print(self.resources)
            self.total_resources = {abilities[i]: hours[i] for i in range(len(abilities))}
            self.stop = stop


        def print_day(self):
            print(self.resources, self.stop)


    def get_action_space (self, day):
        action_space = []
        restraints = self.days[day]
        print(day, restraints.resources)

        for idx, state in enumerate(self.state_space.states):
            order = self.state_space.states[state]
            
            pred = order.predecessor
            
            #if pred:
            #    print(self.state_space.states[order.predecessor].done)
            predecessor_done = True if order.predecessor == False or self.state_space.states[order.predecessor].done else False

            if restraints.stop == True or order.done or not predecessor_done:
                continue
            
            task = order.tasks[-1]
            if restraints.resources[task.ability] < task.time and restraints.resources[task.ability]-task.time < 0:
                continue
            
            #print(state)
            action_space.append([state, priority[self.state_space.states[state].priority], task.time])


        return action_space