# Adapted from the supplied synthetic-data notebook. All records and prices are simulated.
import argparse
parser=argparse.ArgumentParser(description="Generate synthetic hospital inventory tables for a coursework chatbot.")
parser.add_argument('--drugs',type=int,default=8000)
parser.add_argument('--locations',type=int,default=80)
parser.add_argument('--lots',type=int,default=200000)
parser.add_argument('--seed',type=int,default=42)
parser.add_argument('--as-of',default='2026-11-14',help='Simulation reference date in YYYY-MM-DD format')
parser.add_argument('--output',default='data/generated')
args=parser.parse_args()
if min(args.drugs,args.locations,args.lots)<1:parser.error('Row counts must be positive.')

import pandas as pd
import numpy as np
import random
from datetime import datetime, timedelta
from pathlib import Path
import hashlib

# -----------------------------
# CONFIG
# -----------------------------
NUM_DRUGS = args.drugs
NUM_LOCATIONS = args.locations
NUM_LOTS = args.lots
OUT_DIR = Path(args.output)
OUT_DIR.mkdir(parents=True, exist_ok=True)

random.seed(args.seed)
np.random.seed(args.seed)

# -----------------------------
# "Orange Book-friendly" ingredient list
# - Large, common U.S. Rx ingredients (biased toward OB-covered products)
# - Not exhaustive, but intentionally broad for your project prompts
# -----------------------------
INGREDIENTS = [
    # Pain / fever / inflammation
    "acetaminophen","ibuprofen","naproxen","diclofenac","ketorolac","meloxicam","celecoxib",
    "tramadol","codeine","hydrocodone","oxycodone","morphine","hydromorphone","fentanyl",
    "gabapentin","pregabalin","cyclobenzaprine","baclofen","tizanidine",

    # Antibiotics
    "amoxicillin","amoxicillin-clavulanate","penicillin v","dicloxacillin",
    "cephalexin","cefuroxime","cefdinir","ceftriaxone","cefazolin","cefepime","ceftazidime",
    "azithromycin","clarithromycin","doxycycline","minocycline",
    "ciprofloxacin","levofloxacin","moxifloxacin",
    "clindamycin","metronidazole","trimethoprim-sulfamethoxazole",
    "linezolid","vancomycin","daptomycin",
    "meropenem","ertapenem","piperacillin-tazobactam",

    # Cardio / HTN / lipids
    "lisinopril","enalapril","ramipril","losartan","valsartan","olmesartan",
    "amlodipine","diltiazem","verapamil","nifedipine",
    "metoprolol","atenolol","carvedilol","propranolol",
    "hydrochlorothiazide","chlorthalidone","furosemide","spironolactone",
    "atorvastatin","rosuvastatin","simvastatin","pravastatin",
    "clopidogrel","aspirin","nitroglycerin",

    # Anticoag / antiplatelet
    "warfarin","heparin","enoxaparin","apixaban","rivaroxaban","dabigatran",

    # Diabetes / endocrine
    "metformin","glipizide","glyburide","sitagliptin","empagliflozin",
    "insulin regular","insulin aspart","insulin lispro","insulin glargine","insulin detemir",
    "levothyroxine","methimazole",

    # GI
    "omeprazole","pantoprazole","esomeprazole","lansoprazole",
    "famotidine","cimetidine",
    "ondansetron","metoclopramide","promethazine",
    "loperamide","docusate","senna","polyethylene glycol",

    # Respiratory / allergy
    "albuterol","levalbuterol","ipratropium","tiotropium",
    "budesonide","fluticasone","mometasone",
    "montelukast","cetirizine","loratadine","fexofenadine",

    # Neuro / psych
    "sertraline","fluoxetine","escitalopram","citalopram","venlafaxine","duloxetine","bupropion",
    "alprazolam","lorazepam","diazepam","clonazepam",
    "quetiapine","olanzapine","risperidone","haloperidol",
    "lamotrigine","levetiracetam","valproic acid","carbamazepine",
    "sumatriptan",

    # Infectious disease antivirals
    "acyclovir","valacyclovir","oseltamivir",

    # Steroids / immunology
    "prednisone","methylprednisolone","dexamethasone","hydrocortisone",

    # Eye / derm / misc
    "timolol","latanoprost",
    "mupirocin","triamcinolone","hydrocortisone topical",
    "tamsulosin","finasteride","sildenafil",

    # Emergency / critical care
    "epinephrine","norepinephrine","phenylephrine","dopamine","dobutamine",
    "naloxone","atropine","adenosine","amiodarone","lidocaine injection",
    "magnesium sulfate","potassium chloride","calcium gluconate",
]

