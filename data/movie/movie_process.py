
import csv
import json
import pandas as pd
import random
import numpy as np

f = open('ratings.dat', 'r')
data = f.readlines()
f = open('movies.dat', 'r', encoding='ISO-8859-1')
movies = f.readlines()
movie_names = [_.split('::')[1] for _ in movies]
movie_ids = [_.split('::')[0] for _ in movies]
movie_dict = dict(zip(movie_ids, movie_names))
id_mapping = dict(zip(movie_ids, range(len(movie_ids))))


interaction_dicts = dict()
for line in data:
    user_id, movie_id, rating, timestamp = line.split('::')
    if user_id not in interaction_dicts:
        interaction_dicts[user_id] = {
            'movie_id': [],
            'rating': [],
            'timestamp': [],
            'movie_title': [],
        }
    interaction_dicts[user_id]['movie_id'].append(movie_id)
    interaction_dicts[user_id]['rating'].append(int(float(rating) > 3.0))
    interaction_dicts[user_id]['timestamp'].append(timestamp)
    interaction_dicts[user_id]['movie_title'].append(movie_dict[movie_id])


with open('all.csv', 'w') as f:

    writer = csv.writer(f)
    writer.writerow(['user_id', 'item_id', 'rating', 'timestamp', 'item_title'])
    for user_id, user_dict in interaction_dicts.items():
        writer.writerow([user_id, user_dict['movie_id'], user_dict['rating'], user_dict['timestamp'], user_dict['movie_title']])
    


sequential_interaction_list = []
seq_len = 10
for user_id in interaction_dicts:
    temp = zip(interaction_dicts[user_id]['movie_id'], interaction_dicts[user_id]['rating'], interaction_dicts[user_id]['timestamp'], interaction_dicts[user_id]['movie_title'])
    temp = sorted(temp, key=lambda x: int(x[2]))
    result = zip(*temp)
    interaction_dicts[user_id]['movie_id'], interaction_dicts[user_id]['rating'], interaction_dicts[user_id]['timestamp'], interaction_dicts[user_id]['movie_title'] = [list(_) for _ in result]
    for i in range(10, len(interaction_dicts[user_id]['movie_id'])):
        sequential_interaction_list.append(
            [user_id, interaction_dicts[user_id]['movie_title'][i - seq_len: i],
            interaction_dicts[user_id]['movie_id'][i-seq_len:i], 
            interaction_dicts[user_id]['rating'][i-seq_len:i], 
            interaction_dicts[user_id]['movie_id'][i], interaction_dicts[user_id]['rating'][i], interaction_dicts[user_id]['timestamp'][i].strip('\n')]
        )
print(len(sequential_interaction_list))



sequential_interaction_list = sorted(sequential_interaction_list, key=lambda x: int(x[-1]))
with open('./train.csv', 'w') as f:
    writer = csv.writer(f)
    writer.writerow(['user_id', 'history_movie_title', 'history_movie_id', 'history_rating', 'movie_id', 'rating', 'timestamp'])
    writer.writerows(sequential_interaction_list[:int(len(sequential_interaction_list)*0.8)])
with open('./valid.csv', 'w') as f:
    writer = csv.writer(f)
    writer.writerow(['user_id', 'history_movie_title', 'history_movie_id', 'history_rating', 'movie_id', 'rating', 'timestamp'])
    writer.writerows(sequential_interaction_list[int(len(sequential_interaction_list)*0.8):int(len(sequential_interaction_list)*0.9)])
with open('./test.csv', 'w') as f:
    writer = csv.writer(f)
    writer.writerow(['user_id', 'history_movie_title', 'history_movie_id', 'history_rating', 'movie_id', 'rating', 'timestamp'])
    writer.writerows(sequential_interaction_list[int(len(sequential_interaction_list)*0.9):])


def csv_to_json(input_path, output_path, sample=False, cal=False):
    data = pd.read_csv(input_path)
    if sample:
        data = data.sample(n=5000, random_state=42).reset_index(drop=True)
    with open(output_path, 'w') as f:
        json.dump(data.to_dict('records'), f, indent=4)



csv_to_json('./train.csv', './train.json')
csv_to_json('./valid.csv', './valid.json')
csv_to_json('./test.csv', './test.json')
csv_to_json('./valid.csv', './valid_5000.json', sample=True)
csv_to_json('./test.csv', './test_5000.json', sample=True)
