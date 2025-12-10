"""
Classify construction activities using LLM (Gemini Flash 2.5 via OpenRouter).

Handles:
- Cheat sheet loading and parsing
- Prompt engineering for classification
- LLM API calls
- Response validation
"""

import json
import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


def load_cheat_sheet(path: str) -> Tuple[str, Dict[str, Dict]]:
    """
    Load trade type cheat sheet from markdown file.

    Args:
        path: Path to cheat sheet markdown file

    Returns:
        Tuple of (simplified_markdown_for_llm, trade_type_lookup_dict)
    """
    with open(path, 'r', encoding='utf-8') as f:
        markdown_text = f.read()

    # Parse the markdown table
    trade_type_lookup = {}
    simplified_lines = ["| Activity Examples | Trade Type |", "|-------------------|------------|"]

    lines = markdown_text.strip().split('\n')

    # Skip header and separator rows
    data_lines = [line for line in lines[2:] if line.strip() and '|' in line]

    for line in data_lines:
        parts = [p.strip() for p in line.split('|')]
        if len(parts) >= 5:  # At least: |, Activity, Trade Type, Sub-Category, Main Category, |
            activity = parts[1]
            trade_type = parts[2]
            sub_category = parts[3]
            main_category = parts[4]

            if activity and trade_type:  # Valid row
                # Build simplified cheat sheet for LLM (only Activity and Trade Type)
                simplified_lines.append(f"| {activity} | {trade_type} |")

                # Build lookup table for automatic mapping
                if trade_type not in trade_type_lookup:
                    trade_type_lookup[trade_type] = {
                        "sub_category": sub_category,
                        "main_category": main_category,
                    }

    simplified_markdown = "\n".join(simplified_lines)
    logger.info(f"Loaded {len(trade_type_lookup)} unique trade types from cheat sheet")
    return simplified_markdown, trade_type_lookup


