# import pickle
import pandas as pd


# repositories = []
# repositories.append("Bigkoo_Android_PickerView")
#
# datar = {'Name': repositories}
# dfr = pd.DataFrame(data=datar)
#
# dfr.to_hdf('../data/data.h5', key='repos', mode='w')
#

df = pd.read_csv("../data/repositories/Bigkoo_Android_PickerView.csv")
print(df.dtypes)





