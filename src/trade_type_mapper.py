"""
Map LLM classifications back to individual tasks.

Handles:
- Matching tasks to classifications by activity name + context type
- Enriching leaf task attributes with trade type data
- Handling unmatched tasks
- Statistics tracking
"""

import logging
from typing import Dict, List

logger = logging.getLogger(__name__)


def map_classifications_to_tasks(
    tasks: List[Dict],
    classification_result: Dict,
    unique_activities_data: Dict
) -> Dict:
    """
    Map LLM classifications back to individual leaf tasks.

    Algorithm:
    1. Build classification lookup by (activity_name, context_type)
    2. For each leaf task:
       - Extract activity name and context (same as extractor logic)
       - Look up classification
       - Enrich task attributes with trade type data
    3. Track statistics

    Args:
        tasks: List of task dictionaries (will be modified in-place)
        classification_result: Output from classify_activities_with_llm
        unique_activities_data: Output from extract_unique_activities

    Returns:
        Dictionary with enrichment statistics
    """
    project_name = classification_result["project"]
    logger.info(f"Mapping classifications to tasks for project: {project_name}")

    # Build classification lookup
    classification_lookup = build_classification_lookup(
        classification_result["classifications"]
    )

    # Build activity lookup (for efficient matching)
    activity_lookup = build_activity_lookup(unique_activities_data)

    # Track statistics
    stats = {
        "total_leaf_tasks": 0,
        "enriched_tasks": 0,
        "unmatched_tasks": 0,
        "validation_issues": 0,
        "by_context": {
            "tower": 0,
            "common_area": 0,
            "external": 0,
            "infrastructure": 0,
        },
        "by_confidence": {
            "high": 0,
            "medium": 0,
            "low": 0,
        },
    }

    # Enrich tasks
    for task in tasks:
        # Only process leaf tasks
        if task.get("is_summary") or task.get("is_milestone"):
            continue

        if task.get("attributes") is None:
            continue

        stats["total_leaf_tasks"] += 1

        # Get activity info from unique_activities extraction
        task_wbs = task.get("wbs")
        activity_info = activity_lookup.get(task_wbs)

        if not activity_info:
            # Task wasn't in extraction (shouldn't happen)
            stats["unmatched_tasks"] += 1
            logger.warning(f"Task {task_wbs} not found in activity extraction")
            continue

        activity_name = activity_info["activity_name"]
        context_type = activity_info["context_type"]

        # Look up classification
        key = (activity_name, context_type)
        classification = classification_lookup.get(key)

        if not classification:
            # No classification found (shouldn't happen if LLM returned all)
            stats["unmatched_tasks"] += 1
            logger.warning(
                f"No classification found for activity '{activity_name}' "
                f"with context '{context_type}'"
            )
            continue

        # Enrich task attributes
        task["attributes"]["trade_type"] = classification.get("trade_type")
        task["attributes"]["sub_category"] = classification.get("sub_category")
        task["attributes"]["main_category"] = classification.get("main_category")

        # Note: classification_confidence and classification_reasoning are logged but not stored in output
        # to comply with task_schema.json

        stats["enriched_tasks"] += 1
        stats["by_context"][context_type] += 1
        stats["by_confidence"][classification.get("confidence", "unknown")] += 1

        if classification.get("validation_status") != "valid":
            stats["validation_issues"] += 1

    # Calculate enrichment rate
    enrichment_rate = (
        stats["enriched_tasks"] / stats["total_leaf_tasks"]
        if stats["total_leaf_tasks"] > 0
        else 0
    )

    logger.info(
        f"Trade type enrichment complete: {stats['enriched_tasks']}/{stats['total_leaf_tasks']} "
        f"tasks ({enrichment_rate:.1%})"
    )

    if stats["unmatched_tasks"] > 0:
        logger.warning(f"Unmatched tasks: {stats['unmatched_tasks']}")

    if stats["validation_issues"] > 0:
        logger.warning(f"Validation issues: {stats['validation_issues']}")

    return {
        "project": project_name,
        "enrichment_stats": stats,
        "enrichment_rate": enrichment_rate,
    }


def build_classification_lookup(classifications: List[Dict]) -> Dict[tuple, Dict]:
    """
    Build lookup dictionary for classifications.

    Args:
        classifications: List of classification dictionaries

    Returns:
        Dictionary keyed by (activity_name, context_type)
    """
    lookup = {}
    for classification in classifications:
        activity_name = classification.get("activity_name")
        context_type = classification.get("context_type")

        if activity_name and context_type:
            key = (activity_name, context_type)
            lookup[key] = classification

    return lookup


def build_activity_lookup(unique_activities_data: Dict) -> Dict[str, Dict]:
    """
    Build lookup for matching tasks to their activity info.

    Since we need to match each task back to its extracted activity,
    we'll use the extraction logic's grouping to create a reverse lookup.

    However, since extract_unique_activities groups tasks, we need to
    recreate the extraction logic for individual tasks.

    Args:
        unique_activities_data: Output from extract_unique_activities

    Returns:
        Dictionary mapping task WBS to activity info
    """
    # This is actually not feasible without re-running extraction
    # We need to run extraction logic during mapping
    # For now, return empty dict - we'll handle this differently
    return {}


