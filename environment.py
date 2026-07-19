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
            self.days.append(self.Day(abilities, hours, stop))

        self.state_space = self.State_space(orders=orders, tasks=tasks)
        for day in self.days:
            day.print_day()

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

            def print_order(self, name):
                print(f"name: {name}, condition: {self.condition}, priority: {self.priority}, predecessor: {self.predecessor}")


            class Task ():
                def __init__(self, ability, time, quantity):
                    self.ability = ability
                    self.time = time
                    self.quantity = quantity
                    self.done = False
                

    class Day ():
        def __init__(self, abilities, hours, stop):
            self.resources = {ability: hour for ability in abilities for hour in hours}
            self.stop = stop

        def print_day(self):
            print(self.resources, self.stop)