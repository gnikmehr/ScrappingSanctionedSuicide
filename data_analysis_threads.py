import pandas as pd
# import matplotlib
# matplotlib.use('TkAgg') 
import matplotlib.pyplot as plt


def convert_to_numeric(value):
    if 'K' in value:
        return int(value.replace('K', '')) * 1000
    elif 'M' in value:
        return int(value.replace('M', '')) * 1000000
    else:
        return int(value)

thread_df = pd.read_json("All_Threads.json")

print("Raw thread data length: ", len(thread_df))

thread_df = thread_df[thread_df['replies'] != '–']

print("Raw thread data length after drop '-': ", len(thread_df))


thread_df['views'] = thread_df['views'].apply(convert_to_numeric)
thread_df['replies'] = thread_df['replies'].apply(convert_to_numeric)

print(thread_df.head())

max_views = thread_df['views'].max()
min_views = thread_df['views'].min()

print("max_views", max_views)
print("min_views", min_views)

max_replies = thread_df['replies'].max()
min_replies = thread_df['replies'].min()

print("max_replies", max_replies)
print("min_replies", min_replies)

plt.hist(thread_df['replies'], bins=10, color='blue', edgecolor='black')

# Add labels and title
plt.xlabel('Values')
plt.ylabel('Frequency')
plt.title('Distribution of Values')

plt.savefig('dist.png')
# Display the plot
plt.show()

print(thread_df['replies'].describe())
print("---")
print(thread_df['views'].describe())

