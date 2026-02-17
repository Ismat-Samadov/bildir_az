#!/usr/bin/env python3
"""
bildir.az Business Intelligence — Chart Generator
Produces 10 business-focused charts from data/data.csv into charts/
"""

import csv
import os
import statistics
from collections import defaultdict

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.ticker as mticker

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
BASE_DIR   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CSV_PATH   = os.path.join(BASE_DIR, "data", "data.csv")
CHARTS_DIR = os.path.join(BASE_DIR, "charts")
os.makedirs(CHARTS_DIR, exist_ok=True)

# ---------------------------------------------------------------------------
# Style
# ---------------------------------------------------------------------------
BRAND_BLUE   = "#1A56DB"
BRAND_RED    = "#E02424"
BRAND_GREEN  = "#057A55"
BRAND_ORANGE = "#FF5A1F"
BRAND_GRAY   = "#6B7280"
BRAND_YELLOW = "#FACA15"
LIGHT_GRAY   = "#F3F4F6"

plt.rcParams.update({
    "font.family":   "DejaVu Sans",
    "font.size":     11,
    "axes.spines.top":    False,
    "axes.spines.right":  False,
    "axes.grid":          True,
    "grid.color":         "#E5E7EB",
    "grid.linewidth":     0.7,
    "figure.facecolor":   "white",
    "axes.facecolor":     "white",
})

# ---------------------------------------------------------------------------
# Load data
# ---------------------------------------------------------------------------
def load():
    rows = []
    with open(CSV_PATH, encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rows.append(r)
    return rows


def flt(v):
    try:
        return float(v) if v and v.strip() else None
    except ValueError:
        return None


def build_cat_stats(rows, min_companies=5):
    cats = defaultdict(list)
    for r in rows:
        c = r["category"] or "Digər"
        rating  = flt(r["overall_rating"])
        reviews = flt(r["total_reviews"])
        loyalty = flt(r["customer_loyalty_pct"])
        response = flt(r["response_rate_pct"])
        resolved = flt(r["resolved_complaints_pct"])
        cats[c].append({
            "rating":   rating,
            "reviews":  reviews or 0,
            "loyalty":  loyalty,
            "response": response,
            "resolved": resolved,
        })

    summary = []
    for c, items in cats.items():
        if len(items) < min_companies:
            continue
        with_rating = [i for i in items if i["rating"] is not None]
        if not with_rating:
            continue
        summary.append({
            "category":      c,
            "count":         len(items),
            "avg_rating":    round(statistics.mean(i["rating"] for i in with_rating), 2),
            "total_reviews": int(sum(i["reviews"] for i in items)),
            "avg_loyalty":   round(statistics.mean(i["loyalty"] for i in items if i["loyalty"] is not None), 1)
                             if any(i["loyalty"] is not None for i in items) else 0,
            "avg_response":  round(statistics.mean(i["response"] for i in items if i["response"] is not None), 1)
                             if any(i["response"] is not None for i in items) else 0,
            "avg_resolved":  round(statistics.mean(i["resolved"] for i in items if i["resolved"] is not None), 1)
                             if any(i["resolved"] is not None for i in items) else 0,
        })
    return summary


def save(name):
    path = os.path.join(CHARTS_DIR, name)
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"  Saved: {name}")


# ---------------------------------------------------------------------------
# Chart 1 — Company count by category (market landscape)
# ---------------------------------------------------------------------------
def chart_01_market_landscape(rows):
    cats = defaultdict(int)
    for r in rows:
        cats[r["category"] or "Digər"] += 1
    data = sorted(cats.items(), key=lambda x: x[1], reverse=True)[:15]
    labels  = [d[0] for d in data]
    values  = [d[1] for d in data]
    colors  = [BRAND_BLUE if v == max(values) else "#93C5FD" for v in values]

    fig, ax = plt.subplots(figsize=(12, 7))
    bars = ax.barh(labels[::-1], values[::-1], color=colors[::-1], height=0.65, edgecolor="white")
    for bar, val in zip(bars, values[::-1]):
        ax.text(val + 2, bar.get_y() + bar.get_height() / 2,
                str(val), va="center", fontsize=10, color="#374151")
    ax.set_xlabel("Number of Companies", labelpad=8)
    ax.set_title("Market Landscape — Number of Businesses by Sector", fontsize=14, fontweight="bold", pad=15)
    ax.set_xlim(0, max(values) * 1.15)
    fig.tight_layout()
    save("01_market_landscape.png")


