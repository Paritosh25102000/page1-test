# Enrichment Analysis Report (Updated)

## Summary Statistics

- **Total Projects**: 12
- **Total Unique Towers**: 42
- **Total Unique Floors**: 78
- **Total Tasks Enriched**: 97,977

---

## Global Unique Values

### All Unique Towers (42)

| Category | Tower Values |
|----------|--------------|
| **T-Patterns** | T1, T2, T3, T4, T5, T6 |
| **Tower (Numeric)** | Tower 1, Tower 2, Tower 2A, Tower 3, Tower 4, Tower 5, Tower 6, Tower 7 |
| **Tower (Zero-padded)** | Tower 01, Tower 02, Tower 03, Tower 04, Tower 05, Tower 06, Tower 07, Tower 08, Tower 09 |
| **Tower (Alphabetic)** | Tower A, Tower B, Tower C, Tower D, Tower E, Tower F, Tower G, Tower H, Tower J, Tower K, Tower L, Tower M, Tower N, Tower P, Tower Q, Tower s |
| **Tower (Combined)** | Tower T1, Tower T2, Tower T6 |

**Excluded Patterns (Successfully Removed):**
- ✅ Block Work, Block work (not spatial structures)
- ✅ Building Certification, Building certifications (not spatial structures)
- ✅ Tower Area, Tower Completion, Tower Drop, Tower Finishing (descriptive, not identifiers)
- ✅ Tower Ground, Tower Raft, Tower Structure (construction phases, not identifiers)

### All Unique Floors (78)

| Floor Range | Values |
|-------------|--------|
| **Basement** | Basement, Basement 1, Basement 2, Basement 3 |
| **Ground** | Ground Floor |
| **1-10** | 1st Floor, 2nd Floor, 3rd Floor, 4th Floor, 5th Floor, 6th Floor, 7th Floor, 8th Floor, 9th Floor, 10th Floor |
| **11-20** | 11th Floor, 12th Floor, 13th Floor, 14th Floor, 15th Floor, 16th Floor, 17th Floor, 18th Floor, 19th Floor, 20th Floor |
| **21-30** | 21st Floor, 22nd Floor, 23rd Floor, 24th Floor, 25th Floor, 26th Floor, 27th Floor, 28th Floor, 29th Floor, 30th Floor |
| **31-40** | 31st Floor, 32nd Floor, 33rd Floor, 34th Floor, 35th Floor, 36th Floor, 37th Floor, 38th Floor, 39th Floor, 40th Floor |
| **41-50** | 41st Floor, 42nd Floor, 43rd Floor, 44th Floor, 45th Floor, 46th Floor, 47th Floor, 48th Floor, 49th Floor, 50th Floor |
| **51-60** | 51st Floor, 52nd Floor, 53rd Floor, 54th Floor, 55th Floor, 56th Floor, 57th Floor, 58th Floor, 59th Floor, 60th Floor |
| **61-72** | 61st Floor, 62nd Floor, 63rd Floor, 64th Floor, 65th Floor, 66th Floor, 67th Floor, 68th Floor, 69th Floor, 70th Floor, 71st Floor, 72nd Floor |
| **Terrace** | Terrace |

**Floor Range**: Basement 1-3 to 72nd Floor + Terrace

**Normalization Applied:**
- ✅ B1, B2, B3 → Basement 1, Basement 2, Basement 3
- ✅ Basement 01, 02, 03 → Basement 1, 2, 3 (leading zeros removed)

---

## By Project Analysis

### Aristocrat
- **Zone**: NZ
- **Region**: NZ1
- **Towers**: 7 unique
  - Tower 1, Tower 2, Tower 3, Tower 4, Tower 5, Tower 6, Tower s
- **Floors**: 37 unique (Basement 1-2 to 32nd Floor + Terrace)
- **Enriched Tasks**: 4,984 / 5,614 (89%)

### Azadnagar (Horizon)
- **Zone**: MZ
- **Region**: MZ1
- **Towers**: 12 unique
  - T1, T2, T3, T4, T5, T6, Tower 1, Tower 2, Tower 3, Tower 4, Tower 5, Tower 6
