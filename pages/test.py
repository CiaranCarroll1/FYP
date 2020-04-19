# import pickle
import pandas as pd


df = pd.read_hdf('../data/data.h5', "Bigkoo_Android_PickerView")
# print(df)
df['Filename'] = df['Filename'].str.rsplit("/", 1).str[1]
print(df)

# string = "/src/hello/world/filename.txt"
#
# print(string.rsplit("/", 1))



