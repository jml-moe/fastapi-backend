"""Dataset survei sintetis kecil yang lolos seluruh penyaringan (tanpa dataset asli)."""

import numpy as np
import pandas as pd

# bidang -> (bahasa, basis data, platform, framework) yang dominan
PROFIL = {
    "Developer, back-end": (
        ["Python", "Java", "SQL"],
        ["PostgreSQL", "MySQL", "Redis"],
        ["Docker", "Amazon Web Services (AWS)"],
        ["Django", "FastAPI", "Spring Boot"],
    ),
    "Developer, front-end": (
        ["JavaScript", "TypeScript", "HTML/CSS"],
        ["SQLite", "PostgreSQL"],
        ["Docker", "Vercel"],
        ["React", "Vue.js", "Angular"],
    ),
    "Data scientist or machine learning specialist": (
        ["Python", "R", "SQL"],
        ["PostgreSQL", "SQLite", "Elasticsearch"],
        ["Amazon Web Services (AWS)", "Google Cloud"],
        ["FastAPI", "Flask"],
    ),
}
SEMUA = (
    ["Python", "Java", "SQL", "JavaScript", "TypeScript", "HTML/CSS", "R"],
    ["PostgreSQL", "MySQL", "Redis", "SQLite", "Elasticsearch"],
    ["Docker", "Amazon Web Services (AWS)", "Vercel", "Google Cloud"],
    ["Django", "FastAPI", "Spring Boot", "React", "Vue.js", "Angular", "Flask"],
)


def _pilih(rng, dominan, semua, wajib=False):
    ada = [t for t in semua if rng.random() < (0.8 if t in dominan else 0.1)]
    if wajib and not ada:
        ada = [dominan[0]]
    return ";".join(ada) if ada else np.nan


def buat_dataset_sintetis(n_per_bidang: int = 200, seed: int = 0) -> pd.DataFrame:
    """Tiga bidang x `n_per_bidang` developer (default 600), ditambah 55 baris yang harus tersaring."""
    rng = np.random.default_rng(seed)
    baris = []
    for bidang, dominan in PROFIL.items():
        for _ in range(n_per_bidang):
            pengalaman = np.nan if rng.random() < 0.05 else float(rng.integers(0, 16))
            baris.append(
                {
                    "MainBranch": "I am a developer by profession",
                    "Employment": "Employed",
                    "DevType": bidang,
                    "WorkExp": pengalaman,
                    "LanguageHaveWorkedWith": _pilih(rng, dominan[0], SEMUA[0], wajib=True),
                    "DatabaseHaveWorkedWith": _pilih(rng, dominan[1], SEMUA[1]),
                    "PlatformHaveWorkedWith": _pilih(rng, dominan[2], SEMUA[2]),
                    "WebframeHaveWorkedWith": _pilih(rng, dominan[3], SEMUA[3]),
                }
            )
    df = pd.DataFrame(baris)
    # 55 baris tambahan yang harus tersaring (jumlah per bidang tetap di atas ambang 151):
    # bukan developer profesional, tanpa jenis pekerjaan, dan peran manajerial
    ekstra = df.iloc[:55].copy()
    ekstra.loc[ekstra.index[:25], "MainBranch"] = "I am learning to code"
    ekstra.loc[ekstra.index[25:40], "DevType"] = np.nan
    ekstra.loc[ekstra.index[40:55], "DevType"] = "Engineering manager"
    df = pd.concat([df, ekstra], ignore_index=True)
    df.insert(0, "ResponseId", range(1, len(df) + 1))
    return df
