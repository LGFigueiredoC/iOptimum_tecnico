import pandas as pd
import environment
from algorithm import create_solution

file_path = "backlog_desafio_1000.xlsx"

sol = create_solution(file_path)
print(sol)