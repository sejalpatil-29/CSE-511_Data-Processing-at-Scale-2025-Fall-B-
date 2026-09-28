# CSE 511: Hot Spot Analysis — NYC Taxi Data (Apache Spark + Scala)

Spatio-temporal hot spot analysis on NYC yellow-taxi pickup data using Apache Spark SQL and Scala. Two independent analyses:

1. **Hot Zone Analysis** — a spatial range join that counts taxi pickups inside a set of rectangular zones.
2. **Hot Cell Analysis** — the Getis-Ord G* statistic over a space-time grid, to find statistically significant pickup hot spots (the ACM SIGSPATIAL GISCUP 2016 problem).

This README is the complete reference for building, running, and understanding this project.

---

## Tech stack & exact versions

| Component | Version |
|---|---|
| Java | 17 (Amazon Corretto 17) |
| Scala | 2.12.17 |
| Apache Spark | 3.4.1 (Spark SQL, Hadoop 3 build) |
| sbt | 1.9.4 (pinned in `project/build.properties`) |
| sbt-assembly | 0.14.5 |
| Hadoop winutils | 3.3.5 (Windows-only helper binaries) |

These exact versions matter — Spark's Scala binary version must match the jar's Scala version, and the grading environment expects this specific combination.

---

## Project layout

```
CSE512-Hotspot-Analysis-Template/
├── build.sbt                          # sbt build config — Scala/Spark versions, jar name
├── project/
│   ├── build.properties               # pins sbt.version=1.9.4
│   └── plugins.sbt                    # sbt-assembly plugin
├── src/
│   ├── main/scala/cse512/
│   │   ├── Entrance.scala             # CLI entry point, task dispatch, Spark session setup
│   │   ├── HotzoneAnalysis.scala      # range join + aggregation logic
│   │   ├── HotzoneUtils.scala         # ST_Contains (point-in-rectangle test)
│   │   ├── HotcellAnalysis.scala      # grid construction, neighbourhood join, G* ranking
│   │   └── HotcellUtils.scala         # coordinate mapping, neighbour counts, G* formula
│   └── resources/
│       ├── point_hotzone.csv          # sample points for hot zone testing
│       ├── zone-hotzone.csv           # rectangle definitions for hot zone testing
│       └── yellow_trip_sample_100000.csv  # NYC taxi sample (not committed — see .gitignore)
├── testcase/
│   ├── hotzone/                       # reference input/output for hot zone
│   └── hotcell/                       # reference input/output for hot cell
├── target/scala-2.12/                 # build output (jar lands here — not committed)
└── README.md                          # this file
```

---

## How the analyses work

### Hot Zone Analysis
- `ST_Contains(rectangle, point)` is registered as a Spark SQL UDF. It normalizes the two rectangle corner coordinates into min/max bounds, then does an inclusive bounds check on the point.
- Rectangles are joined to points via `ST_Contains`, grouped by rectangle, counted, and sorted alphabetically by the rectangle string.
- Output is written as a single CSV via `.coalesce(1)`.

### Hot Cell Analysis
1. Each pickup is mapped to a grid cell `(x, y, z)`: `x`/`y` are longitude/latitude floored to 0.01° steps, `z` is the day of month (1–31).
2. Pickups outside the study bounds (lon −74.50 to −73.70, lat 40.50 to 40.90, day 1–31) are filtered out.
3. Pickups are aggregated to a pickup count per cell.
4. Each cell's 3×3×3 neighbourhood (27 cells) is found via a self-join with `BETWEEN` conditions. Neighbour counts are summed; the neighbour count `w` is reduced for cells on the grid boundary (27, 18, or 12 valid neighbours).
5. Mean and standard deviation are computed over **all** cells in the grid, including empty ones.
6. The Getis-Ord G* statistic is computed per cell:

   ```
   G*_i = (Σx_j − X̄·w_i) / (S · sqrt((n·w_i − w_i²) / (n−1)))
   ```

   where `x_j` are neighbourhood pickup counts, `w_i` is the neighbour count, `n` is total grid cells.
7. The top 50 cells by G* score are output (score itself is **not** included in the output, per assignment spec).

---

## How to build

```
cd path\to\CSE512-Hotspot-Analysis-Template
sbt clean assembly
```

- First run downloads the Scala compiler and all dependencies — takes several minutes.
- Ends with `[success]` when it works.
- The jar lands at:
  ```
  target\scala-2.12\CSE512-Hotspot-Analysis-Template-assembly-0.1.0.jar
  ```

---

## How to run

### Hot zone only
```
spark-submit target\scala-2.12\CSE512-Hotspot-Analysis-Template-assembly-0.1.0.jar out hotzoneanalysis src\resources\point_hotzone.csv src\resources\zone-hotzone.csv
```
→ Output: `out0\part-*.csv`

### Hot cell only
```
spark-submit target\scala-2.12\CSE512-Hotspot-Analysis-Template-assembly-0.1.0.jar out hotcellanalysis src\resources\yellow_trip_sample_100000.csv
```
→ Output: `out0\part-*.csv`