# ---------------------------------------------------------------------------
# Chart 2 — Average rating by category (satisfaction benchmark)
# ---------------------------------------------------------------------------
def chart_02_avg_rating_by_category(summary):
    data = sorted(summary, key=lambda x: x["avg_rating"], reverse=True)[:15]
    labels = [d["category"] for d in data]
    values = [d["avg_rating"] for d in data]

    def color(v):
        if v >= 3.5: return BRAND_GREEN
        if v >= 2.5: return BRAND_YELLOW
        return BRAND_RED

    colors = [color(v) for v in values]
    fig, ax = plt.subplots(figsize=(12, 7))
    bars = ax.barh(labels[::-1], values[::-1], color=colors[::-1], height=0.65, edgecolor="white")
    for bar, val in zip(bars, values[::-1]):
        ax.text(val + 0.04, bar.get_y() + bar.get_height() / 2,
                f"{val:.1f}", va="center", fontsize=10)
    ax.axvline(x=2.5, color=BRAND_GRAY, linewidth=1.2, linestyle="--", label="Acceptable threshold (2.5)")
    ax.set_xlim(0, 5.4)
    ax.set_xlabel("Average Customer Rating (out of 5)", labelpad=8)
    ax.set_title("Customer Satisfaction by Sector — Average Rating", fontsize=14, fontweight="bold", pad=15)
    green_p = mpatches.Patch(color=BRAND_GREEN,  label="Strong (≥ 3.5)")
    yellow_p = mpatches.Patch(color=BRAND_YELLOW, label="Moderate (2.5–3.5)")
    red_p   = mpatches.Patch(color=BRAND_RED,    label="Critical (< 2.5)")
    ax.legend(handles=[green_p, yellow_p, red_p], loc="lower right", framealpha=0.9)
    fig.tight_layout()
    save("02_avg_rating_by_category.png")


# ---------------------------------------------------------------------------
# Chart 3 — Review volume by category (engagement & exposure)
# ---------------------------------------------------------------------------
def chart_03_review_volume(summary):
    data = sorted(summary, key=lambda x: x["total_reviews"], reverse=True)[:12]
    labels = [d["category"] for d in data]
    values = [d["total_reviews"] for d in data]

    fig, ax = plt.subplots(figsize=(12, 6))
    bars = ax.bar(range(len(labels)), values, color=BRAND_BLUE, width=0.6, edgecolor="white")
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 10,
                f"{val:,}", ha="center", va="bottom", fontsize=9, color="#374151")
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=35, ha="right", fontsize=10)
    ax.set_ylabel("Total Customer Reviews", labelpad=8)
    ax.set_title("Customer Engagement — Total Reviews per Sector", fontsize=14, fontweight="bold", pad=15)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
    fig.tight_layout()
    save("03_review_volume_by_category.png")


# ---------------------------------------------------------------------------
# Chart 4 — Response rate vs Resolution rate by category
# ---------------------------------------------------------------------------
def chart_04_response_vs_resolution(summary):
    data = sorted(summary, key=lambda x: -x["total_reviews"])[:12]
    labels   = [d["category"] for d in data]
    response = [d["avg_response"] for d in data]
    resolved = [d["avg_resolved"] for d in data]

    x = range(len(labels))
    w = 0.38
    fig, ax = plt.subplots(figsize=(14, 6))
    b1 = ax.bar([i - w/2 for i in x], response, width=w, label="Response Rate %", color=BRAND_BLUE,   edgecolor="white")
    b2 = ax.bar([i + w/2 for i in x], resolved, width=w, label="Resolution Rate %", color=BRAND_ORANGE, edgecolor="white")
    for bar in list(b1) + list(b2):
        h = bar.get_height()
        if h > 2:
            ax.text(bar.get_x() + bar.get_width() / 2, h + 0.8,
                    f"{h:.0f}%", ha="center", va="bottom", fontsize=8.5)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=35, ha="right", fontsize=10)
    ax.set_ylabel("Rate (%)", labelpad=8)
    ax.set_ylim(0, 115)
    ax.set_title("Customer Service Performance — Response vs. Resolution Rate by Sector",
                 fontsize=14, fontweight="bold", pad=15)
    ax.legend(loc="upper right", framealpha=0.9)
    fig.tight_layout()
    save("04_response_vs_resolution.png")


