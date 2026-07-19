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
        orders, tasks, self.resources, self.stops = self.backlog_read(path)
        orders["Predecessora"] = orders["Predecessora"].fillna(False)

        self.days = []
        stops = self.stops["Dia"].tolist()

        for i in range(1, 6):
            day = self.resources.loc[self.resources["Dia"] == f"Dia_{i}"]
            abilities = day["Habilidade"].tolist()
            hours = day["HH_Disponivel"].tolist()
            stop = False

            if i in stops:
                stop = True
            self.days.append(self.Day(i, abilities, hours, stop))


        self.state_space = self.State_space(orders=orders, tasks=tasks)

        # for order in self.state_space:
        #     current = self.state_space[order]
        #     pred = self.state_space[current.predecessor]

        #     if priority[current.priority] > priority[pred.priority]:
        #         pred.priority
        # for day in self.days:
        #     day.print_day()


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

            for state in self.states:
                self.states[state].print_order(state)


        class Order ():
            def __init__(self, condition, prio, predecessor):
                self.condition = condition
                self.priority = prio
                self.predecessor = predecessor
                self.done = False
                self.tasks = []


            def print_order(self, name):
                print(f"name: {name}, condition: {self.condition}, priority: {self.priority}, predecessor: {self.predecessor}")

            def do_order(self):
                task = self.tasks[0]
                ability, time = task.do_task()

                if task.done:
                    self.tasks.pop(0)

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
            self.resources = {ability: hour for ability in abilities for hour in hours}
            self.total_resources = {ability: hour for ability in abilities for hour in hours}
            self.stop = stop


        def print_day(self):
            print(self.resources, self.stop)


    def get_action_space (self, day):
        action_space = []
        restraints = self.days[day]

        for idx, state in enumerate(self.state_space):
            order = self.state_space[state]
            predecessor_done = True if self.state_space[order.predecessor].done else False
            task = order.tasks[0]

            if restraints.stop == True or order.done or not predecessor_done or restraints.resources[task.ability] < task.time:
                continue

            action_space.append([state, priority[self.state_space[state].priority], restraints.resources[task.ability] - task.time])


        return action_space