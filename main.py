import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import date

if __name__ == "__main__":

    # URL = "https://candidat.pole-emploi.fr/offres/recherche?motsCles=Data+scientist&offresPartenaires=true&range=0-19&rayon=40&tri=0"
    # URL = "https://candidat.pole-emploi.fr/offres/emploi/data-scientist/s28m15"
    URL = "https://candidat.pole-emploi.fr/offres/recherche?motsCles=Data+scientist&offresPartenaires=true&range=0-100&rayon=100&tri=1"

    r = requests.get(URL)
    soup = BeautifulSoup(r.content, "lxml")

    jobs = soup.select('a[id^="pagelink"]')

    df = pd.DataFrame(columns=["id", "url", "date", "title", "location", "description", "info", "horaires", "salairemin","salairemax","entreprise","experience"])

    for job in jobs:
        
        job_link = job.get("href")

        r = requests.get(f"https://candidat.pole-emploi.fr{job_link}")

        if r.status_code == 200:

            soup = BeautifulSoup(r.content, "lxml")

            df_ =  pd.DataFrame.from_dict(
                {
                    "id": job_link.split("/")[-1],
                    "url": f"https://candidat.pole-emploi.fr{job_link}",
                    "date": soup.find("p", class_="t5 title-complementary").find("span").get("content"),
                    "title": soup.title.string,
                    "location": soup.find("p", itemprop="jobLocation").find("span", itemprop="name").text,
                    "description": soup.find_all("div", class_="description")[0].p.string,
                    "info": soup.find_all("div", class_="description-aside")[0].dd.text,
                    "horaires": soup.find("div", class_="description-aside", ).find("dd", itemprop="workHours").text.strip() if soup.find("div", class_="description-aside", ).find("dd", itemprop="workHours") else "unspecified",
                    "salairemin": soup.find("div", class_="description-aside", ).find("span", itemprop="minValue").get("content") if soup.find("div", class_="description-aside", ).find("span", itemprop="minValue") else "unspecified",
                    "salairemax": soup.find("div", class_="description-aside", ).find("span", itemprop="maxValue").get("content") if soup.find("div", class_="description-aside", ).find("span", itemprop="maxValue") else "unspecified",
                    "entreprise": soup.find("h3", class_="t4 title").text.strip() if soup.find("h3", class_="t4 title") else "unspecified",
                    "experience": soup.find_all("ul", class_="skill-list list-unstyled")[0].find("span", class_="skill-name").text,
                },
                orient="index",
                ).T
            
            df = pd.concat([df, df_], ignore_index=True)

    df["contrat"] = df["info"].str.strip().str.split("\n\n").str[0]
    # df["apprentissage"] = df["info"].str.strip().str.split("\n\n").str[1] == "Contrat apprentissage"
    df["debutant"] = df["experience"].str.contains("Débutant")
    df["entreprise"] = df["entreprise"].str.capitalize()

    df.to_csv(f"./data/raw/df_{date.today()}.csv", index=False)