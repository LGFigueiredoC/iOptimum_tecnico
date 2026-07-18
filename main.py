import pandas as pd

file_path = "backlog_desafio_500.xlsx"

def backlog_read(path):
    backlog = pd.ExcelFile(path)
    sheets = []

    for sheet in backlog.sheet_names:
        df = pd.read_excel(backlog, sheet_name=sheet)
        sheets.append(df)

    return sheets


def create_solution(path):
    ordem, tarefas, recursos, paradas = backlog_read(path)

    