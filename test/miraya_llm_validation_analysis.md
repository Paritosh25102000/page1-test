# Miraya LLM Trade Type Validation Analysis

## Summary

**Yes, you are absolutely correct!** The LLM is returning trade type values that don't exactly match the cheat sheet.

## Mismatches Found

The following trade types were returned by the LLM but are **NOT** in the cheat sheet:

| LLM Returned | Task Count | What Cheat Sheet Has | Issue |
|--------------|------------|---------------------|-------|
| **DG** | 10 tasks | `Ext Electrical` | LLM used "DG" instead of "Ext Electrical" (line 70 in cheat sheet) |
| **Substation** | 4 tasks | `Ext Electrical` | LLM used "Substation" instead of "Ext Electrical" (line 73) |
| **Fire Fighting Work** | 106 tasks | `CA-Fire-fighting & FAPA` | LLM used generic "Fire Fighting Work" instead of CA- prefix |
| **IPS** | 94 tasks | `Flooring` | LLM extracted "IPS" as trade type, but cheat sheet line 29 has "IPS" as Activity with "Flooring" as Trade Type |
| **Handover Activity Completion** | 15 tasks | `Misc` | LLM created new category; cheat sheet line 67 uses "Misc" for handover |
| **Wooden Flooring** | 3 tasks | `Flooring` | LLM used "Wooden Flooring" as trade type, but cheat sheet line 66 has it as Activity with "Flooring" as Trade Type |
| **Landscape** | 1 task | `Ext Infra` | LLM used "Landscape" as trade type, but cheat sheet line 78 has "Landscape" as Activity with "Ext Infra" as Trade Type |
| **Boundary Wall (balance from Apr'24 onwards)** | 1 task | `Ext Infra` | LLM copied the full Activity name instead of using "Ext Infra" as Trade Type (line 79) |
| **Testing & Commissioning** | 9 tasks | `CA-PHE` | LLM created new type; cheat sheet line 45 has T&C as Activity under "CA-PHE" |
| **Shuttering- conventional** | 122 tasks | `Shuttering- Conventional` | Case mismatch: "conventional" vs "Conventional" |

## Correctly Matched Trade Types

The LLM correctly used these trade types from the cheat sheet (37 matches):

✓ BRM-Security, Blockwork, CA-Blockwork, CA-Door, CA-Electrical, CA-Fire-fighting & FAPA, CA-Flooring, CA-HVAC, CA-Int Plaster, CA-Paint, CA-PHE, CA-Railing, CP Sanitary, Concreting, Door, Electrical, Ext Electrical, Ext Fire fighting & FAPA, Ext Infra, Ext Paint, Ext PHE, False Ceiling, Flooring, Lift, Misc, NTA Finishing, NTA RCC, Paint, Plumbing, Post Pour, Railing, Reinforcement, STP, Waterproofing, Window, WTP

## Statistics

- **Cheat Sheet Trade Types:** 41 unique values
- **LLM Returned:** 47 unique values
- **Exact Matches:** 37 (78.7%)
- **Mismatches:** 10 (21.3%)

## Root Cause Analysis

The validation issues occur because:

1. **Activity vs Trade Type Confusion:** The LLM sometimes uses the Activity name (column 1) instead of the Trade Type (column 2)
   - Examples: "IPS", "Wooden Flooring", "Landscape", "Boundary Wall..."

2. **Incomplete Mappings:** Some infrastructure items in the cheat sheet don't have specific trade types:
   - "DG" activities → cheat sheet says use "Ext Electrical"
   - "Substation" activities → cheat sheet says use "Ext Electrical"

3. **Case Sensitivity:** Minor capitalization differences
   - "Shuttering- conventional" vs "Shuttering- Conventional"

4. **Genericization:** LLM sometimes creates more general categories:
   - "Fire Fighting Work" instead of context-specific "CA-Fire-fighting & FAPA"
   - "Testing & Commissioning" instead of "CA-PHE"

5. **New Categories:** LLM creates logical but non-existent categories:
   - "Handover Activity Completion" (should use "Misc")

## Impact

Despite these mismatches:
- **85.2% of tasks have HIGH confidence** - LLM is semantically correct
- The LLM correctly identifies the **work domain** (DG, Substation, Fire Fighting)
- Most issues are **naming convention mismatches**, not conceptual errors
- **21% mismatch rate** suggests the prompt needs refinement to enforce exact cheat sheet matches

## Recommendations

1. **Update Prompt:** Add explicit instruction to ONLY use values from Trade Type column (column 2)
2. **Add Examples:** Show examples of Activity → Trade Type mapping
3. **Post-processing:** Add a correction layer that maps common mistakes (e.g., "DG" → "Ext Electrical")
4. **Cheat Sheet Updates:** Consider if some LLM suggestions are actually better (e.g., separate "DG" trade type)
