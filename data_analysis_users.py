import pandas as pd
import glob
from tqdm import tqdm
import json
import matplotlib.pyplot as plt
from collections import Counter


processed_data_path = "/home/golnaz/data/Processed/"
data_path = "/home/golnaz/data/data/*"

file_list =glob.glob(data_path)

users = []
user_threads = {}
users_info ={}
threads_with_no_users = []
damaged_files = []
for file in tqdm(file_list):
    try:
        thread_info = pd.read_json(file)
        if 'users' in thread_info:
            users_list = thread_info["users"].tolist()[0]
            for u in users_list:
                if u['name'] not in users_info:
                    users_info[u['name']] = {"title": u["title"], "register_date": u["register_date"], "number_of_posts": u["number_of_posts"]}
                    user_threads[u['name']] = [thread_info['title'].tolist()[0]]
                else:
                    user_threads[u['name']].append(thread_info['title'].tolist()[0])
                    pass
        else:
            threads_with_no_users.append(thread_info["title"].tolist()[0])
    except ValueError:
        damaged_files.append(file)
    

print("Number of unique users ", len(users_info))
json_file_path = "users_info.json"

# Write the dictionary to a JSON file
with open(json_file_path, 'w') as jsonfile:
    json.dump(users_info, jsonfile, indent=4)

json_file_path2 = "user_threads.json"

# Write the dictionary to a JSON file
with open(json_file_path2, 'w') as jsonfile:
    json.dump(user_threads, jsonfile, indent=4)


print("Number of threads_with_no_users", len(threads_with_no_users))
print(threads_with_no_users)

print("Number of damaged_files", len(damaged_files))
print(damaged_files)

# max_value = max(thread_lens)
# thread_lens.remove(max_value)
# value_counts = Counter(thread_lens)

# values = list(value_counts.keys())
# counts = list(value_counts.values())

# print(max(counts))
# plt.bar(values, counts, color='blue')
# plt.xlabel('Values')
# plt.ylabel('Counts')
# plt.title('Value Counts threads that a user posted in')
# plt.show() 