# Remove duplicates while keeping order
seen = set()
INGREDIENTS = [x for x in INGREDIENTS if not (x in seen or seen.add(x))]

DOSE_FORMS = ["tablet","capsule","oral solution","injection","IV bag","cream","ointment","patch","inhaler"]
ROUTES = ["oral","IV","IM","subcutaneous","topical","inhalation","sublingual"]

# Typical strengths (roughly realistic, but generic)
STRENGTHS_MG = [2.5,5,10,12.5,20,25,40,50,75,80,100,150,200,250,300,400,500,600,800,1000]
STRENGTHS_MCG = [25,50,75,100,125,200,250,400,500]
STRENGTHS_G = [1,2,3,4]

def pick_strength(ingredient: str):
    # Heuristic: insulin and some injectables better as units/mL etc, but we keep it simple for CSV
    if "insulin" in ingredient:
        return f"{random.choice([100,200,300])} units/mL"
    if ingredient in ["levothyroxine"]:
        return f"{random.choice(STRENGTHS_MCG)} mcg"
    if "topical" in ingredient:
        return f"{random.choice([0.5,1,2.5])}%"
    if random.random() < 0.15:
        return f"{random.choice(STRENGTHS_G)} g"
    return f"{random.choice(STRENGTHS_MG)} mg"

def pick_form_route(ingredient: str):
    # Simple biasing so the dataset looks like real hospital distribution
    if "topical" in ingredient or ingredient in ["mupirocin","triamcinolone"]:
        return random.choice(["cream","ointment"]), "topical"
    if ingredient in ["albuterol","levalbuterol","ipratropium","tiotropium","budesonide","fluticasone","mometasone"]:
        return random.choice(["inhaler"]), "inhalation"
    if ingredient in ["nitroglycerin"]:
        return random.choice(["tablet","patch"]), random.choice(["sublingual","topical"])
    if ingredient in ["ceftriaxone","cefazolin","vancomycin","meropenem","ertapenem","piperacillin-tazobactam",
                      "norepinephrine","epinephrine","amiodarone","adenosine","dopamine","dobutamine"]:
        return random.choice(["injection","IV bag"]), random.choice(["IV","IM"])
    # default outpatient-friendly (Orange Book heavy)
    form = random.choice(["tablet","capsule","oral solution"])
    route = "oral"
    return form, route

# Some plausible brand tokens (not exhaustive, just to create brand vs generic variance)
BRAND_TOKENS = [
    "XR","ER","SR","XL","ODT","HCT","DM","Plus","Max","PM","EC","LA","CR"
]

def make_brand(ingredient: str):
    # Not real brand names—just realistic “brand-like” labels for simulation
    base = ingredient.split()[0].capitalize()
    if random.random() < 0.6:
        return ""
    token = random.choice(BRAND_TOKENS)
    return f"{base}-{token}"

def ob_group_key(ingredient, strength, dose_form, route):
    # Canonical key for "same active ingredient + strength + form + route"
    # (rough proxy for how OB substitution works in many cases)
    raw = f"{ingredient}|{strength}|{dose_form}|{route}".lower().strip()
    return hashlib.sha1(raw.encode("utf-8")).hexdigest()[:16]

