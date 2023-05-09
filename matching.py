from ast import MatchOr
import pandas as pd
from pymongo import MongoClient
import difflib
import os
from dotenv import load_dotenv

client = MongoClient(os.getenv("MONGO_URI"))
db = client['VolunteerHub']
collection = db['missions']

df = pd.DataFrame(list(collection.find()))

def get_recommended_missions(user_id):
    user_skills = db.User.find_one({'_id': user_id})['skills']

    missions = db.Mission.find()

    recommended_missions = []
    

    for mission in missions:
        for skill in mission['SkillsRequired']:
            if skill in user_skills:

                recommended_missions.append(mission)
                break
            
        skill = difflib.SequenceMatcher(None, skill, user_skills)
        matching_blocks = MatchOr.get_matching_blocks()
        total_length = sum([block.size for block in matching_blocks])
        percentage = (total_length * 100) / max(len(skill), len(user_skills))
    return recommended_missions,percentage



# mission_rec = ['mission' + str(i) for i in range(len(get_recommended_missions))]
# df[mission_rec] = pd.DataFrame(get_recommended_missions)

# def matching(row):
#     last_missions = row[mission_rec].sort_values(ascending=False)
#     return ', '.join(last_missions.index)

# df['matching'] = df.apply(matching, axis=1)


# for index, row in df.iterrows():
#     record = row.to_dict()
#     collection.update_one({'_id': record['_id']}, {'$set': record}, upsert=True)