# ---------------------------------------------------------------------------
# Chart 5 — Customer loyalty (NPS proxy) by category — diverging bar
# ---------------------------------------------------------------------------
def chart_05_customer_loyalty(summary):
    data = sorted(summary, key=lambda x: x["avg_loyalty"], reverse=True)[:15]
    labels  = [d["category"] for d in data]
    values  = [d["avg_loyalty"] for d in data]
    colors  = [BRAND_GREEN if v >= 0 else BRAND_RED for v in values]

    fig, ax = plt.subplots(figsize=(12, 7))
    bars = ax.barh(labels[::-1], values[::-1], color=colors[::-1], height=0.65, edgecolor="white")
    for bar, val in zip(bars, values[::-1]):
        xpos = val + 0.5 if val >= 0 else val - 0.5
        ha   = "left"    if val >= 0 else "right"
        ax.text(xpos, bar.get_y() + bar.get_height() / 2,
                f"{val:+.1f}%", va="center", ha=ha, fontsize=9.5)
    ax.axvline(x=0, color="#374151", linewidth=1.0)
    ax.set_xlabel("Customer Loyalty Score (%)", labelpad=8)
    ax.set_title("Customer Loyalty by Sector — Net Promoter Indicator",
                 fontsize=14, fontweight="bold", pad=15)
    pos_p = mpatches.Patch(color=BRAND_GREEN, label="Net Promoters (positive)")
    neg_p = mpatches.Patch(color=BRAND_RED,   label="Net Detractors (negative)")
    ax.legend(handles=[pos_p, neg_p], loc="lower right", framealpha=0.9)
    fig.tight_layout()
    save("05_customer_loyalty.png")


# ---------------------------------------------------------------------------
# Chart 6 — Rating distribution buckets across all companies
# ---------------------------------------------------------------------------
def chart_06_rating_distribution(rows):
    buckets = {"No Rating": 0, "0–1": 0, "1–2": 0, "2–3": 0, "3–4": 0, "4–5": 0}
    for r in rows:
        v = flt(r["overall_rating"])
        if v is None:
            buckets["No Rating"] += 1
        elif v <= 1:
            buckets["0–1"] += 1
        elif v <= 2:
            buckets["1–2"] += 1
        elif v <= 3:
            buckets["2–3"] += 1
        elif v <= 4:
            buckets["3–4"] += 1
        else:
            buckets["4–5"] += 1

    labels = list(buckets.keys())
    values = list(buckets.values())
    clrs   = [BRAND_GRAY, BRAND_RED, BRAND_RED, BRAND_YELLOW, BRAND_GREEN, BRAND_GREEN]

    fig, ax = plt.subplots(figsize=(11, 5))
    bars = ax.bar(labels, values, color=clrs, width=0.6, edgecolor="white")
    total = sum(values)
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 3,
                f"{val}\n({100*val/total:.0f}%)", ha="center", va="bottom", fontsize=10)
    ax.set_ylabel("Number of Companies", labelpad=8)
    ax.set_title("Rating Distribution — How Trustworthy Is the Market?",
                 fontsize=14, fontweight="bold", pad=15)
    ax.set_ylim(0, max(values) * 1.2)
    fig.tight_layout()
    save("06_rating_distribution.png")


# ---------------------------------------------------------------------------
# Chart 7 — Top 15 most reviewed companies (highest public scrutiny)
# ---------------------------------------------------------------------------
def chart_07_most_reviewed(rows):
    rated = [
        (r["name"], flt(r["total_reviews"]) or 0, flt(r["overall_rating"]))
        for r in rows if flt(r["total_reviews"]) and flt(r["total_reviews"]) >= 10
    ]
    top = sorted(rated, key=lambda x: -x[1])[:15]
    labels = [t[0] for t in top]
    reviews = [t[1] for t in top]
    ratings  = [t[2] for t in top]

    def color(rt):
        if rt is None: return BRAND_GRAY
        if rt >= 3.5:  return BRAND_GREEN
        if rt >= 2.5:  return BRAND_YELLOW
        return BRAND_RED

    colors = [color(rt) for rt in ratings]
    fig, ax = plt.subplots(figsize=(12, 7))
    bars = ax.barh(labels[::-1], reviews[::-1], color=colors[::-1], height=0.65, edgecolor="white")
    for bar, val, rt in zip(bars, reviews[::-1], ratings[::-1]):
        lbl = f"{int(val):,}  ★{rt:.1f}" if rt else f"{int(val):,}"
        ax.text(val + 5, bar.get_y() + bar.get_height() / 2,
                lbl, va="center", fontsize=9.5)
    ax.set_xlabel("Total Reviews (Customer Feedback Volume)", labelpad=8)
    ax.set_title("Most Scrutinised Companies — Highest Review Counts",
                 fontsize=14, fontweight="bold", pad=15)
    green_p  = mpatches.Patch(color=BRAND_GREEN,  label="Well-rated (≥ 3.5)")
    yellow_p = mpatches.Patch(color=BRAND_YELLOW, label="Moderate (2.5–3.5)")
    red_p    = mpatches.Patch(color=BRAND_RED,    label="Poorly-rated (< 2.5)")
    ax.legend(handles=[green_p, yellow_p, red_p], loc="lower right", framealpha=0.9)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
    fig.tight_layout()
    save("07_most_reviewed_companies.png")


