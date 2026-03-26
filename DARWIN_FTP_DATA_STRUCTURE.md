# Darwinex FTP Raw Data Structure

**Source:** Darwinex FTP data feed, synced to local NAS (`/mnt/bigraidz2/Darwinex_FTP/`)
**Reference:** https://help.darwinex.com/raw-darwin-data-user-guide
**Last audited:** 2026-03-26

## Overview

- **50,317 DARWINs** in the directory
- Mix of 3-letter Classic DARWINs (e.g., `AAB`, `LVS`, `NIG`) and 4-letter Zero DARWINs (e.g., `AAAA`, `HAKR`, `ATPK`)
- Same data structure for both Classic and Zero DARWINs
- Each DARWIN has a directory with D-Score component files + quote data

## Directory Layout

```
/mnt/bigraidz2/Darwinex_FTP/
├── AAAA/
│   ├── _AAAA_former_var10/     # Historical data under old VaR 10 regime
│   │   ├── RETURN              # (same structure as current files)
│   │   ├── TRADES
│   │   └── ...
│   ├── AVG_LEVERAGE            # Current data: flat files (NOT directories)
│   ├── BADGES
│   ├── BEHAVIOR
│   ├── CLOSE_STRATEGY
│   ├── DAILY_FIXED_DIVERGENCE
│   ├── DAILY_REAL_DIVERGENCE
│   ├── DURATION_CONSISTENCY
│   ├── EXPERIENCE
│   ├── LOSING_CONSISTENCY
│   ├── LOSS_AVERSION
│   ├── LOSS_AVERSION_UNADJUSTED_VAR
│   ├── MARKET_CORRELATION
│   ├── MONTHLY_DIVERGENCE
│   ├── OPEN_STRATEGY
│   ├── ORDER_DIVERGENCE
│   ├── PERFORMANCE
│   ├── POSITIONS
│   ├── RETURN
│   ├── RETURN_DIVERGENCE
│   ├── RISK_ADJUSTMENT
│   ├── RISK_STABILITY
│   ├── ROTATION
│   ├── SCALABILITY
│   ├── TRADE_CONSISTENCY
│   ├── TRADE_LOSS_AVERSION
│   ├── TRADES
│   ├── TRADE_UNADJUSTED_LOSS_AVERSION
│   ├── WINNING_CONSISTENCY
│   └── quotes/
│       ├── 2024-06/
│       │   ├── AAAA.5.1_97905_2026-02-11.18.csv.gz
│       │   └── ...
│       ├── 2024-07/
│       └── ...
```

**IMPORTANT:** The FTP sync creates both:
1. **Empty subdirectories** with the component names (e.g., `RETURN/` directory)
2. **Flat files** at the top level with the same names (e.g., `RETURN` file)

The **flat files are the actual data**. The subdirectories are empty scaffolding from the FTP directory listing.

## D-Score Component Files

Each file is a CSV-like format with one row per trading day:

```
timestamp_ms,d_score_value[,extra_data]
```

- `timestamp_ms` — Unix epoch milliseconds (midnight UTC of the trading day)
- `d_score_value` — Normalized score for that component (0.0 to ~10.0)
- `extra_data` — Component-specific nested data (Python list/tuple literals)

### RETURN
Daily return score + cumulative equity curve.

```
1715893200000,0.0,[1.0]
1716152400000,0.0,[1.0, 1.00027774, 0.99969814, 1.020174900095215, 1.0201311319127138]
1716238800000,0.06666666666666667,[1.0201311319127138, 1.0103213821017576]
```

- Column 1: timestamp
- Column 2: D-Score return component
- Column 3: Array of cumulative return values (equity multiplier, 1.0 = starting point)
- Last value in array = current cumulative return

### TRADES
Daily trade activity score.

```
1715893200000,0.0
1716152400000,0.0
1716238800000,0.06666666666666667
```

- Simple timestamp + score. No extra data.

### POSITIONS
Open positions with per-symbol statistics.

```
1716152400000,0.0,[['CAT', 5, 2, 3, 1.020766372009022, 0.9986702002101621, 22582957, 63028797]],5,4
```

- Column 3: Array of position tuples: `['SYMBOL', total_trades, wins, losses, best_return, worst_return, min_hold_ms, max_hold_ms]`
- Column 4: open position count
- Column 5: total closed position count

### EXPERIENCE
Track record length and trade count.

```
1716238800000,0.06666666666666667,[1, 3.9551066280653657]
```

- Column 3: `[trade_count, months_of_experience]`

### RISK_STABILITY
VaR stability score (Darwinex measures consistency of risk-taking).

```
1716152400000,0.0,[5, None, None, [0.841..., 1.0083, [1.019..., ...], 0]]
```

- Complex nested structure with VaR percentile data and distribution parameters.

