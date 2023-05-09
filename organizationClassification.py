import os

import numpy
import spacy
from pymongo import MongoClient
import pandas as pd
from dotenv import load_dotenv


def organizations_classification():
    load_dotenv()

    # load pre-trained embeddings from spaCy
    nlp = spacy.load('en_core_web_lg')

    # connect to MongoDB database
    client = MongoClient(os.getenv("MONGO_URI"))
    db = client['VolunteerHub']
    collection = db['organizations']

    # load data
    df = pd.DataFrame(list(collection.find()))
    print(df.columns)
    # preprocess data
    sdgs = {
        "no poverty": ["poverty", "income", "inequality", "disparities", "vulnerability", "basic services"],
        "zero hunger": ["hunger", "food", "nutrition", "agriculture", "farming", "rural", "urban agriculture"],
        "good health and well-being": ["health", "well-being", "disease", "mortality", "vaccination", "mental health", "healthcare"],
        "quality education": ["education", "literacy", "skills", "knowledge", "digital literacy", "STEM", "early childhood education"],
        "gender equality": ["gender", "equality", "empowerment", "violence against women", "discrimination", "leadership"],
        "clean water and sanitation": ["water", "sanitation", "hygiene", "water scarcity", "water quality", "water management"],
        "affordable and clean energy": ["energy", "renewable", "efficiency", "access to energy", "fossil fuels", "energy conservation"],
        "decent work and economic growth": ["employment", "economy", "productivity", "entrepreneurship", "youth employment", "informal economy"],
        "industry, innovation and infrastructure": ["industry", "innovation", "infrastructure", "technology", "digital transformation", "transportation", "smart cities"],
        "reduced inequalities": ["inequality", "discrimination", "injustice", "social protection", "inclusion", "participation", "accessibility"],
        "sustainable cities and communities": ["sustainability", "urbanization", "resilience", "green spaces", "public transportation", "community development"],
        "responsible consumption and production": ["consumption", "production", "sustainability", "waste management", "circular economy", "sustainable procurement"],
        "climate action": ["climate", "emissions", "adaptation", "mitigation", "renewable energy", "carbon pricing"],
        "life below water": ["oceans", "marine", "biodiversity", "coastal ecosystems", "overfishing", "marine pollution"],
        "life on land": ["forests", "biodiversity", "land degradation", "desertification", "wildlife conservation", "sustainable forestry"],
        "peace, justice and strong institutions": ["peace", "justice", "governance", "corruption", "transparency", "rule of law"],
        "partnerships for the goals": ["partnerships", "collaboration", "cooperation", "global solidarity", "multilateralism", "partnership for development"]
    }

    # calculate cosine similarities between organization and SDGs
    sdg_similarities = []
    for i in range(len(df)):
        org_issues = ' '.join(df['issues'][i])
        org_doc = nlp(org_issues)
        org_sdgs = []
        for sdg in sdgs:
            sdg_tokens = sdgs[sdg]
            sdg_doc = nlp(' '.join(sdg_tokens))
            similarity = org_doc.similarity(sdg_doc)
            org_sdgs.append(similarity)
        sdg_similarities.append(org_sdgs)

    # add results to dataframe
    sdg_cols = ['sdg_' + str(i) for i in range(len(sdgs))]
    df[sdg_cols] = pd.DataFrame(sdg_similarities)

    # classify organizations based on top 3 SDGs
    def classify_org(row):
        top_3_sdgs = row[sdg_cols].sort_values(ascending=False)[:3]
        return ', '.join(top_3_sdgs.index)

    df['sdg_classification'] = df.apply(classify_org, axis=1)

    # save results to MongoDB database
    for index, row in df.iterrows():
        record = row.to_dict()
        collection.update_one({'_id': record['_id']}, {'$set': record}, upsert=True)