def build_classification_prompt(
    unique_activities: Dict,
    cheat_sheet_text: str
) -> str:
    """
    Build optimized prompt for LLM classification.

    Args:
        unique_activities: Output from extract_unique_activities
        cheat_sheet_text: Full cheat sheet markdown

    Returns:
        Formatted prompt string
    """
    project = unique_activities["project"]
    activities = unique_activities["unique_activities"]

    # Build activity list
    activity_list_lines = []
    for i, activity in enumerate(activities, 1):
        activity_list_lines.append(
            f"{i}. Activity: \"{activity['activity_name']}\"\n"
            f"   Context: {activity['context_type']}\n"
            f"   Occurrences: {activity['occurrence_count']}\n"
            f"   Sample tasks: {', '.join(activity['sample_task_names'][:3])}"
        )

    activity_list = "\n\n".join(activity_list_lines)

    # Build prompt
    prompt = f"""You are a construction work classification expert specializing in high-rise residential projects.
Your task is to classify construction activities into TRADE TYPES ONLY based on the provided cheat sheet.

CRITICAL: THE CHEAT SHEET STRUCTURE
The cheat sheet has 2 columns:
1. Activity Examples - EXAMPLES ONLY (not exhaustive, just hints of what work might belong to a trade type)
2. Trade Type - THE ACTUAL VALUE YOU MUST RETURN (this is what you classify)

YOUR TASK: Return ONLY the Trade Type from column 2.
NEVER use values from column 1 (Activity Examples) as your output - those are just examples to help you understand what belongs to each trade type.

EXAMPLE:
Cheat sheet row: | IPS | Flooring |
- Column 1: "IPS" is just an EXAMPLE of flooring work
- Column 2: "Flooring" is what you MUST return as trade_type
- If you see "IPS" work, return trade_type="Flooring", NOT "IPS"

EXAMPLE:
Cheat sheet row: | DG | Ext Electrical |
- Column 1: "DG" is just an example of electrical infrastructure work
- Column 2: "Ext Electrical" is what you MUST return
- If you see DG/generator work, return trade_type="Ext Electrical", NOT "DG"

KEY CLASSIFICATION RULES:

1. Context Matters - The same activity may have different classifications based on context:
   - "tower" context (flats/apartments): Use Tower-specific trade types (e.g., Blockwork, Flooring, Int Plaster)
   - "common_area" context: Use CA- prefixed trade types (e.g., CA-Blockwork, CA-Flooring, CA-Paint)
   - "external" context: Use Ext- prefixed trade types (e.g., Ext Electrical, Ext Plumbing)
   - "infrastructure" context: Infrastructure trade types (e.g., STP, WTP, Ext Electrical for DG/Substation)

2. Common Area Indicators (use CA- prefix):
   - Activities in staircases, lifts, lobbies, corridors
   - Basement/parking finishing (when common area)
   - Common area MEP work

3. Tower/Flat Indicators (NO CA- prefix):
   - Activities within apartment units
   - Internal flat finishing
   - Flat-level MEP work

4. Activity Synonyms - Match semantic meaning, then lookup correct Trade Type:
   - "IPS", "Indian Patent Stone" → trade_type="Flooring" (NOT "IPS")
   - "DG", "Diesel Generator" → trade_type="Ext Electrical" (NOT "DG")
   - "Wooden Flooring" → trade_type="Flooring" (NOT "Wooden Flooring")
   - "Landscape", "Softscape" → trade_type="Ext Infra" (NOT "Landscape")
   - "Blockwork" = "Block Work" = "Internal Block Work" → trade_type="Blockwork"
   - "Plaster" = "Plastering" → trade_type="Int Plaster" or "CA-Int Plaster" (based on context)

5. Infrastructure Activities - Common mappings:
   - DG (Diesel Generator) work → trade_type="Ext Electrical"
   - Substation/Transformer work → trade_type="Ext Electrical"
   - STP work → trade_type="STP"
   - WTP work → trade_type="WTP"
   - Solar work → trade_type="Solar"
   - Landscape/Garden work → trade_type="Ext Infra"
   - Road/Pavement work → trade_type="Ext Infra"
   - Boundary wall → trade_type="Ext Infra"

6. MANDATORY: Use ONLY exact values from cheat sheet columns 2, 3, 4:
   - trade_type must EXACTLY match a value from "Trade Type" column (column 2)
   - sub_category must EXACTLY match a value from "Sub-Category" column (column 3)
   - main_category must EXACTLY match a value from "Summary- Main category codes" column (column 4)
   - NEVER invent new trade type names
   - NEVER use Activity column values as trade_type

PROJECT: {project}

ACTIVITIES TO CLASSIFY:

{activity_list}

TRADE TYPE CHEAT SHEET:

{cheat_sheet_text}

OUTPUT REQUIREMENTS:

Return ONLY a valid JSON array with the following structure. Do NOT include any explanatory text before or after the JSON.

[
  {{
    "activity_name": "exact activity name from input",
    "context_type": "context from input (tower/common_area/external/infrastructure)",
    "trade_type": "MUST be exact value from Trade Type column (column 2) - NEVER from Activity column",
    "confidence": "high/medium/low",
    "reasoning": "brief explanation: which cheat sheet row you used and why"
  }}
]

CRITICAL REMINDERS:
- Return classifications for ALL {len(activities)} activities
- Return ONLY trade_type (we will automatically fill sub_category and main_category based on trade_type)
- Use context_type to distinguish Tower vs Common Area activities
- trade_type MUST be from column 2, NOT column 1
- Match values EXACTLY as they appear in cheat sheet column 2 (Trade Type)
- Match case exactly (e.g., "Shuttering- Conventional" not "Shuttering- conventional")
- If unsure, use confidence: "medium" or "low"
- The Activity column is for reference only - understand the concept, but use Trade Type column value
"""

    return prompt


