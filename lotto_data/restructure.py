import ast

import pandas as pd

fileLocation = '/Users/admin/Documents/CodeAll/db_prog/lotto/lotto_data/lotto.csv'
df = pd.read_csv(fileLocation, dtype={'prize_1st': str, 'prize_2digits': str})

def safe_parse(val):
    if isinstance(val, (list, tuple)):
        return val
    if pd.isna(val):
        return []
    if isinstance(val, str):
        try:
            return ast.literal_eval(val)
        except (ValueError, SyntaxError):
            return []
    return val

list_columns = ['prize_pre_3digit', 'prize_sub_3digits', 'nearby_1st', 'prize_2nd', 'prize_3rd', 'prize_4th', 'prize_5th']
for col in list_columns:
    df[col] = df[col].apply(safe_parse)

f = open("lotto_all.csv", "w")
f.write("date,lotto,type\n")
for row in df.itertuples():
    date = str(row.date)
    if not pd.isna(row.prize_1st):
        f.write(",".join([date, str(row.prize_1st), "\"prize_1st\""]) + "\n")
    if not pd.isna(row.prize_2digits):
        f.write(",".join([date, str(row.prize_2digits), "\"prize_2digits\""]) + "\n")
    for prize in row.prize_pre_3digit:
        f.write(",".join([date, str(prize), "\"prize_pre_3digit\""]) + "\n")
    for prize in row.prize_sub_3digits:
        f.write(",".join([date, str(prize), "\"prize_sub_3digits\""]) + "\n")
    for prize in row.nearby_1st:
        f.write(",".join([date, str(prize), "\"nearby_1st\""]) + "\n")
    for prize in row.prize_2nd:
        f.write(",".join([date, str(prize), "\"prize_2nd\""]) + "\n")
    for prize in row.prize_3rd:
        f.write(",".join([date, str(prize), "\"prize_3rd\""]) + "\n")
    for prize in row.prize_4th:
        f.write(",".join([date, str(prize), "\"prize_4th\""]) + "\n")
    for prize in row.prize_5th:
        if(prize.isdigit()):
            f.write(",".join([date, str(prize), "\"prize_5th\""]) + "\n")
f.close()