import pandas as pd
import json

def load_careers_data(path="data/careers.csv"):
    return pd.read_csv(path)

def load_roadmap_template(path="data/roadmap_template.json"):
    with open(path, "r") as file:
        return json.load(file)

