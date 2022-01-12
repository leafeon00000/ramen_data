import pandas as pd

header = ["name", "age", "weight"]

df2 = pd.DataFrame(header, columns=header)

df = pd.DataFrame({
    'name': ['isshiki', 'endo', 'kawasaki'],
    'age': [20, 25, 24],
    'weight': [55.44, 66.77, 123.456]
})

df2.to_csv("./kensho/csv/test_csv.csv", index=False, header=True)