# -----------------------------
# DRUG MASTER
# -----------------------------
drug_rows = []
for i in range(NUM_DRUGS):
    ing = random.choice(INGREDIENTS)
    form, route = pick_form_route(ing)
    strength = pick_strength(ing)

    brand = make_brand(ing)

    refrigerated_flag = (("insulin" in ing) or (random.random() < 0.12))
    controlled_flag = ing in ["fentanyl","morphine","hydromorphone","oxycodone","hydrocodone","alprazolam","lorazepam","diazepam","clonazepam"]

    drug_rows.append({
        "drug_id": f"D{i:05d}",
        "generic_name": ing,
        "brand_name": brand,  # blank means generic packaging
        "strength": strength,
        "dose_form": form,
        "route": route,
        "controlled_flag": bool(controlled_flag),
        "refrigerated_flag": bool(refrigerated_flag),
        "ob_group_key": ob_group_key(ing, strength, form, route)
    })

drug_master = pd.DataFrame(drug_rows)

# Reduce duplicates a bit (optional): keep unique combos if you want “more variety”
drug_master = drug_master.drop_duplicates(subset=["generic_name","brand_name","strength","dose_form","route"]).reset_index(drop=True)

# If dedup shrank rows below NUM_DRUGS, top back up by resampling
while len(drug_master) < NUM_DRUGS:
    ing = random.choice(INGREDIENTS)
    form, route = pick_form_route(ing)
    strength = pick_strength(ing)
    brand = make_brand(ing)
    refrigerated_flag = (("insulin" in ing) or (random.random() < 0.12))
    controlled_flag = ing in ["fentanyl","morphine","hydromorphone","oxycodone","hydrocodone","alprazolam","lorazepam","diazepam","clonazepam"]
    new_row = {
        "drug_id": f"D{len(drug_master):05d}",
        "generic_name": ing,
        "brand_name": brand,
        "strength": strength,
        "dose_form": form,
        "route": route,
        "controlled_flag": bool(controlled_flag),
        "refrigerated_flag": bool(refrigerated_flag),
        "ob_group_key": ob_group_key(ing, strength, form, route)
    }
    drug_master = pd.concat([drug_master, pd.DataFrame([new_row])], ignore_index=True)
# ✅ Ensure drug_id is unique (prevents ambiguous Series error)
drug_master = drug_master.reset_index(drop=True)
drug_master["drug_id"] = [f"D{i:05d}" for i in range(len(drug_master))]


drug_master.to_csv(OUT_DIR / "drug_master.csv", index=False)

# -----------------------------
# LOCATIONS
# -----------------------------
areas = ["Main Pharmacy", "Satellite Pharmacy", "OR Pyxis", "ICU Pyxis", "ED Pyxis", "Oncology Vault", "Peds Pyxis"]
facilities = ["Hospital A","Hospital B","Hospital C"]

locations = []
for i in range(NUM_LOCATIONS):
    area = random.choice(areas)
    # More refrigerated capacity in main/satellite, less in cabinets
    if area in ["Main Pharmacy","Satellite Pharmacy","Oncology Vault"]:
        tz = random.choices(["room","refrigerated"], weights=[65,35])[0]
    else:
        tz = random.choices(["room","refrigerated"], weights=[85,15])[0]
    locations.append({
        "location_id": f"L{i:03d}",
        "facility": random.choice(facilities),
        "area": area,
        "temperature_zone": tz,
        "access_level": random.choice(["pharmacy","clinical","restricted"])
    })

locations_df = pd.DataFrame(locations)
locations_df.to_csv(OUT_DIR / "locations.csv", index=False)

# -----------------------------
# COST / CONTRACTS
# -----------------------------
vendors = ["McKesson", "Cardinal", "AmerisourceBergen", "Local 340B", "Specialty Vendor"]
today = datetime.fromisoformat(args.as_of)

