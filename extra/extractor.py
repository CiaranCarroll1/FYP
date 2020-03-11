from github import Github
import pandas as pd

ACCESS_TOKEN = '821f643807b3d0078f309d35531c7e59d577aa43'
g = Github(ACCESS_TOKEN)

repo = g.get_repo("gothinkster/realworld")

dates = []
adds = []
dels = []
values = []
count = -1
shas = []
filenames = []
filetotal = []

commits = repo.get_commits()
for commit in commits:
    date = commit.commit.author.date.date()
    date = date.replace(day=1)
    addition = commit.stats.additions
    deletion = commit.stats.deletions
    total = commit.stats.total

    files = commit.files

    for file in files:
        if file.filename in filenames:
            index = filenames.index(file.filename)
            filetotal[index] = filetotal[index] + file.changes
        else:
            filenames.append(file.filename)
            filetotal.append(file.changes)

    if date in dates:
        index = dates.index(date)
        adds[index] = adds[index] + addition
        dels[index] = dels[index] + deletion
        values[index] = values[index] + total
    else:
        dates.append(date)
        adds.append(addition)
        dels.append(deletion)
        values.append(total)


data = {'Date': dates, 'Additions': adds, 'Deletions': dels, 'Total': values}
df = pd.DataFrame(data=data)

df.to_csv('./gothinkster-realworld.csv', index=False)

data2 = {'Filename': filenames, 'Changes': filetotal}
df2 = pd.DataFrame(data=data2)

df2.to_csv('./gothinkster-realworld-files.csv', index=False)