# ---------------------------------------------------------------------------
# Chart 8 — Top 10 trusted vs bottom 10 worst-rated (min 10 reviews)
# ---------------------------------------------------------------------------
def chart_08_best_vs_worst(rows):
    rated = [
        (r["name"], flt(r["overall_rating"]), flt(r["total_reviews"]))
        for r in rows
        if flt(r["overall_rating"]) and flt(r["total_reviews"]) and flt(r["total_reviews"]) >= 10
    ]
    best  = sorted(rated, key=lambda x: -x[1])[:10]
    worst = sorted(rated, key=lambda x:  x[1])[:10]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

    # Best
    labels_b = [f"{b[0]}" for b in best]
    vals_b   = [b[1] for b in best]
    ax1.barh(labels_b[::-1], vals_b[::-1], color=BRAND_GREEN, height=0.65, edgecolor="white")
    for i, (val, name) in enumerate(zip(vals_b[::-1], labels_b[::-1])):
        ax1.text(val + 0.04, i, f"{val:.1f}", va="center", fontsize=10)
    ax1.set_xlim(0, 5.6)
    ax1.set_xlabel("Rating (out of 5)", labelpad=8)
    ax1.set_title("Top 10 Most Trusted Companies", fontsize=13, fontweight="bold", pad=12)
    ax1.axvline(x=4.0, color=BRAND_GRAY, linewidth=1, linestyle="--")

    # Worst
    labels_w = [f"{w[0]}" for w in worst]
    vals_w   = [w[1] for w in worst]
    ax2.barh(labels_w[::-1], vals_w[::-1], color=BRAND_RED, height=0.65, edgecolor="white")
    for i, (val, name) in enumerate(zip(vals_w[::-1], labels_w[::-1])):
        ax2.text(val + 0.04, i, f"{val:.1f}", va="center", fontsize=10)
    ax2.set_xlim(0, 5.6)
    ax2.set_xlabel("Rating (out of 5)", labelpad=8)
    ax2.set_title("Bottom 10 Lowest-Rated Companies", fontsize=13, fontweight="bold", pad=12)
    ax2.axvline(x=2.5, color=BRAND_GRAY, linewidth=1, linestyle="--", label="Acceptable (2.5)")

    fig.suptitle("Company Reputation Extremes — Trusted vs. At-Risk Brands",
                 fontsize=15, fontweight="bold", y=1.01)
    fig.tight_layout()
    save("08_best_vs_worst_companies.png")


# ---------------------------------------------------------------------------
# Chart 9 — Social media presence by category
# ---------------------------------------------------------------------------
def chart_09_social_presence(rows):
    cats_all      = defaultdict(int)
    cats_facebook = defaultdict(int)
    cats_instagram = defaultdict(int)
    cats_linkedin = defaultdict(int)

    for r in rows:
        c = r["category"] or "Digər"
        cats_all[c] += 1
        if r["facebook"] and "bildir" not in r["facebook"]:
            cats_facebook[c] += 1
        if r["instagram"] and "bildir" not in r["instagram"]:
            cats_instagram[c] += 1
        if r["linkedin"] and "bildir" not in r["linkedin"]:
            cats_linkedin[c] += 1

    # Top 12 categories by company count
    top_cats = [c for c, _ in sorted(cats_all.items(), key=lambda x: -x[1])[:12]]

    fb_pct = [100 * cats_facebook[c]  / cats_all[c] for c in top_cats]
    ig_pct = [100 * cats_instagram[c] / cats_all[c] for c in top_cats]
    li_pct = [100 * cats_linkedin[c]  / cats_all[c] for c in top_cats]

    x = range(len(top_cats))
    w = 0.26
    fig, ax = plt.subplots(figsize=(15, 6))
    ax.bar([i - w for i in x],     fb_pct, width=w, label="Facebook",  color="#1877F2", edgecolor="white")
    ax.bar([i      for i in x],     ig_pct, width=w, label="Instagram", color="#E1306C", edgecolor="white")
    ax.bar([i + w  for i in x],     li_pct, width=w, label="LinkedIn",  color="#0A66C2", edgecolor="white")
    ax.set_xticks(x)
    ax.set_xticklabels(top_cats, rotation=35, ha="right", fontsize=10)
    ax.set_ylabel("% of Companies with Profile", labelpad=8)
    ax.set_ylim(0, 115)
    ax.set_title("Digital Presence — Social Media Adoption by Sector",
                 fontsize=14, fontweight="bold", pad=15)
    ax.legend(loc="upper right", framealpha=0.9)
    fig.tight_layout()
    save("09_social_media_presence.png")


