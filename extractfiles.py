from github import Github
import pandas as pd

ACCESS_TOKEN = '821f643807b3d0078f309d35531c7e59d577aa43'
g = Github(ACCESS_TOKEN)

reposdf = pd.read_csv("./repos.csv")
repositories = reposdf['Name'].tolist()
name = "Bigkoo/Android-PickerView"
repo = g.get_repo(name)
name = name.replace("/", "_")

dates = []
filenames = []
prevfnames = []
totals = []
adds = []
dels = []

commits = repo.get_commits()
for commit in commits:
    date = commit.commit.author.date.date()
    date = date.replace(day=1)

    files = commit.files

    for file in files:
        dates.append(date)
        fname = file.filename
        if '/' in fname:
            fsplit = fname.split('/')
            fname = fsplit[len(fsplit) - 1]
        filenames.append(fname)
        # prevfnames.append(file.previous_filename)
        totals.append(file.changes)
        adds.append(file.additions)
        dels.append(file.deletions)


data = {'Date': dates, 'Filename': filenames, 'Total': totals, 'Additions': adds, 'Deletions': dels}
df = pd.DataFrame(data=data)

df.to_csv('./repositories/' + name + '.csv', index=False)

if name not in repositories:
    repositories.append(name)
datar = {'Name': repositories}
dfr = pd.DataFrame(data=datar)

dfr.to_csv('./repos.csv', index=False)