### PERFORMANCE
Return quality adjusted for risk.

```
1716152400000,0.0,[5, None, None, [0.643..., 1.0044, [...], 1]]
```

- Similar nested structure to RISK_STABILITY.

### BADGES
Darwinex badge history (quality markers).

### BEHAVIOR
Trading behavior consistency.

### CLOSE_STRATEGY / OPEN_STRATEGY
Entry/exit strategy analysis.

### DURATION_CONSISTENCY
Holding period consistency.

### LOSING_CONSISTENCY / WINNING_CONSISTENCY
Loss/win pattern consistency.

### LOSS_AVERSION / TRADE_LOSS_AVERSION
How the trader handles losing trades.

### MARKET_CORRELATION
Correlation to broad market indices.

### MONTHLY_DIVERGENCE / DAILY_FIXED_DIVERGENCE / DAILY_REAL_DIVERGENCE / RETURN_DIVERGENCE / ORDER_DIVERGENCE
Various divergence metrics between the DARWIN and its underlying strategy.

### RISK_ADJUSTMENT
Risk adjustment factor applied by Darwinex.

### ROTATION
Symbol rotation patterns.

### SCALABILITY
Capacity assessment (how much AUM the strategy can handle).

### TRADE_CONSISTENCY
Consistency of trade execution.

## Quote Data

Tick-level DARWIN price quotes stored as gzipped CSV files:

```
quotes/
├── 2024-06/
│   ├── HAKR.5.22_58832_2025-07-11.16.csv.gz
│   └── ...
```

### Filename Format
```
{DARWIN}.{version}.{var}_{investor_id}_{date}.{hour}.csv.gz
```

- `HAKR.5.22` — DARWIN ticker, version 5, VaR setting 22
- `58832` — Investor/account ID
- `2025-07-11.16` — Date and hour (UTC)

### File Contents
```csv
timestamp,quote
1752249621595,126.8677
1752249630662,126.8664
1752249659112,126.8677
```

- `timestamp` — Unix epoch milliseconds
- `quote` — DARWIN price (normalized, starts at 100.0 at DARWIN creation)

## `_former_var10/` Directory

Contains the same D-Score component files but from the **old VaR 10 regime** (before Darwinex migrated DARWINs to the current variable VaR system). Only present for DARWINs that existed before the migration.

Structure is identical to the current files — same format, same component names. Useful for comparing pre/post VaR migration performance.

## Data Volume Estimates

| Data Type | Per DARWIN | 50K DARWINs | Notes |
|-----------|-----------|-------------|-------|
| D-Score files (23 components) | ~50 KB total | ~2.5 GB | 481 daily rows × 23 files |
| Quotes (1 year) | ~3,000 files, ~50 MB | ~2.5 TB | Gzipped tick data |
| former_var10 | ~50 KB total | ~2.5 GB | Same as D-Score |

## Efficient I/O Strategy (ZFS raidz2, 6 disks, 2.5Gbit LAN)

1. **D-Score component scan**: Sequential read of flat files. ~50KB per DARWIN × 50K = 2.5GB total. ZFS raidz2 delivers ~500MB/s sequential → ~5 seconds for full scan.

2. **Quote data**: Gzipped CSVs, random access by month. Decompress on read. For correlation analysis, only need RETURN file (not quotes).

3. **Batch indexing**: Read all RETURN files in a single pass to build a returns database for correlation screening. This is the most useful first step.

4. **Avoid**: Don't `find` recursively across all 50K dirs — use direct path construction (`{ftp_dir}/{ticker}/RETURN`). The empty subdirectories cause `find` to do unnecessary directory traversals.

## Our 6 DARWINs — Current Sync Status (2026-03-26)

| DARWIN | Quote Files | D-Score Data | former_var10 | Notes |
|--------|------------|-------------|-------------|-------|
| ATPK | 2,840 | Quotes only | No | 4-letter Zero |
| HAKR | 3,649 | 481 days (full) | Yes (23 files) | 4-letter Zero, fully synced |
| WBYE | 2,724 | Syncing | No | 4-letter Zero |
| GVZJ | 2,642 | Quotes only | No | 4-letter Zero |
| MFSO | 2,668 | Quotes only | No | 4-letter Zero |
| XUQF | 3,429 | Quotes only | No | 4-letter Zero |

## Parsing Notes

- Timestamps are **milliseconds since Unix epoch** (divide by 1000 for seconds)
- The "extra data" columns use **Python literal syntax** (lists, tuples, None) — need a custom parser, not standard CSV
- Some fields contain `None` (Python null) — treat as missing/null
- RETURN cumulative array gives the full equity curve within each day's data point
- POSITIONS symbol stats use Python list syntax: `[['SYM', int, int, int, float, float, int, int]]`
