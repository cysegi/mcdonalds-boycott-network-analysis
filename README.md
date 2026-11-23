# #BoycottMcDonalds on X: Social Network Analysis

Who drove, bridged and received attention in the #BoycottMcDonalds conversation on X (Twitter)? This project analyzes a NodeXL Pro interaction network of 1,467 accounts and 2,205 interactions, then recomputes the NodeXL metrics in Python with NetworkX so the results are reproducible outside Excel.

Course assignment for ABM503D Web and Social Media Analytics, Universiti Sains Malaysia (Semester 1, 2025/2026). Group SocialCheck: Chew Yoong Chang and Felicia Yeow Kar Mun.

## Questions

1. Which accounts have the highest degree, betweenness, closeness and eigenvector centrality, and what does each measure mean here?
2. How fragmented is the network?
3. Who is the top organic influencer once the brand account is set aside?

## Data

- NodeXL Pro search network for #BoycottMcDonalds. The workbook appears to have been provided as course material ("Group 1" dataset).
- Interactions dated 2023-10-21 to 2024-11-01.
- Edge types: replies (722), quotes (443), tweets/self-loops (351), mentions in replies (329), mentions (211), mentions in quotes (134), mentions in quote replies (15).
- The workbook is not committed because it contains account handles and tweet text. See `data/README.md`.

## Method

- In the course, the analysis was done in NodeXL (Excel): graph metrics, Clauset-Newman-Moore clustering, and network visualizations.
- After the course, `src/network_metrics.py` was added. It rebuilds the same graph with NetworkX and recomputes:
  - overall metrics
  - in- and out-degree, both raw and unique
  - betweenness, on the NodeXL scale
  - closeness
  - eigenvector centrality
  - modularity groups

## Results

Overall network (Python recomputation):

| Metric | Value |
|---|---:|
| Vertices | 1,468 |
| Total / unique edges | 2,205 / 1,845 |
| Self-loops (standalone tweets) | 375 |
| Connected components | 249 (145 isolates) |
| Largest component | 1,029 vertices |
| Max / average geodesic distance (largest component) | 14 / 4.65 |
| Directed density | 0.00086 |

Centrality:

- Betweenness. @mcdonalds is the dominant bridge (766,126.7), followed by @guardiannews (249,865.5). The next three are individual accounts (about 92,000 to 106,000). These values match the NodeXL output exactly.
- In-degree. Most attention goes to @mcdonalds (381 incoming interactions) and @guardiannews (110 to 111).
- Out-degree. One individual account initiated the most interactions: 47 unique targets, or 112 including repeats. A small set of users drives most of the activity.
- Eigenvector. @mcdonalds scores 0.051, about seven times the next account (0.007). Influence is concentrated in one core.

Top organic influencer:

- The brand account is excluded because it attracts mentions by default.
- @guardiannews has the highest remaining betweenness. It is the main bridge between news coverage and the many small discussion clusters.

## Corrections to the submitted report

The Python rebuild surfaced several issues in the course report:

- The report's data range text says 1 January to 31 December 2023. The edges in the workbook span October 2023 to November 2024.
- The report gives two different sets of counts: 222 vs. 248 components, 117 vs. 144 isolates, and 1,467 vs. 1,442 vertices. The workbook supports about 248 components, 144 isolates and 1,467 vertices. The Python count differs by one because of name normalization.
- The report lists closeness values of 1.0 as the most central accounts. In NodeXL, closeness is computed within each component, so two-account islands score 1.0. Using closeness on the whole graph (Wasserman-Faust), @mcdonalds ranks first (0.274).
- The report's modularity (0.625, 126 groups) comes from NodeXL's grouping settings. NetworkX's CNM on the whole graph, including isolates, gives 270 groups and a modularity of 0.781. These numbers are not directly comparable.

## Limitations

- A keyword search network covers only users who used or were linked to the hashtag. It is not representative of all X users.
- The analysis measures structure only. No sentiment or stance classification was done.

## Run

```bash
pip install -r requirements.txt
python src/network_metrics.py data/mcdonald_nodexl.xlsx --top 5
```

Outputs are written to `results/`. The account-level table `centrality_by_account.csv` is git-ignored.

## Credits

- Joint work with Felicia Yeow Kar Mun.
- Course: ABM503D, Prof. Dr. Nor Hasliza Md Saad, Universiti Sains Malaysia.
- Tools: NodeXL Pro (Social Media Research Foundation) and NetworkX.