# ---------------------------------------------------------------------------
# Chart 10 — Star breakdown for 6 key categories (stacked bar)
# ---------------------------------------------------------------------------
def chart_10_star_breakdown(rows):
    target_cats = [
        "Kargo şirkətləri", "İnternet və İT xidmətləri",
        "Banklar", "Yemək çatdırılması",
        "Supermarketlər", "Maliyyə"
    ]
    cat_stars = {c: {"5": [], "4": [], "3": [], "2": [], "1": []} for c in target_cats}

    for r in rows:
        c = r["category"]
        if c not in target_cats:
            continue
        for s in ["5", "4", "3", "2", "1"]:
            v = flt(r[f"star{s}_pct"])
            if v is not None:
                cat_stars[c][s].append(v)

    avgs = {}
    for c in target_cats:
        avgs[c] = {s: round(statistics.mean(cat_stars[c][s]), 1)
                   if cat_stars[c][s] else 0.0 for s in ["5", "4", "3", "2", "1"]}

    labels = target_cats
    s5 = [avgs[c]["5"] for c in labels]
    s4 = [avgs[c]["4"] for c in labels]
    s3 = [avgs[c]["3"] for c in labels]
    s2 = [avgs[c]["2"] for c in labels]
    s1 = [avgs[c]["1"] for c in labels]

    x = range(len(labels))
    fig, ax = plt.subplots(figsize=(13, 6))
    ax.bar(x, s5, label="5★ Promoters",  color="#057A55", edgecolor="white")
    ax.bar(x, s4, bottom=s5, label="4★",  color="#31C48D", edgecolor="white")
    ax.bar(x, s3, bottom=[a+b for a,b in zip(s5,s4)], label="3★ Neutral", color=BRAND_YELLOW, edgecolor="white")
    b234 = [a+b+c for a,b,c in zip(s5,s4,s3)]
    ax.bar(x, s2, bottom=b234, label="2★",  color="#F98080", edgecolor="white")
    b2345 = [a+b for a,b in zip(b234,s2)]
    ax.bar(x, s1, bottom=b2345, label="1★ Detractors", color=BRAND_RED, edgecolor="white")

    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=20, ha="right", fontsize=10)
    ax.set_ylabel("Average % of Reviews", labelpad=8)
    ax.set_title("Review Sentiment Breakdown — Star Rating Mix by Key Sector",
                 fontsize=14, fontweight="bold", pad=15)
    ax.legend(loc="upper right", ncol=5, framealpha=0.9, fontsize=9)
    fig.tight_layout()
    save("10_star_breakdown_by_category.png")


# ---------------------------------------------------------------------------
# Run all
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("Loading data …")
    rows = load()
    print(f"  {len(rows)} companies loaded.")

    summary = build_cat_stats(rows, min_companies=5)
    print(f"  {len(summary)} categories with ≥5 companies.\n")

    print("Generating charts …")
    chart_01_market_landscape(rows)
    chart_02_avg_rating_by_category(summary)
    chart_03_review_volume(summary)
    chart_04_response_vs_resolution(summary)
    chart_05_customer_loyalty(summary)
    chart_06_rating_distribution(rows)
    chart_07_most_reviewed(rows)
    chart_08_best_vs_worst(rows)
    chart_09_social_presence(rows)
    chart_10_star_breakdown(rows)

    print(f"\nAll charts saved to: {CHARTS_DIR}")
