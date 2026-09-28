# CSE 511: Data Processing at Scale (Fall 2025, Session B)

This repository contains my coursework and assignment solutions for **CSE 511 – Data Processing at Scale**. Each folder is a separate assignment or project covering a different area of large-scale data processing: relational data fragmentation, query processing, NoSQL databases, distributed spatial analysis, and recommendation systems.

## Repository Structure

```
.
├── CSE512-Hotspot-Analysis-Template/   # Spatial hotspot analysis (Apache Spark)
├── Fragmentation/                      # Data fragmentation assignment
├── Interface_qpa/                      # Query processing assignment
├── Movie Recommendation/               # Movie recommendation project
├── NoSQL/                              # NoSQL database assignment
├── ml-10M100K/                         # MovieLens 10M dataset (large file not tracked)
├── CSE 511_Data Fragmentation Assignment_Overview.*
├── CSE 511_Query Processing Assignment_Overview.*
├── .gitignore
└── README.md
```

## Contents

| Folder | Description |
| --- | --- |
| `Fragmentation/` | Loads the MovieLens ratings data into a relational database and partitions it using horizontal fragmentation (e.g., range and round-robin partitioning). |
| `Interface_qpa/` | Query processing assignment: implements query functions that run over the fragmented data. |
| `NoSQL/` | Assignment on modeling and querying data with a NoSQL database. |
| `Movie Recommendation/` | Recommendation system built on the MovieLens data. |
| `CSE512-Hotspot-Analysis-Template/` | Geospatial hotspot analysis over large datasets using Apache Spark. |
| `ml-10M100K/` | The MovieLens 10M dataset used by several assignments. |

The two overview documents in the root folder describe the requirements for the Data Fragmentation and Query Processing assignments.

## Dataset

Several assignments use the [MovieLens 10M dataset](https://grouplens.org/datasets/movielens/10m/) (`ml-10M100K`).

> **Note:** `ml-10M100K/ratings.dat` is about 253 MB, which exceeds GitHub's 100 MB file size limit, so it is **not included** in this repository (it is listed in `.gitignore`).

To run the code locally:

1. Download the dataset from the link above.
2. Extract it so the folder is named `ml-10M100K/`.
3. Make sure `ratings.dat` sits at `ml-10M100K/ratings.dat`.

## Prerequisites

Depending on the assignment, you will need some of the following:

- Python 3.x
- PostgreSQL (with `psycopg2`)
- Apache Spark / PySpark
- A NoSQL database (see the `NoSQL/` folder for details)
- Git and, if you ever need to track large files, [Git LFS](https://git-lfs.github.com/)

Check the files inside each folder for assignment-specific setup and run instructions.

## Getting Started

```bash
# Clone the repository
git clone https://github.com/sejalpatil-29/CSE-511_Data-Processing-at-Scale-2025-Fall-B-.git
cd CSE-511_Data-Processing-at-Scale-2025-Fall-B-

# Download the MovieLens 10M dataset into ml-10M100K/ (see Dataset section)
```

Then open the folder for the assignment you want to run and follow its instructions.

## Author

**Sejal Patil**
GitHub: [@sejalpatil-29](https://github.com/sejalpatil-29)

## Academic Integrity

This repository is for personal reference. If you are currently taking this course, please follow your institution's academic integrity policy and do not copy this work.
