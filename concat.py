import pandas as pd
import numpy as np
from datetime import date
from glob import glob

import matplotlib.pyplot as plt

plt.style.use("ggplot")


def adjust_salary(df: pd.DataFrame, column: str) -> np.array:
    return np.where(df[column] < 10000, df[column] * 12, df[column])


def count_skills(group):
    return pd.concat(
        [
            group["description"]
            .str.contains(skill)
            .value_counts(normalize=True)
            .rename(skill.capitalize())
            for skill in skills
        ],
        axis=1,
    ).T


df_list = [pd.read_csv(fn) for fn in glob("./data/raw/*.csv")]
df = pd.concat(df_list, ignore_index=True)
df = df.drop_duplicates(subset="id")
df["description"] = df["description"].str.lower()
df["debutant"] = df["experience"].str.contains("Débutant")

df.to_csv(f"./data/transformed/df_merged_{date.today()}.csv", index=False)

no_salary = df.query("salairemin == 'unspecified' | salairemax == 'unspecified'")
content = f"{no_salary.shape[0]} offer with unpecified salary out of {df.shape[0]}"

content += "\n # Salaires moyen :\n"

df_salaire = (
    df[~df["debutant"]]
    .query("salairemin != 'unspecified'")[["salairemin", "salairemax"]]
    .astype(float)
)
df_salaire["salaireavg"] = (df_salaire["salairemax"] + df_salaire["salairemin"]) / 2

salaire_avg = adjust_salary(df_salaire, "salaireavg").mean()
content += f"\n- Salaire moyen : {salaire_avg.round()} euros/ans soit {(salaire_avg/12).round()} par mois"

salairemin_avg = adjust_salary(df_salaire, "salairemin").mean()
content += f"\n- Salaire min moyen : {salairemin_avg.round()} euros/ans soit {(salairemin_avg/12).round()} par mois"

salairemax_avg = adjust_salary(df_salaire, "salairemax").mean()
content += f"\n- Salaire max moyen : {salairemax_avg.round()} euros/ans soit {(salairemax_avg/12).round()} par mois"

# Débutant :
content += "\n\n# Salaires débutant :\n"
df_debutant = df[df["debutant"]]

df_salaire_debutant = df_debutant.query("salairemin != 'unspecified'")[
    ["salairemin", "salairemax"]
].astype(float)
df_salaire_debutant["salaireavg"] = (
    df_salaire_debutant["salairemax"] + df_salaire_debutant["salairemin"]
) / 2

salaire_avg = adjust_salary(df_salaire_debutant, "salaireavg").mean()
content += f"\n- Salaire moyen : {salaire_avg.round()} euros/ans soit {(salaire_avg/12).round()} par mois"

salairemin_avg = adjust_salary(df_salaire_debutant, "salairemin").mean()
content += f"\n- Salaire min moyen : {salairemin_avg.round()} euros/ans soit {(salairemin_avg/12).round()} par mois"

salairemax_avg = adjust_salary(df_salaire_debutant, "salairemax").mean()
content += f"\n- Salaire max moyen : {salairemax_avg.round()} euros/ans soit {(salairemax_avg/12).round()} par mois"

plt.hist(
    [
        adjust_salary(df_salaire_debutant, "salaireavg"),
        adjust_salary(df_salaire, "salaireavg"),
    ],
    bins=15,
)
plt.title("Data Scientist Salary")
plt.legend(["Debutant", "Other"])
plt.tight_layout()
plt.savefig("./docs/salaryplot.png")

content += "\n# \n\n ![](./docs/salaryplot.png)"

skills = [
    "python",
    "sql",
    "spark",
    "machine learning",
    "intelligence artificielle",
    "pytorch",
    "tensorflow",
    "deep learning",
    "java",
    "scikit-learn",
    "pandas",
    "numpy",
    "scipy",
]

df_skills = df.groupby("debutant").apply(count_skills).unstack().T.xs(True).fillna(0)
df_skills.sort_values(True).plot(
    kind="barh", width=0.8, edgecolor="black", title="Skills Mentioned in %"
)
plt.xlim([0, 1])
plt.tight_layout()

plt.savefig("./docs/skillsplot.png")

content += "\n\n# Top skills\n ![](./docs/skillsplot.png)"

with open("README.md", "w") as f:
    f.write(content)
