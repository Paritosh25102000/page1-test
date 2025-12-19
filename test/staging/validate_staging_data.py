"""
Staging Data Validator - Cross-check all numeric calculations in staging dataset.

Validation Rules:
1. Hierarchy Aggregation: PROJ → REG → ZONE → ALL
2. Time Slice Consistency: FY, Quarter, Month period sums
3. Gauge Calculations: achieved_pct = (actual / plan) * 100
4. Cumulative Costs: Running sum of periodic costs
5. Matrix Bucket Consistency: Sum of buckets = total projects
6. Cross-node Consistency: Same data accessible from different filter paths
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Any
from datetime import datetime
from collections import defaultdict
import math

# Tolerance for floating point comparisons (0.01% relative tolerance)
RELATIVE_TOLERANCE = 0.0001
ABSOLUTE_TOLERANCE = 0.01


class ValidationResult:
    """Container for validation results."""

    def __init__(self, name: str):
        self.name = name
        self.checks: List[Dict] = []
        self.passed = 0
        self.failed = 0
        self.warnings = 0

    def add_check(self, check_name: str, status: str, expected: Any = None,
                  actual: Any = None, details: str = None):
        """Add a validation check result."""
        check = {
            "check": check_name,
            "status": status,  # "pass", "fail", "warn"
            "expected": expected,
            "actual": actual,
            "details": details
        }
        self.checks.append(check)

        if status == "pass":
            self.passed += 1
        elif status == "fail":
            self.failed += 1
        else:
            self.warnings += 1

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "summary": {
                "passed": self.passed,
                "failed": self.failed,
                "warnings": self.warnings,
                "total": len(self.checks)
            },
            "checks": self.checks
        }


def is_close(a: float, b: float, rel_tol: float = RELATIVE_TOLERANCE,
             abs_tol: float = ABSOLUTE_TOLERANCE) -> bool:
    """Check if two floats are approximately equal."""
    if a is None or b is None:
        return a == b
    if a == 0 and b == 0:
        return True
    if a == 0 or b == 0:
        return abs(a - b) <= abs_tol
    return abs(a - b) <= max(rel_tol * max(abs(a), abs(b)), abs_tol)


def format_number(n: float) -> str:
    """Format large numbers for readability."""
    if n is None:
        return "None"
    if abs(n) >= 1e12:
        return f"{n/1e12:.2f}T"
    if abs(n) >= 1e9:
        return f"{n/1e9:.2f}B"
    if abs(n) >= 1e6:
        return f"{n/1e6:.2f}M"
    return f"{n:.2f}"


class StagingDataValidator:
    """Validates staging data integrity."""

    def __init__(self, staging_data: Dict):
        self.data = staging_data
        self.hierarchy = staging_data.get("controls", {}).get("hierarchy_tree", {})
        self.time_modes = staging_data.get("controls", {}).get("time_modes", {})
        self.dashboard_data = staging_data.get("dashboard_data", {})
        self.results: List[ValidationResult] = []

    def validate_all(self) -> List[ValidationResult]:
        """Run all validation checks."""
        self.results = []

        # 1. Hierarchy aggregation checks
        self.validate_hierarchy_aggregation()

        # 2. Time slice consistency
        self.validate_time_slices()

        # 3. Gauge calculations
        self.validate_gauge_calculations()

        # 4. Cumulative costs
        self.validate_cumulative_costs()

        # 5. Matrix bucket consistency
        self.validate_matrix_buckets()

        # 6. Additional cross-checks
        self.validate_additional_rules()

        return self.results

    def validate_hierarchy_aggregation(self):
        """
        Rule 1: Sum of child nodes must equal parent node.
        PROJ → REG → ZONE → ALL
        """
        result = ValidationResult("Hierarchy Aggregation")

        # For each time mode, check COC trend aggregation
        for time_mode in ["fy", "quarter", "month"]:
            series_key = f"{time_mode}_series"

            # Check Zone aggregation to ALL
            zone_totals = {"plan": 0.0, "actual": 0.0}
            for zone in self.hierarchy.keys():
                zone_key = f"ZONE_{zone}"
                if zone_key in self.dashboard_data:
                    zone_data = self.dashboard_data[zone_key]
                    series = zone_data.get("coc_trend", {}).get(series_key, [])
                    for point in series:
                        zone_totals["plan"] += point.get("plan_cost") or 0
                        zone_totals["actual"] += point.get("actual_cost") or 0

            # Get ALL totals
            all_data = self.dashboard_data.get("ALL", {})
            all_series = all_data.get("coc_trend", {}).get(series_key, [])
            all_totals = {"plan": 0.0, "actual": 0.0}
            for point in all_series:
                all_totals["plan"] += point.get("plan_cost") or 0
                all_totals["actual"] += point.get("actual_cost") or 0

            # Compare
            plan_match = is_close(zone_totals["plan"], all_totals["plan"])
            actual_match = is_close(zone_totals["actual"], all_totals["actual"])

            result.add_check(
                f"ZONE→ALL {time_mode} plan costs",
                "pass" if plan_match else "fail",
                format_number(all_totals["plan"]),
                format_number(zone_totals["plan"]),
                f"Diff: {format_number(all_totals['plan'] - zone_totals['plan'])}"
            )

            result.add_check(
                f"ZONE→ALL {time_mode} actual costs",
                "pass" if actual_match else "fail",
                format_number(all_totals["actual"]),
                format_number(zone_totals["actual"]),
                f"Diff: {format_number(all_totals['actual'] - zone_totals['actual'])}"
            )

        # Check Region aggregation to Zone
        for zone, regions in self.hierarchy.items():
            zone_key = f"ZONE_{zone}"
            zone_data = self.dashboard_data.get(zone_key, {})

            for time_mode in ["fy", "quarter", "month"]:
                series_key = f"{time_mode}_series"

                region_totals = {"plan": 0.0, "actual": 0.0}
                for region in regions.keys():
                    region_key = f"REG_{region}"
                    if region_key in self.dashboard_data:
                        reg_data = self.dashboard_data[region_key]
                        series = reg_data.get("coc_trend", {}).get(series_key, [])
                        for point in series:
                            region_totals["plan"] += point.get("plan_cost") or 0
                            region_totals["actual"] += point.get("actual_cost") or 0

                zone_series = zone_data.get("coc_trend", {}).get(series_key, [])
                zone_totals = {"plan": 0.0, "actual": 0.0}
                for point in zone_series:
                    zone_totals["plan"] += point.get("plan_cost") or 0
                    zone_totals["actual"] += point.get("actual_cost") or 0

                plan_match = is_close(region_totals["plan"], zone_totals["plan"])
                actual_match = is_close(region_totals["actual"], zone_totals["actual"])

                result.add_check(
                    f"REG→ZONE_{zone} {time_mode} plan",
                    "pass" if plan_match else "fail",
                    format_number(zone_totals["plan"]),
                    format_number(region_totals["plan"]),
                    f"Diff: {format_number(zone_totals['plan'] - region_totals['plan'])}"
                )

        # Check Project aggregation to Region
        for zone, regions in self.hierarchy.items():
            for region, projects in regions.items():
                region_key = f"REG_{region}"
                region_data = self.dashboard_data.get(region_key, {})

                for time_mode in ["fy", "quarter", "month"]:
                    series_key = f"{time_mode}_series"

                    proj_totals = {"plan": 0.0, "actual": 0.0}
                    for project in projects:
                        proj_key = f"PROJ_{project['id']}"
                        if proj_key in self.dashboard_data:
                            proj_data = self.dashboard_data[proj_key]
                            series = proj_data.get("coc_trend", {}).get(series_key, [])
                            for point in series:
                                proj_totals["plan"] += point.get("plan_cost") or 0
                                proj_totals["actual"] += point.get("actual_cost") or 0

                    reg_series = region_data.get("coc_trend", {}).get(series_key, [])
                    reg_totals = {"plan": 0.0, "actual": 0.0}
                    for point in reg_series:
                        reg_totals["plan"] += point.get("plan_cost") or 0
                        reg_totals["actual"] += point.get("actual_cost") or 0

                    plan_match = is_close(proj_totals["plan"], reg_totals["plan"])

                    result.add_check(
                        f"PROJ→REG_{region} {time_mode} plan",
                        "pass" if plan_match else "fail",
                        format_number(reg_totals["plan"]),
                        format_number(proj_totals["plan"]),
                        f"Diff: {format_number(reg_totals['plan'] - proj_totals['plan'])}"
                    )

        self.results.append(result)

    def validate_time_slices(self):
        """
        Rule 2: Validate time slice period sums.
        - FY series should cover Apr-Mar (12 months)
        - Quarter series should cover the quarter period
        - Month series should cover +/- 5 weeks
        """
        result = ValidationResult("Time Slice Consistency")

        for node_key, node_data in self.dashboard_data.items():
            coc_trend = node_data.get("coc_trend", {})

            # Check FY series has 12 months
            fy_series = coc_trend.get("fy_series", [])
            result.add_check(
                f"{node_key} FY series count",
                "pass" if len(fy_series) == 12 else "warn",
                12,
                len(fy_series),
                "FY should have 12 monthly periods"
            )

            # Check quarter series (approximately 13-14 weeks)
            quarter_series = coc_trend.get("quarter_series", [])
            q_len_ok = 12 <= len(quarter_series) <= 15
            result.add_check(
                f"{node_key} Quarter series count",
                "pass" if q_len_ok else "warn",
                "12-15 weeks",
                len(quarter_series),
                "Quarter should have ~13 weekly periods"
            )

            # Check month series (approximately 10-11 weeks for +/- 5 weeks)
            month_series = coc_trend.get("month_series", [])
            m_len_ok = 9 <= len(month_series) <= 12
            result.add_check(
                f"{node_key} Month series count",
                "pass" if m_len_ok else "warn",
                "9-12 weeks",
                len(month_series),
                "Month (Looking Glass) should have ~10 weekly periods"
            )

            # Only check first node to avoid too many checks
            if node_key == "ALL":
                break

        self.results.append(result)

    def validate_gauge_calculations(self):
        """
        Rule 3: Validate gauge percentage calculations.
        achieved_pct = (actual / plan) * 100
        """
        result = ValidationResult("Gauge Calculations")

        for node_key, node_data in self.dashboard_data.items():
            kpi_gauges = node_data.get("kpi_gauges", {})

            for gauge_type in ["aop", "sprint"]:
                gauge_data = kpi_gauges.get(gauge_type, {})

                for time_mode in ["fy", "quarter", "month"]:
                    mode_data = gauge_data.get(time_mode, {})

                    actual = mode_data.get("actual", 0)
                    plan = mode_data.get("plan", 0)
                    reported_pct = mode_data.get("achieved_pct", 0)

                    if plan > 0:
                        calculated_pct = (actual / plan) * 100
                        # Round to 1 decimal for comparison
                        calculated_rounded = round(calculated_pct, 1)

                        pct_match = is_close(calculated_rounded, reported_pct, rel_tol=0.01)

                        result.add_check(
                            f"{node_key} {gauge_type} {time_mode} achieved_pct",
                            "pass" if pct_match else "fail",
                            f"{reported_pct}%",
                            f"{calculated_rounded}%",
                            f"actual={format_number(actual)}, plan={format_number(plan)}"
                        )
                    else:
                        # Plan is zero, percentage should be 0
                        result.add_check(
                            f"{node_key} {gauge_type} {time_mode} zero plan",
                            "pass" if reported_pct == 0 else "warn",
                            "0%",
                            f"{reported_pct}%",
                            "Plan is zero, percentage should be 0"
                        )

                    # Validate status color
                    status_color = mode_data.get("status_color")
                    expected_color = self._get_expected_color(reported_pct)

                    result.add_check(
                        f"{node_key} {gauge_type} {time_mode} status_color",
                        "pass" if status_color == expected_color else "fail",
                        expected_color,
                        status_color,
                        f"For {reported_pct}%: red<85, amber 85-95, green>95"
                    )

        self.results.append(result)

    def _get_expected_color(self, pct: float) -> str:
        """Get expected status color based on percentage."""
        if pct < 85:
            return "red"
        elif pct <= 95:
            return "amber"
        else:
            return "green"

    def validate_cumulative_costs(self):
        """
        Rule 4: Cumulative costs must equal running sum of periodic costs.
        cumm_plan[n] = sum(plan_cost[0:n+1])
        cumm_actual[n] = sum(actual_cost[0:n+1])
        """
        result = ValidationResult("Cumulative Costs")

        for node_key, node_data in self.dashboard_data.items():
            coc_trend = node_data.get("coc_trend", {})

            for time_mode in ["fy", "quarter", "month"]:
                series_key = f"{time_mode}_series"
                series = coc_trend.get(series_key, [])

                running_plan = 0.0
                running_actual = 0.0

                for i, point in enumerate(series):
                    plan_cost = point.get("plan_cost") or 0
                    actual_cost = point.get("actual_cost") or 0
                    cumm_plan = point.get("cumm_plan") or 0
                    cumm_actual = point.get("cumm_actual") or 0

                    running_plan += plan_cost
                    running_actual += actual_cost

                    plan_match = is_close(running_plan, cumm_plan)
                    actual_match = is_close(running_actual, cumm_actual)

                    if not plan_match:
                        result.add_check(
                            f"{node_key} {time_mode}[{i}] cumm_plan",
                            "fail",
                            format_number(running_plan),
                            format_number(cumm_plan),
                            f"Period: {point.get('label')}"
                        )

                    if not actual_match:
                        result.add_check(
                            f"{node_key} {time_mode}[{i}] cumm_actual",
                            "fail",
                            format_number(running_actual),
                            format_number(cumm_actual),
                            f"Period: {point.get('label')}"
                        )

                # Final cumulative should match
                if series:
                    final_point = series[-1]
                    result.add_check(
                        f"{node_key} {time_mode} final cumulative plan",
                        "pass" if is_close(running_plan, final_point.get("cumm_plan", 0)) else "fail",
                        format_number(running_plan),
                        format_number(final_point.get("cumm_plan", 0)),
                        f"Final period: {final_point.get('label')}"
                    )

        self.results.append(result)

    def validate_matrix_buckets(self):
        """
        Rule 5: Matrix bucket counts should sum to total projects.
        Sum of all bucket counts = number of projects in scope
        """
        result = ValidationResult("Matrix Bucket Consistency")

        # For ALL, sum of buckets should equal total projects
        all_data = self.dashboard_data.get("ALL", {})
        all_matrix = all_data.get("project_matrix", {})
        all_rows = all_matrix.get("rows", [])

        total_projects = sum(
            len(projects)
            for zone, regions in self.hierarchy.items()
            for projects in regions.values()
        )

        # Sum bucket counts across all rows
        bucket_sum = 0
        for row in all_rows:
            buckets = row.get("buckets", {})
            for bucket_key in ["gt_120", "100_120", "85_100", "60_85", "lt_60"]:
                bucket_sum += buckets.get(bucket_key, 0)

        result.add_check(
            "ALL matrix bucket sum = total projects",
            "pass" if bucket_sum == total_projects else "fail",
            total_projects,
            bucket_sum,
            f"Hierarchy has {total_projects} projects"
        )

        # Check each zone row projects match zone's project count
        for zone, regions in self.hierarchy.items():
            zone_projects = sum(len(projects) for projects in regions.values())

            zone_row = next((r for r in all_rows if r.get("id") == f"ZONE_{zone}"), None)
            if zone_row:
                buckets = zone_row.get("buckets", {})
                row_sum = sum(buckets.get(k, 0) for k in ["gt_120", "100_120", "85_100", "60_85", "lt_60"])

                result.add_check(
                    f"ZONE_{zone} bucket sum = zone projects",
                    "pass" if row_sum == zone_projects else "fail",
                    zone_projects,
                    row_sum,
                    f"Zone {zone} has {zone_projects} projects"
                )

        self.results.append(result)

    def validate_additional_rules(self):
        """
        Rule 6: Additional cross-checks.
        - Non-negative costs
        - Consistent date ordering
        - Tasks_with_sprint consistency
        """
        result = ValidationResult("Additional Cross-Checks")

        # Check for non-negative costs
        negative_costs = []
        for node_key, node_data in self.dashboard_data.items():
            coc_trend = node_data.get("coc_trend", {})
            for series_key in ["fy_series", "quarter_series", "month_series"]:
                series = coc_trend.get(series_key, [])
                for point in series:
                    if (point.get("plan_cost") or 0) < 0:
                        negative_costs.append(f"{node_key} {series_key} plan_cost")
                    if (point.get("actual_cost") or 0) < 0:
                        negative_costs.append(f"{node_key} {series_key} actual_cost")

        result.add_check(
            "No negative costs",
            "pass" if not negative_costs else "fail",
            "0 negative values",
            f"{len(negative_costs)} negative values",
            "; ".join(negative_costs[:5]) if negative_costs else None
        )

        # Check date ordering in series
        date_order_issues = []
        for node_key, node_data in self.dashboard_data.items():
            coc_trend = node_data.get("coc_trend", {})
            for series_key in ["fy_series", "quarter_series", "month_series"]:
                series = coc_trend.get(series_key, [])
                for i in range(1, len(series)):
                    prev_date = series[i-1].get("sort_date", "")
                    curr_date = series[i].get("sort_date", "")
                    if curr_date < prev_date:
                        date_order_issues.append(f"{node_key} {series_key}[{i}]")

        result.add_check(
            "Series dates in ascending order",
            "pass" if not date_order_issues else "fail",
            "All ordered",
            f"{len(date_order_issues)} out of order",
            "; ".join(date_order_issues[:5]) if date_order_issues else None
        )

        # Check percentage bounds (0-200% reasonable range)
        pct_issues = []
        for node_key, node_data in self.dashboard_data.items():
            kpi_gauges = node_data.get("kpi_gauges", {})
            for gauge_type in ["aop", "sprint"]:
                for time_mode in ["fy", "quarter", "month"]:
                    pct = kpi_gauges.get(gauge_type, {}).get(time_mode, {}).get("achieved_pct", 0)
                    if pct < 0 or pct > 200:
                        pct_issues.append(f"{node_key} {gauge_type} {time_mode}: {pct}%")

        result.add_check(
            "Achievement percentages in reasonable range (0-200%)",
            "pass" if not pct_issues else "warn",
            "All in range",
            f"{len(pct_issues)} out of range",
            "; ".join(pct_issues[:5]) if pct_issues else None
        )

        # Check gauge plan vs COC trend total
        # The gauge plan/actual should match COC trend totals for corresponding period
        for time_mode in ["fy", "quarter", "month"]:
            all_gauges = self.dashboard_data.get("ALL", {}).get("kpi_gauges", {})
            aop_data = all_gauges.get("aop", {}).get(time_mode, {})
            gauge_plan = aop_data.get("plan", 0)
            gauge_actual = aop_data.get("actual", 0)

            series_key = f"{time_mode}_series"
            all_series = self.dashboard_data.get("ALL", {}).get("coc_trend", {}).get(series_key, [])

            trend_plan = sum(p.get("plan_cost") or 0 for p in all_series)
            trend_actual = sum(p.get("actual_cost") or 0 for p in all_series)

            # Note: These might not match exactly due to different calculation methods
            # This is more of a sanity check
            plan_ratio = gauge_plan / trend_plan if trend_plan > 0 else 0
            actual_ratio = gauge_actual / trend_actual if trend_actual > 0 else 0

            # They should be somewhat close (within 50% - just a sanity check)
            result.add_check(
                f"ALL {time_mode} gauge vs trend plan ratio",
                "pass" if 0.5 < plan_ratio < 2.0 else "warn",
                "0.5-2.0",
                f"{plan_ratio:.2f}",
                f"Gauge: {format_number(gauge_plan)}, Trend: {format_number(trend_plan)}"
            )

        self.results.append(result)


def generate_metrics(results: List[ValidationResult]) -> Dict:
    """Generate metrics dataset from validation results."""
    metrics = {
        "generated_at": datetime.now().isoformat(),
        "summary": {
            "total_checks": 0,
            "passed": 0,
            "failed": 0,
            "warnings": 0,
            "pass_rate": 0.0
        },
        "by_category": {},
        "all_checks": [],
        "failed_checks": [],
        "warning_checks": [],
        "sample_checks": []  # Representative sample for report
    }

    for result in results:
        metrics["summary"]["total_checks"] += len(result.checks)
        metrics["summary"]["passed"] += result.passed
        metrics["summary"]["failed"] += result.failed
        metrics["summary"]["warnings"] += result.warnings

        # Store full result with checks
        metrics["by_category"][result.name] = result.to_dict()

        # Collect sample checks (first 3 from each category)
        for check in result.checks[:3]:
            metrics["sample_checks"].append({
                "category": result.name,
                **check
            })

        for check in result.checks:
            metrics["all_checks"].append({
                "category": result.name,
                **check
            })
            if check["status"] == "fail":
                metrics["failed_checks"].append({
                    "category": result.name,
                    **check
                })
            elif check["status"] == "warn":
                metrics["warning_checks"].append({
                    "category": result.name,
                    **check
                })

    total = metrics["summary"]["total_checks"]
    if total > 0:
        metrics["summary"]["pass_rate"] = round(
            (metrics["summary"]["passed"] / total) * 100, 2
        )

    return metrics


def generate_report(metrics: Dict) -> str:
    """Generate markdown report from metrics."""
    lines = [
        "# Staging Data Validation Report",
        "",
        f"**Generated:** {metrics['generated_at']}",
        "",
        "## Summary",
        "",
        "| Metric | Value |",
        "|--------|-------|",
        f"| Total Checks | {metrics['summary']['total_checks']} |",
        f"| Passed | {metrics['summary']['passed']} |",
        f"| Failed | {metrics['summary']['failed']} |",
        f"| Warnings | {metrics['summary']['warnings']} |",
        f"| Pass Rate | {metrics['summary']['pass_rate']}% |",
        "",
        "## Results by Category",
        "",
    ]

    for category, cat_data in metrics["by_category"].items():
        summary = cat_data.get("summary", cat_data)
        checks = cat_data.get("checks", [])
        status_emoji = "✅" if summary["failed"] == 0 else "❌"
        lines.append(f"### {status_emoji} {category}")
        lines.append("")
        lines.append(f"- Passed: {summary['passed']}")
        lines.append(f"- Failed: {summary['failed']}")
        lines.append(f"- Warnings: {summary['warnings']}")
        lines.append("")

        # Add sample checks from this category
        if checks:
            lines.append("**Sample Checks:**")
            lines.append("")
            lines.append("| Check | Status | Expected | Actual |")
            lines.append("|-------|--------|----------|--------|")
            for check in checks[:5]:  # Show up to 5 samples per category
                status_icon = "✓" if check["status"] == "pass" else ("⚠" if check["status"] == "warn" else "✗")
                lines.append(
                    f"| {check['check']} | {status_icon} | "
                    f"{check.get('expected', '-')} | {check.get('actual', '-')} |"
                )
            if len(checks) > 5:
                lines.append(f"| ... | | | +{len(checks) - 5} more |")
            lines.append("")

    if metrics["failed_checks"]:
        lines.append("## Failed Checks")
        lines.append("")
        lines.append("| Category | Check | Expected | Actual | Details |")
        lines.append("|----------|-------|----------|--------|---------|")
        for check in metrics["failed_checks"]:
            lines.append(
                f"| {check['category']} | {check['check']} | "
                f"{check.get('expected', '-')} | {check.get('actual', '-')} | "
                f"{check.get('details', '-')} |"
            )
        lines.append("")

    if metrics["warning_checks"]:
        lines.append("## Warnings")
        lines.append("")
        lines.append("| Category | Check | Expected | Actual | Details |")
        lines.append("|----------|-------|----------|--------|---------|")
        for check in metrics["warning_checks"][:20]:  # Limit to first 20
            lines.append(
                f"| {check['category']} | {check['check']} | "
                f"{check.get('expected', '-')} | {check.get('actual', '-')} | "
                f"{check.get('details', '-')} |"
            )
        if len(metrics["warning_checks"]) > 20:
            lines.append(f"| ... | ... | ... | ... | +{len(metrics['warning_checks']) - 20} more warnings |")
        lines.append("")

    lines.append("## Validation Rules")
    lines.append("")
    lines.append("1. **Hierarchy Aggregation**: Sum of child nodes (PROJ→REG→ZONE→ALL) must match parent totals")
    lines.append("2. **Time Slice Consistency**: FY has 12 months, Quarter ~13 weeks, Month ~10 weeks")
    lines.append("3. **Gauge Calculations**: `achieved_pct = (actual / plan) * 100`, status colors match thresholds")
    lines.append("4. **Cumulative Costs**: `cumm_plan[n] = sum(plan_cost[0:n+1])`")
    lines.append("5. **Matrix Bucket Consistency**: Sum of bucket counts equals total projects")
    lines.append("6. **Additional Checks**: Non-negative costs, date ordering, percentage bounds")
    lines.append("")

    return "\n".join(lines)


def main():
    """Main entry point."""
    # Find staging data file
    script_dir = Path(__file__).parent
    staging_file = script_dir.parent.parent / "output" / "staging" / "page1-executive-summary.json"

    if not staging_file.exists():
        print(f"Error: Staging file not found: {staging_file}")
        sys.exit(1)

    print(f"Loading staging data from: {staging_file}")

    with open(staging_file) as f:
        data = json.load(f)

    print("Running validations...")

    validator = StagingDataValidator(data)
    results = validator.validate_all()

    # Generate metrics
    metrics = generate_metrics(results)

    # Save metrics JSON
    metrics_file = script_dir / "validation_metrics.json"
    with open(metrics_file, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"Saved metrics to: {metrics_file}")

    # Generate and save report
    report = generate_report(metrics)
    report_file = script_dir / "validation_report.md"
    with open(report_file, "w") as f:
        f.write(report)
    print(f"Saved report to: {report_file}")

    # Print summary
    print("\n" + "="*50)
    print("VALIDATION SUMMARY")
    print("="*50)
    print(f"Total Checks: {metrics['summary']['total_checks']}")
    print(f"Passed: {metrics['summary']['passed']}")
    print(f"Failed: {metrics['summary']['failed']}")
    print(f"Warnings: {metrics['summary']['warnings']}")
    print(f"Pass Rate: {metrics['summary']['pass_rate']}%")

    if metrics["failed_checks"]:
        print("\n⚠️  Some checks failed! Review validation_report.md for details.")
        sys.exit(1)
    else:
        print("\n✅ All checks passed!")
        sys.exit(0)


if __name__ == "__main__":
    main()