- **Floors**: 54 unique (Basement 1-3 to 48th Floor + Terrace)
- **Enriched Tasks**: 15,705 / 17,456 (90%)

### BLSaha (BL Saha)
- **Zone**: WEZ
- **Region**: Kolkata
- **Towers**: 7 unique
  - Tower 1, Tower 2, Tower 3, Tower 4, Tower 5, Tower 6, Tower 7
- **Floors**: 22 unique (1st to 21st Floor + Terrace)
- **Enriched Tasks**: 9,517 / 10,065 (95%)

### Bigbull-Reserve (Reserve)
- **Zone**: MZ
- **Region**: MZ1
- **Towers**: 10 unique
  - Tower 1, Tower 2, Tower 3, Tower 4, Tower 5, Tower 6, Tower T1, Tower T2, Tower T6, Tower s
- **Floors**: 54 unique (Ground Floor to 52nd Floor + Terrace)
- **Enriched Tasks**: 14,843 / 16,438 (90%)

### Jardinia
- **Zone**: NZ
- **Region**: NZ2
- **Towers**: 6 unique
  - Tower 1, Tower 2, Tower 3, Tower 4, Tower 5, Tower s
- **Floors**: 39 unique (Basement to 35th Floor + Terrace)
- **Enriched Tasks**: 4,209 / 4,723 (89%)

### Miraya
- **Zone**: NZ
- **Region**: NZ1
- **Towers**: 3 unique
  - Tower A, Tower B, Tower C
- **Floors**: 37 unique (Basement 1-2 to 32nd Floor + Terrace)
- **Enriched Tasks**: 2,527 / 2,849 (89%)

### OneM (Avenue 11)
- **Zone**: MZ
- **Region**: MZ1
- **Towers**: 2 unique
  - Tower A, Tower B
- **Floors**: 72 unique (Basement 1-2 to 72nd Floor + Terrace)
- **Enriched Tasks**: 3,483 / 3,910 (89%)

### RGA Land2 (RGA 2)
- **Zone**: SZ
- **Region**: SZ1
- **Towers**: 8 unique
  - Tower 1, Tower 2, Tower 2A, Tower 3, Tower 4, Tower 5, Tower 6, Tower 7
- **Floors**: 28 unique (Basement to 25th Floor + Terrace)
- **Enriched Tasks**: 7,198 / 8,492 (85%)

### Riverine (Sec. 44, Noida)
- **Zone**: NZ
- **Region**: NZ2
- **Towers**: 4 unique
  - Tower 1, Tower 2, Tower 3, Tower 4
- **Floors**: 43 unique (Basement 1-2 to 38th Floor + Terrace)
- **Enriched Tasks**: 3,037 / 3,635 (84%)

### Tropical Isle 146 (Tropical Isle)
- **Zone**: NZ
- **Region**: NZ2
- **Towers**: 6 unique
  - Tower 1, Tower 2, Tower 3, Tower 4, Tower 5, Tower s
- **Floors**: 39 unique (Basement to 35th Floor + Terrace)
- **Enriched Tasks**: 4,257 / 4,770 (89%)

### Woodscapes
- **Zone**: SZ
- **Region**: SZ1
- **Towers**: 15 unique
  - Tower A, Tower B, Tower C, Tower D, Tower E, Tower F, Tower G, Tower H, Tower J, Tower K, Tower L, Tower M, Tower N, Tower P, Tower Q
- **Floors**: 44 unique (Basement to 39th Floor + Terrace)
- **Enriched Tasks**: 20,201 / 23,494 (86%)

### Zenith
- **Zone**: NZ
- **Region**: NZ1
- **Towers**: 9 unique
  - Tower 01, Tower 02, Tower 03, Tower 04, Tower 05, Tower 06, Tower 07, Tower 08, Tower 09
- **Floors**: 42 unique (Basement 3 to 36th Floor + Terrace)
- **Enriched Tasks**: 8,016 / 8,978 (89%)

---