def enrich_tasks_with_trade_types(
    tasks: List[Dict],
    classification_result: Dict,
    project_name: str
) -> Dict:
    """
    Enrich tasks with trade type classifications.

    This function combines extraction and mapping logic to avoid
    needing to store intermediate extraction results.

    Args:
        tasks: List of task dictionaries (will be modified in-place)
        classification_result: Output from classify_activities_with_llm
        project_name: Name of the project

    Returns:
        Dictionary with enrichment statistics
    """
    # Import here to avoid circular dependency
    from .trade_type_extractor import (
        build_tasks_by_wbs,
        is_spatial_leaf,
        extract_activity_from_parent,
        determine_context_type,
    )

    logger.info(f"Enriching tasks with trade types for project: {project_name}")

    # Build classification lookup
    classification_lookup = build_classification_lookup(
        classification_result["classifications"]
    )

    # Build tasks lookup for parent traversal
    tasks_by_wbs = build_tasks_by_wbs(tasks)

    # Track statistics
    stats = {
        "total_leaf_tasks": 0,
        "enriched_tasks": 0,
        "unmatched_tasks": 0,
        "validation_issues": 0,
        "by_context": {
            "tower": 0,
            "common_area": 0,
            "external": 0,
            "infrastructure": 0,
        },
        "by_confidence": {
            "high": 0,
            "medium": 0,
            "low": 0,
        },
    }

    # Process each task
    for task in tasks:
        # Only process leaf tasks
        if task.get("is_summary") or task.get("is_milestone"):
            continue

        if task.get("attributes") is None:
            continue

        stats["total_leaf_tasks"] += 1

        # Extract activity name (same logic as extractor)
        task_name = task.get("name", "")
        if not task_name:
            stats["unmatched_tasks"] += 1
            continue

        if is_spatial_leaf(task_name):
            activity_name, parent_chain = extract_activity_from_parent(task, tasks_by_wbs)
        else:
            activity_name = task_name
            # Still get parent chain for context
            parent_chain = []
            current_wbs = task.get("parent_wbs")
            depth = 5
            while current_wbs and depth > 0:
                parent = tasks_by_wbs.get(current_wbs)
                if parent:
                    parent_chain.append(parent.get("name", ""))
                    current_wbs = parent.get("parent_wbs")
                depth -= 1

        # Determine context type
        context_type = determine_context_type(task, parent_chain, tasks_by_wbs)

        # Look up classification
        key = (activity_name, context_type)
        classification = classification_lookup.get(key)

        if not classification:
            # No classification found
            stats["unmatched_tasks"] += 1
            logger.debug(
                f"No classification found for activity '{activity_name}' "
                f"with context '{context_type}' (task: {task.get('wbs')})"
            )
            continue

        # Enrich task attributes
        task["attributes"]["trade_type"] = classification.get("trade_type")
        task["attributes"]["sub_category"] = classification.get("sub_category")
        task["attributes"]["main_category"] = classification.get("main_category")

        # Note: classification_confidence and classification_reasoning are logged but not stored in output
        # to comply with task_schema.json

        stats["enriched_tasks"] += 1
        stats["by_context"][context_type] += 1
        stats["by_confidence"][classification.get("confidence", "unknown")] += 1

        if classification.get("validation_status") != "valid":
            stats["validation_issues"] += 1

    # Calculate enrichment rate
    enrichment_rate = (
        stats["enriched_tasks"] / stats["total_leaf_tasks"]
        if stats["total_leaf_tasks"] > 0
        else 0
    )

    logger.info(
        f"Trade type enrichment complete: {stats['enriched_tasks']}/{stats['total_leaf_tasks']} "
        f"tasks ({enrichment_rate:.1%})"
    )

    if stats["unmatched_tasks"] > 0:
        logger.warning(
            f"Unmatched tasks: {stats['unmatched_tasks']} "
            f"({stats['unmatched_tasks']/stats['total_leaf_tasks']:.1%})"
        )

    if stats["validation_issues"] > 0:
        logger.warning(
            f"Validation issues: {stats['validation_issues']} classifications"
        )

    return {
        "project": project_name,
        "enrichment_stats": stats,
        "enrichment_rate": enrichment_rate,
    }


def get_enrichment_summary(enrichment_result: Dict) -> str:
    """
    Generate human-readable summary of enrichment results.

    Args:
        enrichment_result: Output from enrich_tasks_with_trade_types

    Returns:
        Formatted summary string
    """
    project = enrichment_result["project"]
    stats = enrichment_result["enrichment_stats"]
    rate = enrichment_result["enrichment_rate"]

    summary_lines = [
        f"Trade Type Enrichment Summary for {project}",
        f"Enrichment rate: {rate:.1%} ({stats['enriched_tasks']}/{stats['total_leaf_tasks']} tasks)",
        "",
        "By Context:",
    ]

    for context, count in stats["by_context"].items():
        if count > 0:
            summary_lines.append(f"  {context}: {count} tasks")

    summary_lines.append("")
    summary_lines.append("By Confidence:")

    for confidence, count in stats["by_confidence"].items():
        if count > 0:
            summary_lines.append(f"  {confidence}: {count} tasks")

    if stats["unmatched_tasks"] > 0:
        summary_lines.append("")
        summary_lines.append(f"⚠ Unmatched tasks: {stats['unmatched_tasks']}")

    if stats["validation_issues"] > 0:
        summary_lines.append(f"⚠ Validation issues: {stats['validation_issues']}")

    return "\n".join(summary_lines)