### Both together (mirrors how the assignment's grader runs it)
```
spark-submit target\scala-2.12\CSE512-Hotspot-Analysis-Template-assembly-0.1.0.jar out hotzoneanalysis src\resources\point_hotzone.csv src\resources\zone-hotzone.csv hotcellanalysis src\resources\yellow_trip_sample_100000.csv
```
→ Hot zone output: `out0\part-*.csv`
→ Hot cell output: `out1\part-*.csv`

**Command argument order:** `<output path> <task name> <task-specific args> [<task name> <task-specific args> ...]`
- `hotzoneanalysis` takes 2 args: point CSV path, zone CSV path
- `hotcellanalysis` takes 1 arg: taxi trip CSV path
- Task order doesn't matter; Spark writes each task's output to its own numbered subfolder (`out0`, `out1`, …) in the order the tasks appear on the command line.

---

## What the output looks like

### Hot zone output (`out0\part-*.csv`)
CSV with two columns: rectangle string, pickup count — sorted ascending by rectangle string.
```
"-73.795658,40.743334,-73.753772,40.779114",1
"-73.797297,40.738291,-73.775740,40.770411",1
"-73.832707,40.620010,-73.746541,40.665414",20
```

### Hot cell output (`out0\part-*.csv` or `out1\part-*.csv`)
CSV with three columns: `x, y, z` (grid coordinates), 50 rows, sorted by G* score descending — **no score column** in the output.
```
-7399,4075,15
-7399,4075,29
-7399,4075,14
-7399,4075,28
-7398,4075,15
```

---

## Verified results (100k-trip sample)

- 102,951 total grid cells across the study bounds; 3,956 of them non-empty.
- The hottest cluster is centered around cell `(-7399, 4075)` — roughly 40.75°N, 73.99°W, Midtown Manhattan.
- Top 5 by G* score:

| Rank | Cell (x, y, day) | G* score |
|---|---|---|
| 1 | −7399, 4075, 15 | 79.40 |
| 2 | −7399, 4075, 22 | 77.07 |
| 3 | −7399, 4075, 14 | 76.25 |
| 4 | −7399, 4075, 29 | 76.06 |
| 5 | −7398, 4075, 15 | 75.61 |

The hot zone output was checked byte-for-byte against `testcase/hotzone/hotzone-example-answer.csv` — exact match (165 lines).

The hot cell output was cross-validated against an independent Python re-implementation of the G* formula — same top-50 cell set; ordering differs only where scores tie exactly (a few cells share identical G* values).

---

## Environment setup (Windows)

If setting this up from scratch on a new machine:

1. **Java 17** — Amazon Corretto 17 (MSI installer)
2. **sbt 1.9.4** — from https://github.com/sbt/sbt/releases/tag/v1.9.4 (`sbt-1.9.4.msi`)
3. **Apache Spark 3.4.1, Hadoop 3 build** — from https://archive.apache.org/dist/spark/spark-3.4.1/ (`spark-3.4.1-bin-hadoop3.tgz`). Extract to e.g. `C:\spark-local\spark`.
4. **Hadoop Windows binaries** (`winutils.exe`, `hadoop.dll`) — from the `cdarlint/winutils` GitHub repo, `hadoop-3.3.5/bin`. Place in `C:\spark-local\hadoop\bin`, and copy `hadoop.dll` to `C:\Windows` as well.
5. **VC++ Redistributable 2015 x64** — required for `winutils.exe` to run.
6. **Environment variables** (System → Advanced → Environment Variables → **System variables**, not User variables):
   - `JAVA_HOME` = path to Corretto 17 install
   - `SPARK_HOME` = `C:\spark-local\spark`
   - `HADOOP_HOME` = `C:\spark-local\hadoop`
   - Add `%SPARK_HOME%\bin` and `%HADOOP_HOME%\bin` to `Path`
7. **Restart the computer** after setting environment variables — required for them to take effect.

**Common pitfall:** if a variable was previously set at the *User* level, it silently overrides the correct *System*-level value with the same name. If `spark-submit --version` or `java -version` shows an unexpected old path, check both scopes:
```powershell
[Environment]::GetEnvironmentVariable("JAVA_HOME", "User")
[Environment]::GetEnvironmentVariable("JAVA_HOME", "Machine")
```
Clear the stale User-level one if it exists:
```powershell
[Environment]::SetEnvironmentVariable("JAVA_HOME", $null, "User")
```

**Verify the full toolchain works:**
```
java -version
sbt --version
spark-submit --version
```
Expect: Java 17, sbt reporting project version 1.9.4, Spark 3.4.1 with **Scala 2.12.17**.

---

## Notes

- `yellow_trip_sample_100000.csv` (~18 MB) is intentionally excluded from git via `.gitignore` — download it separately from the course's data page and place it in `src/resources/`.
- `out/`, `target/`, `.idea/`, and `.bsp/` are also git-ignored — all regenerated by build/run.
- The course's own reference answer for hot cell (`testcase/hotcell/hotcell-example-answer.csv`) was generated from a different monthly dataset than `yellow_trip_sample_100000.csv`, so exact row-for-row matching against it is not expected — only the same *method* (grid construction → G* formula → top 50) matters, which was independently verified above.

---

## Author

Sejal Patil — M.S. Computer Science Engineering, Arizona State University
