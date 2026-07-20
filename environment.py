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
                order.add_task(abilities[i], hours[i], quantities[i])


    def adjust_priorities(self):
        states = list(self.state_space.states.items())
        
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


        class Order ():
            def __init__(self, condition, prio, predecessor):
                self.condition = condition
                self.priority = prio
                self.predecessor = predecessor
                self.allocated = False
                self.done = False
                self.tasks = []
                self.current_task = 0

            def add_task(self, ability, time, quantity):
                new_task = self.Task(ability, time, quantity)
                self.tasks.append(new_task)

            def print_order(self, name):
                print(f"name: {name}, condition: {self.condition}, priority: {self.priority}, predecessor: {self.predecessor}")

            def do_order(self, date):
                task = self.tasks[self.current_task]
                ability, time = task.do_task(date)

                if task.done:
                    self.current_task += 1

                
                if len(self.tasks) == self.current_task:
                    self.done = True

                return ability, time


            class Task ():
                def __init__(self, ability, time, quantity):
                    self.ability = ability
                    self.time = time
                    self.quantity = quantity
                    self.done = False
                    self.executed = []

                def do_task(self, day):
                    self.quantity -= 1
                    if self.quantity == 0:
                        self.done = True
                        self.executed.append(day)
                    
                    return self.ability, self.time
                

    class Day ():
        def __init__(self, date, abilities, hours, stop):
            self.date = date
            self.resources = {abilities[i]: hours[i] for i in range(len(abilities))}
            
            self.total_resources = {abilities[i]: hours[i] for i in range(len(abilities))}
            self.stop = stop


        def print_day(self):
            print(self.resources, self.stop)


    def get_action_space (self, day):
        action_space = []
        restraints = self.days[day]


        for idx, state in enumerate(self.state_space.states):
            order = self.state_space.states[state]
            
            pred = order.predecessor

            predecessor_done = True if order.predecessor == False or self.state_space.states[order.predecessor].done else False

            if restraints.stop == True or order.done or not predecessor_done or order.allocated:
                continue
            
            task = order.tasks[order.current_task]
            if restraints.resources[task.ability] < task.time and restraints.resources[task.ability]-task.time < 0:
                continue
            

            action_space.append([state, priority[self.state_space.states[state].priority], task.time])


        return action_space
    
    def reset (self, allocated_orders, not_in_sol):
        for day in self.days:
            day.resources = day.total_resources.copy()

        for info in allocated_orders:
            order = self.state_space.states[info[0][0]]
            for task in order.tasks:
                for date in task.executed:
                    resources = self.days[date-1].resources
                    resources[task.ability] = resources[task.ability]-task.time

            order.allocated = True


        if not_in_sol not in allocated_orders[0] and not_in_sol is not None:
            order = self.state_space.states[not_in_sol[0]]
            for task in order.tasks:
                for date in task.executed:
                    resources = self.days[date-1].resources
                    resources[task.ability] = resources[task.ability]-task.time

            order.allocated = True