contracts = []
for _, row in drug_master.iterrows():
    base = random.uniform(0.2, 300.0)

    # Bias: injectables + controlled + specialty -> higher cost
    if row["dose_form"] in ["injection","IV bag"]:
        base *= random.uniform(1.3, 2.8)
    if row["controlled_flag"]:
        base *= random.uniform(1.2, 2.2)
    if row["generic_name"] in ["insulin glargine","insulin lispro","insulin aspart"]:
        base *= random.uniform(1.5, 3.5)

    start = (today - timedelta(days=random.randint(30, 365))).date().isoformat()
    end = (today + timedelta(days=random.randint(180, 900))).date().isoformat()

    contracts.append({
        "drug_id": row["drug_id"],
        "unit_cost": round(base, 2),
        "vendor": random.choice(vendors),
        "contract_start": start,
        "contract_end": end,
        "gpo_flag": bool(random.random() < 0.6),
    })

contracts_df = pd.DataFrame(contracts)
contracts_df.to_csv(OUT_DIR / "cost_contracts.csv", index=False)

# -----------------------------
# INVENTORY LOTS (≈200k)
# -----------------------------
statuses = ["available", "low", "out", "expired", "recalled", "quarantined"]

def pick_location_for_drug(drug_row):
    # Refrigerated drugs should more often land in refrigerated locations
    if drug_row["refrigerated_flag"]:
        refrigerated_locs = locations_df[locations_df["temperature_zone"] == "refrigerated"]["location_id"].values
        if len(refrigerated_locs) > 0 and random.random() < 0.75:
            return random.choice(refrigerated_locs)
    return random.choice(locations_df["location_id"].values)

lots = []
drug_ids = drug_master["drug_id"].values
drug_lookup = drug_master.set_index("drug_id")

for i in range(NUM_LOTS):
    did = random.choice(drug_ids)
    drow = drug_lookup.loc[did]

    # Expiration: injectables often shorter shelf-life; tablets longer
    if drow["dose_form"] in ["injection","IV bag"]:
        exp_days = random.randint(-60, 365)
    else:
        exp_days = random.randint(-120, 900)

    exp = today + timedelta(days=exp_days)
    if exp < today:
        status = "expired"
    else:
        # more realistic distribution
        status = random.choices(
            ["available","low","out","recalled","quarantined"],
            weights=[78,10,4,4,4]
        )[0]

    # Quantities: cabinets lower than main pharmacy
    loc = pick_location_for_drug(drow)
    area = locations_df.loc[locations_df["location_id"] == loc, "area"].values[0]
    if area in ["OR Pyxis","ICU Pyxis","ED Pyxis","Peds Pyxis"]:
        on_hand = random.randint(0, 120)
        par = random.randint(20, 120)
    else:
        on_hand = random.randint(0, 600)
        par = random.randint(80, 400)

    reorder = max(5, int(par * random.uniform(0.25, 0.6)))

    lots.append({
        "inventory_id": f"LOT{i:07d}",
        "drug_id": did,
        "location_id": loc,
        "lot_number": f"LN{random.randint(100000,999999)}",
        "expiration_date": exp.date().isoformat(),
        "on_hand_qty": int(on_hand),
        "unit": random.choice(["tablet","capsule","vial","mL","bag"]),
        "par_level": int(par),
        "reorder_point": int(reorder),
        "status": status,
        "last_updated": today.isoformat()
    })

inventory_df = pd.DataFrame(lots)
inventory_df.to_csv(OUT_DIR / "inventory_lots.csv", index=False)

print("✅ Dataset generated in folder:", OUT_DIR.resolve())
print("Row counts:")
print(" - drug_master:", len(drug_master))
print(" - locations:", len(locations_df))
print(" - cost_contracts:", len(contracts_df))
print(" - inventory_lots:", len(inventory_df))

print("\nFiles created:")
for f in OUT_DIR.iterdir():
    print(" -", f.name)
