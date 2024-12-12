import ast
import pandas as pd

fileLocation = '/Users/Admin/Desktop/DjangoProject/lotto 10.12/lotto-master/rawLotto.csv'
data = pd.read_csv(fileLocation)

output_file = "output.csv"

# Prepare an empty list to store transformed data
transformed_data = []

# Loop through each row in the DataFrame
for index, row in data.iterrows():
    for column in data.columns:
        transformed_data.append({
            "lotto": row[column],
            "type": column
        })

# Convert the transformed data into a new DataFrame
transformed_df = pd.DataFrame(transformed_data)

# Save the transformed data to a new CSV file
transformed_df.to_csv(output_file, index=False)

print(f"Data transformed and saved to {output_file}")
