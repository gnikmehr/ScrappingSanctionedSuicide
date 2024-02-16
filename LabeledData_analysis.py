import pandas as pd

data = pd.read_csv("data/LabeledData.csv")
data = data.dropna(axis=1, how='all')

print(data.head())
print(len(data))

unique_users = data['author'].unique()
print("Number of unique users: ", len(unique_users))

unique_threads = data['name of thread'].unique()
print("Number of unique threads: ", len(unique_threads))

users_thread = {}
users_len = {}
for u in unique_users:
    temp = data[data['author'] == u]
    users_thread[u] = list(temp['name of thread'])
    users_len[u] = len(list(temp['name of thread']))


max_user = max(users_len, key=users_len.get)
print("Maximum threads that a user posted in: ", users_len[max_user])
# print(users_thread[max_user])


raw_data_path = "/home/golnaz/data/Processed/"

titles = []
for title in data['name of thread']:
    file_name = raw_data_path + title + ".json"
    thread_info = pd.read_json(file_name)
    titles.append(thread_info['title'])

data['title'] = titles

data.to_csv("data/labeled_data_with_title.csv", encoding='utf-8')