async def classify_activities_with_llm(
    unique_activities: Dict,
    project_name: str,
    llm,
    cheat_sheet_path: str
) -> Dict:
    """
    Classify unique activities using Gemini Flash 2.5.

    Args:
        unique_activities: Output from extract_unique_activities
        project_name: Name of the project
        llm: UniversalLLM instance
        cheat_sheet_path: Path to cheat sheet file

    Returns:
        Classification results dictionary
    """
    logger.info(f"Classifying activities for project: {project_name}")

    # Load cheat sheet
    cheat_sheet_text, trade_type_lookup = load_cheat_sheet(cheat_sheet_path)

    # Build prompt
    prompt = build_classification_prompt(unique_activities, cheat_sheet_text)

    logger.info(f"Sending {len(unique_activities['unique_activities'])} activities to LLM")

    # Log the prompt for debugging
    logger.info("=" * 80)
    logger.info("LLM PROMPT:")
    logger.info("=" * 80)
    logger.info(prompt)
    logger.info("=" * 80)

    try:
        # Call LLM
        messages = [
            {"role": "user", "content": prompt}
        ]

        logger.info("Calling LLM API...")
        response = await llm.ainvoke(messages)
        response_text = response.content

        logger.info("=" * 80)
        logger.info("LLM RESPONSE:")
        logger.info("=" * 80)
        logger.info(response_text)
        logger.info("=" * 80)
        logger.info(f"Response length: {len(response_text)} characters")

        # Parse JSON response
        classifications = parse_llm_response(response_text)

        if not classifications:
            raise ValueError("No classifications returned from LLM")

        logger.info(f"Received {len(classifications)} classifications from LLM")

        # Automatically fill sub_category and main_category based on trade_type
        validated_classifications = []
        validation_issues_count = 0
        for classification in classifications:
            trade_type = classification.get("trade_type")

            # Lookup sub_category and main_category from trade_type
            if trade_type in trade_type_lookup:
                classification["sub_category"] = trade_type_lookup[trade_type]["sub_category"]
                classification["main_category"] = trade_type_lookup[trade_type]["main_category"]
                classification["validation_status"] = "valid"
                classification["validation_issues"] = []
            else:
                # Trade type not found in cheat sheet
                classification["sub_category"] = ""
                classification["main_category"] = ""
                classification["validation_status"] = "invalid"
                classification["validation_issues"] = [f"Trade type '{trade_type}' not found in cheat sheet"]
                validation_issues_count += 1
                logger.warning(f"Trade type not found in cheat sheet: '{trade_type}' for activity '{classification.get('activity_name')}'")

            validated_classifications.append(classification)

        # Log validation results
        logger.info("=" * 80)
        logger.info("VALIDATION RESULTS:")
        logger.info("=" * 80)
        for i, classification in enumerate(validated_classifications, 1):
            status = "✓" if classification.get("validation_status") == "valid" else "✗"
            logger.info(
                f"{status} {i}. {classification.get('activity_name')} ({classification.get('context_type')})\n"
                f"     Trade Type: {classification.get('trade_type')}\n"
                f"     Sub-Category: {classification.get('sub_category')}\n"
                f"     Main Category: {classification.get('main_category')}\n"
                f"     Confidence: {classification.get('confidence')}"
            )
            if classification.get("validation_issues"):
                for issue in classification["validation_issues"]:
                    logger.warning(f"     Issue: {issue}")
        logger.info("=" * 80)
        logger.info(f"Valid classifications: {len(validated_classifications) - validation_issues_count}/{len(validated_classifications)}")
        logger.info("=" * 80)

        # Calculate stats
        high_confidence = sum(1 for c in validated_classifications if c.get("confidence") == "high")
        medium_confidence = sum(1 for c in validated_classifications if c.get("confidence") == "medium")
        low_confidence = sum(1 for c in validated_classifications if c.get("confidence") == "low")

        result = {
            "project": project_name,
            "classifications": validated_classifications,
            "total_classified": len(validated_classifications),
            "confidence_distribution": {
                "high": high_confidence,
                "medium": medium_confidence,
                "low": low_confidence
            }
        }

        logger.info(
            f"Classification complete: {high_confidence} high, {medium_confidence} medium, {low_confidence} low confidence"
        )

        return result

    except Exception as e:
        logger.error(f"Error classifying activities: {e}")
        raise


