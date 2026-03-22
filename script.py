import requests
import pandas as pd
import yagmail
import os
from dotenv import load_dotenv

load_dotenv()

APP_ID = os.getenv("ADZUNA_APP_ID")
APP_KEY = os.getenv("ADZUNA_APP_KEY")
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")

KEYWORDS = [
    "data analyst",
    "business analyst",
    "data management"
]

CITIES = [
    "Brussels",
    "Lyon"
]

LEVEL_WORDS = [
    "junior",
    "medior",
    "0-3",
    "1-3",
    "2 years",
    "3 years"
]


def get_jobs(keyword, city):
    url = "https://api.adzuna.com/v1/api/jobs/fr/search/1"

    params = {
        "app_id": APP_ID,
        "app_key": APP_KEY,
        "results_per_page": 20,
        "what": keyword,
        "where": city,
        "sort_by": "date"
    }

    r = requests.get(url, params=params)
    data = r.json()["results"]

    jobs = []

    for job in data:

        description = job["description"].lower()

       
        jobs.append({
            "id": job["id"],
            "title": job["title"],
            "company": job["company"]["display_name"],
            "location": job["location"]["display_name"],
            "url": job["redirect_url"],
            "description": job["description"][:400]
        })

    return jobs


all_jobs = []

for city in CITIES:
    for keyword in KEYWORDS:
        try:
            all_jobs += get_jobs(keyword, city)
        except:
            pass


df = pd.DataFrame(all_jobs)

if df.empty:
    print("No jobs found")
    exit()

# Anti doublons historiques
try:
    old = pd.read_csv("sent_jobs.csv")
    df = df[~df["id"].isin(old["id"])]
    df_all = pd.concat([old, df])
except:
    df_all = df

if df.empty:
    print("No new jobs")
    exit()

df_all.to_csv("sent_jobs.csv", index=False)


# Construction email
content = ""

for _, row in df.iterrows():

    content += f"""
TITLE : {row['title']}
COMPANY : {row['company']}
LOCATION : {row['location']}

{row['description']}

LINK : {row['url']}

-------------------------
"""


yag = yagmail.SMTP(EMAIL_USER, EMAIL_PASS)

yag.send(
    to=EMAIL_USER,
    subject=f"Jobs Data / Business Analyst ({len(df)} nouvelles offres)",
    contents=content
)

print("Email sent")