
import json
from tqdm import tqdm


metadata = []
with open('meta_Video_Games.json') as f:
    for line in f:
        try:
            metadata.append(eval(line))
        except json.decoder.JSONDecodeError:
            print(f"Skipping invalid line: {line.strip()}")


id_title = {}
for meta in tqdm(metadata):
    if 'title' in meta:
        if len(meta['title']) > 1: # remove the item without title
            id_title[meta['asin']] = meta['title']

with open('id_title', 'w') as json_file:
    json.dump(id_title, json_file, indent=4)
with open('id_title', 'r') as json_file:
    id_title = json.load(json_file)  

print('done loading')
with open('Video_Games_5.json') as f:
    reviews = [json.loads(line) for line in f]
users = set()
items = set()
for review in tqdm(reviews):
    users.add(review['reviewerID'])
    items.add(review['asin'])
item2id = dict()
count = 0
for item in items:
    item2id[item] = count
    count += 1
print(len(users), len(items), len(reviews), len(reviews) / (len(users) * len(items)))



id_item = {}
cnt = 0


users = dict()
for review in tqdm(reviews):
    user = review['reviewerID']
    if 'asin' not in review:
        break
    item = review['asin']
    if item not in id_title:
        continue
    if review['asin'] not in id_item:
        id_item[review['asin']] = cnt
        cnt += 1
    if 'overall' not in review:
        continue
    if 'unixReviewTime' not in review:
        continue
    if user not in users:
        users[user] = {
            'items': [],
            'ratings': [],
            'timestamps': [],
            'reviews': []
        }
    users[user]['items'].append(item)
    users[user]['ratings'].append(review['overall'])
    users[user]['timestamps'].append(review['unixReviewTime'])






user_id = 0
interactions = []
B = []
for key in tqdm(users.keys()):
    items = users[key]['items']
    ratings = users[key]['ratings']
    timestamps = users[key]['timestamps']
    all = list(zip(items, ratings, timestamps))
    res = sorted(all, key=lambda x: int(x[-1]))
    items, ratings, timestamps = zip(*res)
    items, ratings, timestamps = list(items), list(ratings), list(timestamps)
    users[key]['items'] = items
    users[key]['item_ids'] = [item2id[x] for x in items]
    users[key]['item_titles'] = [id_title[x] for x in items]
    users[key]['ratings'] = ratings
    users[key]['timestamps'] = timestamps
    for i in range(min(10, len(items) - 1), len(items)):
        st = max(i - 10, 0)
        interactions.append([key, users[key]['items'][st: i], users[key]['items'][i], users[key]['item_ids'][st: i], users[key]['item_ids'][i], users[key]['item_titles'][st: i], users[key]['item_titles'][i], ratings[st: i], ratings[i], int(timestamps[i])])   
print(len(interactions))
interactions = sorted(interactions, key=lambda x: x[-1])
import csv
with open('./train.csv', 'w') as f:
    csvwriter = csv.writer(f)
    csvwriter.writerow(['user_id', 'item_asins', 'item_asin', 'history_item_id', 'item_id', 'history_item_title', 'item_title', 'history_rating', 'rating', 'timestamp'])
    csvwriter.writerows(interactions[:int(len(interactions) * 0.8)])
with open('./valid.csv', 'w') as f:
    csvwriter = csv.writer(f)
    csvwriter.writerow(['user_id', 'item_asins', 'item_asin', 'history_item_id', 'item_id', 'history_item_title', 'item_title', 'history_rating', 'rating', 'timestamp'])
    csvwriter.writerows(interactions[int(len(interactions) * 0.8):int(len(interactions) * 0.9)])
with open('./test.csv', 'w') as f:
    csvwriter = csv.writer(f)
    csvwriter.writerow(['user_id', 'item_asins', 'item_asin', 'history_item_id', 'item_id', 'history_item_title', 'item_title', 'history_rating', 'rating', 'timestamp'])
    csvwriter.writerows(interactions[int(len(interactions) * 0.9):])
import json
import pandas as pd
import random
import numpy as np
from tqdm import tqdm
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
# csv_to_json('./test.csv', './test_50000.json', sample=True)

 
 
 
