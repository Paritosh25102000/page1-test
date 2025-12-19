"""
Validators - Output validation for staging data
"""

from typing import Dict, List, Optional
import logging


def validate_staging_output(data: Dict, page: str) -> List[str]:
    """
    Validate staging output structure and data integrity.

    Args:
        data: Generated staging data
        page: Page identifier

    Returns:
        List of validation errors (empty if valid)
    """
    logger = logging.getLogger(__name__)
    errors = []

    # Check top-level structure
    required_keys = ["meta", "controls", "dashboard_data"]
    for key in required_keys:
        if key not in data:
            errors.append(f"Missing required key: {key}")

    if errors:
        return errors

    # Validate meta
    meta_errors = validate_meta(data["meta"])
    errors.extend(meta_errors)

    # Validate controls
    controls_errors = validate_controls(data["controls"])
    errors.extend(controls_errors)

    # Validate dashboard_data
    dashboard_errors = validate_dashboard_data(data["dashboard_data"])
    errors.extend(dashboard_errors)

    if errors:
        logger.warning(f"Validation completed with {len(errors)} errors")
    else:
        logger.info("Validation passed")

    return errors


def validate_meta(meta: Dict) -> List[str]:
    """Validate meta object."""
    errors = []
    required = ["generated_at", "data_version", "currency_unit"]

    for field in required:
        if field not in meta:
            errors.append(f"Missing meta field: {field}")

    return errors


def validate_controls(controls: Dict) -> List[str]:
    """Validate controls object."""
    errors = []

    if "hierarchy_tree" not in controls:
        errors.append("Missing hierarchy_tree in controls")

    if "time_modes" not in controls:
        errors.append("Missing time_modes in controls")
    else:
        time_modes = controls["time_modes"]
        for mode in ["fy", "quarter", "month"]:
            if mode not in time_modes:
                errors.append(f"Missing time mode: {mode}")

    return errors


def validate_dashboard_data(dashboard_data: Dict) -> List[str]:
    """Validate dashboard_data structure."""
    errors = []

    if not dashboard_data:
        errors.append("dashboard_data is empty")
        return errors

    # Check that ALL key exists
    if "ALL" not in dashboard_data:
        errors.append("Missing 'ALL' filter key in dashboard_data")

    # Validate each node
    for key, node_data in dashboard_data.items():
        node_errors = validate_node_data(key, node_data)
        errors.extend(node_errors)

    return errors


def validate_node_data(key: str, node_data: Dict) -> List[str]:
    """Validate a single node's data."""
    errors = []

    required_widgets = ["kpi_gauges", "coc_trend", "project_matrix"]
    for widget in required_widgets:
        if widget not in node_data:
            errors.append(f"{key}: Missing widget {widget}")

    # Validate KPI gauges
    if "kpi_gauges" in node_data:
        kpi_errors = validate_kpi_gauges(key, node_data["kpi_gauges"])
        errors.extend(kpi_errors)

    # Validate COC trend
    if "coc_trend" in node_data:
        trend_errors = validate_coc_trend(key, node_data["coc_trend"])
        errors.extend(trend_errors)

    # Validate project matrix
    if "project_matrix" in node_data:
        matrix_errors = validate_project_matrix(key, node_data["project_matrix"])
        errors.extend(matrix_errors)

    return errors


def validate_kpi_gauges(key: str, kpi_gauges: Dict) -> List[str]:
    """Validate KPI gauges structure with time-mode support."""
    errors = []

    for gauge_type in ["aop", "sprint"]:
        if gauge_type not in kpi_gauges:
            errors.append(f"{key}: Missing {gauge_type} gauge")
            continue

        gauge = kpi_gauges[gauge_type]

        # Check for time-mode structure
        for time_mode in ["fy", "quarter", "month"]:
            if time_mode not in gauge:
                errors.append(f"{key}: {gauge_type} missing time mode {time_mode}")
                continue

            mode_data = gauge[time_mode]
            required = ["achieved_pct", "status_color", "actual", "plan", "tasks_with_sprint"]

            for field in required:
                if field not in mode_data:
                    errors.append(f"{key}: {gauge_type}.{time_mode} missing field {field}")

            # Validate color
            if "status_color" in mode_data:
                if mode_data["status_color"] not in ["red", "amber", "green"]:
                    errors.append(f"{key}: {gauge_type}.{time_mode} invalid status_color")

    return errors


def validate_coc_trend(key: str, coc_trend: Dict) -> List[str]:
    """Validate COC trend structure."""
    errors = []

    for series_name in ["fy_series", "quarter_series", "month_series"]:
        if series_name not in coc_trend:
            errors.append(f"{key}: Missing {series_name}")
            continue

        series = coc_trend[series_name]
        if not isinstance(series, list):
            errors.append(f"{key}: {series_name} is not a list")

    return errors


def validate_project_matrix(key: str, project_matrix: Dict) -> List[str]:
    """Validate project matrix structure."""
    errors = []

    if "rows" not in project_matrix:
        errors.append(f"{key}: Missing rows in project_matrix")
        return errors

    rows = project_matrix["rows"]
    if not isinstance(rows, list):
        errors.append(f"{key}: rows is not a list")

    return errors