## Tower Naming Patterns (Cleaned)

### 1. Numeric Towers
- **Standard**: Tower 1, Tower 2, Tower 3, Tower 7
- **Zero-padded**: Tower 01, Tower 02, Tower 03, Tower 09
- **Combined**: Tower T1, Tower T2, Tower T6
- **Alpha Suffix**: Tower 2A

### 2. Alphabetic Towers
- **Single Letter**: Tower A, Tower B, Tower C, Tower Q
- Used in: Miraya, Woodscapes, OneM

### 3. Short Form
- **T-Pattern**: T1, T2, T3, T4, T5, T6
- Used in: Azadnagar (Horizon)

### 4. Special Case
- **Tower s**: Appears in multiple projects (Aristocrat, Bigbull-Reserve, Jardinia, Tropical Isle 146)
  - Likely represents a specific tower designation in the source data

---

## Floor Naming Patterns (Normalized)

### 1. Standard Ordinal Floors
- **Format**: [Number][Ordinal Suffix] Floor
- **Examples**: 1st Floor, 2nd Floor, 3rd Floor, 72nd Floor
- **Range**: 1st to 72nd Floor

### 2. Basement (Normalized)
- **Format**: Basement [Number]
- **Examples**: Basement, Basement 1, Basement 2, Basement 3
- **Source Formats**: B1, B2, B3, Basement 01, Basement 02, Basement 03
- **All normalized to**: Basement, Basement 1, Basement 2, Basement 3

### 3. Special Floors
- **Ground Floor**: Entry level
- **Terrace**: Roof level

---

## Improvements from V1

### Towers
- **Before**: 54 unique towers (including Block, Building, and descriptive names)
- **After**: 42 unique towers (only spatial identifiers)
- **Removed**: 12 invalid patterns
  - Block Work, Block work
  - Building Certification, Building certifications
  - Tower Area, Tower Completion, Tower Drop, Tower Finishing, Tower Ground, Tower Raft, Tower Structure

### Floors
- **Before**: 83 unique floors (with variants like B1, B2, Basement 01)
- **After**: 78 unique floors (normalized basement values)
- **Normalized**: Basement formats
  - B1, B2, B3 → Basement 1, Basement 2, Basement 3
  - Basement 01, 02, 03 → Basement 1, 2, 3

---

## Coverage Analysis

| Project | Tower Coverage | Floor Coverage | Overall Enrichment |
|---------|---------------|----------------|-------------------|
| BLSaha | High | High | 95% |
| Azadnagar | High | Very High | 90% |
| Bigbull-Reserve | High | Very High | 90% |
| Aristocrat | High | High | 89% |
| Jardinia | High | High | 89% |
| Miraya | High | High | 89% |
| OneM | High | Very High | 89% |
| Tropical Isle 146 | High | High | 89% |
| Zenith | High | High | 89% |
| Woodscapes | Very High | High | 86% |
| RGA Land2 | High | High | 85% |
| Riverine | High | High | 84% |

**Average Enrichment Rate**: 88.6%

---

## Data Quality Summary

### ✅ Successfully Cleaned
1. **Removed non-spatial patterns**: Block, Building no longer extracted as towers
2. **Removed descriptive patterns**: Tower Area, Tower Completion, etc. excluded
3. **Normalized basement values**: All B1/Basement 01 formats → Basement 1
4. **Consistent floor formatting**: All floors follow standard ordinal format

### ⚠️ Remaining Considerations
1. **Case sensitivity**: Some projects may have different capitalizations
2. **Tower numbering**: Mix of numeric (Tower 1), zero-padded (Tower 01), and short (T1) formats
3. **Tower s**: Appears across multiple projects - likely a valid designation but worth verifying

---

## Generated On
2025-12-10 (Updated)

## Notes
- This report was auto-generated from enriched JSON output after cleaning
- All unique values are extracted from actual task attributes
- Coverage percentages represent tasks with at least one enriched attribute (zone, region, tower, or floor)
- Block/Building patterns successfully removed from tower extraction
- Basement floor values successfully normalized