def parse_llm_response(response_text: str) -> List[Dict]:
    """
    Parse LLM JSON response, handling various formats.

    Args:
        response_text: Raw LLM response

    Returns:
        List of classification dictionaries
    """
    # Try to extract JSON array from response
    # Sometimes LLM adds explanatory text before/after JSON

    # Try direct JSON parse first
    try:
        data = json.loads(response_text)
        if isinstance(data, list):
            return data
        elif isinstance(data, dict) and "classifications" in data:
            return data["classifications"]
    except json.JSONDecodeError:
        pass

    # Try to find JSON array in text
    json_pattern = r'\[[\s\S]*\]'
    match = re.search(json_pattern, response_text)
    if match:
        try:
            data = json.loads(match.group(0))
            if isinstance(data, list):
                return data
        except json.JSONDecodeError:
            pass

    # If all else fails, try to parse line by line
    logger.warning("Could not parse JSON response, attempting line-by-line parsing")
    raise ValueError("Unable to parse LLM response as JSON")


def validate_classification(
    classification: Dict,
    cheat_sheet_data: List[Dict]
) -> Dict:
    """
    Validate LLM output against cheat sheet.

    Checks:
    - Trade type exists in cheat sheet
    - Sub-category matches trade type
    - Main category matches sub-category

    Args:
        classification: Classification from LLM
        cheat_sheet_data: Parsed cheat sheet

    Returns:
        Validated classification with validation_status
    """
    trade_type = classification.get("trade_type", "")
    sub_category = classification.get("sub_category", "")
    main_category = classification.get("main_category", "")

    # Find matching entry in cheat sheet
    matches = [
        entry for entry in cheat_sheet_data
        if entry["trade_type"] == trade_type
    ]

    if not matches:
        # Try case-insensitive match
        matches = [
            entry for entry in cheat_sheet_data
            if entry["trade_type"].lower() == trade_type.lower()
        ]

    validation_issues = []

    if not matches:
        validation_issues.append(f"Trade type '{trade_type}' not found in cheat sheet")
    else:
        # Check if sub-category and main category match
        match = matches[0]  # Use first match

        if match["sub_category"] != sub_category:
            validation_issues.append(
                f"Sub-category mismatch: expected '{match['sub_category']}', got '{sub_category}'"
            )

        if match["main_category"] != main_category:
            validation_issues.append(
                f"Main category mismatch: expected '{match['main_category']}', got '{main_category}'"
            )

    # Add validation status
    classification["validation_status"] = "valid" if not validation_issues else "invalid"
    classification["validation_issues"] = validation_issues

    # Lower confidence if validation failed
    if validation_issues and classification.get("confidence") == "high":
        classification["confidence"] = "medium"
        logger.warning(
            f"Validation issues for '{classification.get('activity_name')}': {validation_issues}"
        )

    return classification


def get_classification_summary(classification_result: Dict) -> str:
    """
    Generate human-readable summary of classification results.

    Args:
        classification_result: Output from classify_activities_with_llm

    Returns:
        Formatted summary string
    """
    project = classification_result["project"]
    total = classification_result["total_classified"]
    confidence = classification_result["confidence_distribution"]

    summary_lines = [
        f"Classification Results for {project}",
        f"Total classified: {total}",
        f"Confidence: {confidence['high']} high, {confidence['medium']} medium, {confidence['low']} low",
        "",
        "Sample Classifications:",
    ]

    # Show first 10
    for i, classification in enumerate(classification_result["classifications"][:10], 1):
        status_marker = "✓" if classification.get("validation_status") == "valid" else "⚠"
        summary_lines.append(
            f"  {status_marker} {i}. {classification['activity_name']} ({classification['context_type']})\n"
            f"     → {classification['trade_type']} | {classification['sub_category']} | "
            f"{classification['main_category']}"
        )

    # Show any validation issues
    invalid = [c for c in classification_result["classifications"] if c.get("validation_status") != "valid"]
    if invalid:
        summary_lines.append("")
        summary_lines.append(f"Validation Issues: {len(invalid)} classifications")

    return "\n".join(summary_lines)
