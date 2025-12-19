"""
Staging Value Lineage Tracer

Traces a staging dashboard value back to its source tasks in the master JSON,
showing all individual values and calculations used to derive the final number.

Usage:
    python trace_staging_value.py --project "Jardinia" --period "Wk 47" --time-mode quarter
    python trace_staging_value.py --project "Horizon" --period "Oct-25" --time-mode fy

Output:
    - CSV file with all contributing tasks and their values
    - MD report with summary and calculation verification
"""

import json
import csv
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class TaskContribution:
    """Represents a single task's contribution to a period."""
    task_uid: str
    task_name: str
    tower: str
    floor: str
    main_category: str
    sub_category: str
    trade_type: str
    aop_start: str
    aop_finish: str
    sprint_start: str
    sprint_finish: str
    actual_start: str
    actual_end: str
    week_start: str
    week_end: str
    plan_cost: float
    actual_cost: float
    plan_hours: float
    actual_hours: float


class StagingValueTracer:
    """Traces staging values back to source tasks."""

    def __init__(self, project_json_dir: str, staging_file: str):
        self.project_json_dir = Path(project_json_dir)
        self.staging_file = Path(staging_file)
        self.staging_data = None
        self.project_data = None

    def load_staging(self):
        """Load staging data."""
        with open(self.staging_file) as f:
            self.staging_data = json.load(f)

    def load_project(self, project_name: str):
        """Load project's master JSON."""
        project_file = self.project_json_dir / f"{project_name}.json"
        if not project_file.exists():
            raise FileNotFoundError(f"Project file not found: {project_file}")

        with open(project_file) as f:
            self.project_data = json.load(f)

    def get_staging_value(self, project: str, period: str, time_mode: str) -> Tuple[float, float, str]:
        """
        Get the staging value for a project/period/time-mode combination.

        Returns:
            (plan_cost, actual_cost, sort_date)
        """
        project_key = f"PROJ_{project}"
        if project_key not in self.staging_data['dashboard_data']:
            raise ValueError(f"Project not found in staging: {project}")

        proj_data = self.staging_data['dashboard_data'][project_key]
        series_key = f"{time_mode}_series"
        series = proj_data.get('coc_trend', {}).get(series_key, [])

        for point in series:
            if point['label'] == period:
                return point['plan_cost'], point['actual_cost'], point['sort_date']

        raise ValueError(f"Period '{period}' not found in {time_mode} series")

    def get_week_start_for_period(self, sort_date: str, time_mode: str) -> str:
        """
        Get the week_start date to match in master JSON.

        For FY (monthly), we need to find all weeks that fall within that month.
        For Quarter/Month (weekly), the sort_date IS the week_start.
        """
        return sort_date

    def trace_contributions(
        self,
        project: str,
        period: str,
        time_mode: str
    ) -> Tuple[List[TaskContribution], Dict]:
        """
        Trace all task contributions to a staging value.

        Returns:
            (list of TaskContribution, summary dict)
        """
        self.load_staging()
        self.load_project(project)

        # Get staging value
        staging_plan, staging_actual, sort_date = self.get_staging_value(
            project, period, time_mode
        )

        contributions = []
        total_plan = 0.0
        total_actual = 0.0

        # Determine date matching strategy
        if time_mode == 'fy':
            # Monthly - need to find all weeks in that month
            target_month = sort_date[:7]  # YYYY-MM
            date_matcher = lambda ws: ws[:7] == target_month if ws else False
        else:
            # Weekly - exact week_start match
            date_matcher = lambda ws: ws == sort_date if ws else False

        # Scan all tasks
        for task in self.project_data:
            if task.get('is_summary') or task.get('is_milestone'):
                continue

            timeline = task.get('cost_timeline') or {}
            weekly_costs = timeline.get('weekly_costs') or []

            for week in weekly_costs:
                week_start = week.get('week_start')
                if not date_matcher(week_start):
                    continue

                plan_data = week.get('plan') or {}
                actual_data = week.get('actual') or {}
                plan_cost = plan_data.get('cost') or 0
                actual_cost = actual_data.get('cost') or 0

                # Skip if no contribution
                if plan_cost == 0 and actual_cost == 0:
                    continue

                # Get task attributes
                attrs = task.get('attributes') or {}
                dates = task.get('dates') or {}
                # AOP dates are stored in 'plan' (baseline plan dates)
                aop = dates.get('plan') or {}
                sprint = dates.get('sprint') or {}
                actual = dates.get('actual') or {}

                contribution = TaskContribution(
                    task_uid=str(task.get('uid') or ''),
                    task_name=task.get('name') or '',
                    tower=attrs.get('tower') or '',
                    floor=attrs.get('floor') or '',
                    main_category=attrs.get('main_category') or '',
                    sub_category=attrs.get('sub_category') or '',
                    trade_type=attrs.get('trade_type') or '',
                    aop_start=aop.get('start') or '',
                    aop_finish=aop.get('end') or '',
                    sprint_start=sprint.get('start') or '',
                    sprint_finish=sprint.get('end') or '',
                    actual_start=actual.get('start') or '',
                    actual_end=actual.get('end') or '',
                    week_start=week_start or '',
                    week_end=week.get('week_end') or '',
                    plan_cost=plan_cost,
                    actual_cost=actual_cost,
                    plan_hours=plan_data.get('hours') or 0,
                    actual_hours=actual_data.get('hours') or 0
                )

                contributions.append(contribution)
                total_plan += plan_cost
                total_actual += actual_cost

        # Build summary
        summary = {
            'project': project,
            'period': period,
            'time_mode': time_mode,
            'sort_date': sort_date,
            'staging_plan': staging_plan,
            'staging_actual': staging_actual,
            'calculated_plan': total_plan,
            'calculated_actual': total_actual,
            'plan_match': abs(staging_plan - total_plan) < 0.01,
            'actual_match': abs(staging_actual - total_actual) < 0.01,
            'task_count': len(contributions),
            'plan_difference': staging_plan - total_plan,
            'actual_difference': staging_actual - total_actual
        }

        return contributions, summary

    def generate_csv(
        self,
        contributions: List[TaskContribution],
        summary: Dict,
        output_path: Path
    ):
        """Generate CSV file with all contributions."""
        headers = [
            'Row #',
            'Task UID',
            'Task Name',
            'Tower',
            'Floor',
            'Main Category',
            'Sub Category',
            'Trade Type',
            'AOP Start',
            'AOP Finish',
            'Sprint Start',
            'Sprint Finish',
            'Actual Start',
            'Actual End',
            'Week Start',
            'Week End',
            'Plan Cost (INR)',
            'Actual Cost (INR)',
            'Plan Hours',
            'Actual Hours'
        ]

        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)

            # Write header info
            writer.writerow(['# Staging Value Lineage Report'])
            writer.writerow([f'# Project: {summary["project"]}'])
            writer.writerow([f'# Period: {summary["period"]} ({summary["time_mode"].upper()})'])
            writer.writerow([f'# Sort Date: {summary["sort_date"]}'])
            writer.writerow([f'# Generated: {datetime.now().isoformat()}'])
            writer.writerow([])

            # Write data headers
            writer.writerow(headers)

            # Write contributions
            for i, contrib in enumerate(contributions, 1):
                writer.writerow([
                    i,
                    contrib.task_uid,
                    contrib.task_name,
                    contrib.tower,
                    contrib.floor,
                    contrib.main_category,
                    contrib.sub_category,
                    contrib.trade_type,
                    contrib.aop_start,
                    contrib.aop_finish,
                    contrib.sprint_start,
                    contrib.sprint_finish,
                    contrib.actual_start,
                    contrib.actual_end,
                    contrib.week_start,
                    contrib.week_end,
                    f'{contrib.plan_cost:.2f}',
                    f'{contrib.actual_cost:.2f}',
                    f'{contrib.plan_hours:.2f}',
                    f'{contrib.actual_hours:.2f}'
                ])

            # Write totals
            writer.writerow([])
            writer.writerow(['', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 'TOTAL (Calculated):',
                           f'{summary["calculated_plan"]:.2f}',
                           f'{summary["calculated_actual"]:.2f}'])
            writer.writerow(['', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 'Staging Value:',
                           f'{summary["staging_plan"]:.2f}',
                           f'{summary["staging_actual"]:.2f}'])
            writer.writerow(['', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 'Difference:',
                           f'{summary["plan_difference"]:.2f}',
                           f'{summary["actual_difference"]:.2f}'])
            writer.writerow(['', '', '', '', '', '', '', '', '', '', '', '', '', '', '', 'Match:',
                           'YES' if summary["plan_match"] else 'NO',
                           'YES' if summary["actual_match"] else 'NO'])

    def generate_report(
        self,
        contributions: List[TaskContribution],
        summary: Dict,
        output_path: Path
    ):
        """Generate markdown report."""
        def format_inr(value: float) -> str:
            """Format as Indian currency."""
            if abs(value) >= 1e12:
                return f"₹{value/1e12:.2f}T"
            if abs(value) >= 1e9:
                return f"₹{value/1e9:.2f}B"
            if abs(value) >= 1e7:
                return f"₹{value/1e7:.2f}Cr"
            if abs(value) >= 1e5:
                return f"₹{value/1e5:.2f}L"
            return f"₹{value:,.2f}"

        lines = [
            "# Staging Value Lineage Report",
            "",
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Query Parameters",
            "",
            f"| Parameter | Value |",
            f"|-----------|-------|",
            f"| Project | {summary['project']} |",
            f"| Period | {summary['period']} |",
            f"| Time Mode | {summary['time_mode'].upper()} |",
            f"| Sort Date | {summary['sort_date']} |",
            "",
            "## Verification Summary",
            "",
            "| Metric | Staging Value | Calculated Value | Difference | Match |",
            "|--------|---------------|------------------|------------|-------|",
            f"| **Plan Cost** | {format_inr(summary['staging_plan'])} | {format_inr(summary['calculated_plan'])} | {format_inr(summary['plan_difference'])} | {'✅' if summary['plan_match'] else '❌'} |",
            f"| **Actual Cost** | {format_inr(summary['staging_actual'])} | {format_inr(summary['calculated_actual'])} | {format_inr(summary['actual_difference'])} | {'✅' if summary['actual_match'] else '❌'} |",
            "",
            "## Calculation Details",
            "",
            f"- **Total Tasks Contributing:** {summary['task_count']}",
            f"- **Calculation Method:** Sum of all weekly costs where `week_start` = `{summary['sort_date']}`",
            "",
            "### Formula",
            "",
            "```",
            f"Staging Plan Cost = Σ (task.cost_timeline.weekly_costs[week_start={summary['sort_date']}].plan.cost)",
            f"                  = {format_inr(summary['calculated_plan'])}",
            "",
            f"Staging Actual Cost = Σ (task.cost_timeline.weekly_costs[week_start={summary['sort_date']}].actual.cost)",
            f"                    = {format_inr(summary['calculated_actual'])}",
            "```",
            "",
            "## Top Contributors (by Plan Cost)",
            "",
        ]

        # Sort by plan cost and show top 20
        sorted_contribs = sorted(contributions, key=lambda x: x.plan_cost, reverse=True)

        lines.append("| # | Task Name | Category | Trade Type | Plan Cost | Actual Cost |")
        lines.append("|---|-----------|----------|------------|-----------|-------------|")

        for i, c in enumerate(sorted_contribs[:20], 1):
            name = c.task_name[:40] + "..." if len(c.task_name) > 40 else c.task_name
            lines.append(
                f"| {i} | {name} | {c.main_category[:20]} | {c.trade_type[:15]} | "
                f"{format_inr(c.plan_cost)} | {format_inr(c.actual_cost)} |"
            )

        if len(contributions) > 20:
            lines.append(f"| ... | *{len(contributions) - 20} more tasks* | | | | |")

        lines.append("")

        # Category breakdown
        lines.append("## Breakdown by Main Category")
        lines.append("")

        category_totals = {}
        for c in contributions:
            cat = c.main_category or 'Unknown'
            if cat not in category_totals:
                category_totals[cat] = {'plan': 0, 'actual': 0, 'count': 0}
            category_totals[cat]['plan'] += c.plan_cost
            category_totals[cat]['actual'] += c.actual_cost
            category_totals[cat]['count'] += 1

        sorted_cats = sorted(category_totals.items(), key=lambda x: x[1]['plan'], reverse=True)

        lines.append("| Category | Tasks | Plan Cost | Actual Cost | % of Total |")
        lines.append("|----------|-------|-----------|-------------|------------|")

        for cat, totals in sorted_cats:
            pct = (totals['plan'] / summary['calculated_plan'] * 100) if summary['calculated_plan'] > 0 else 0
            lines.append(
                f"| {cat[:30]} | {totals['count']} | {format_inr(totals['plan'])} | "
                f"{format_inr(totals['actual'])} | {pct:.1f}% |"
            )

        lines.append("")

        # Trade type breakdown
        lines.append("## Breakdown by Trade Type")
        lines.append("")

        trade_totals = {}
        for c in contributions:
            trade = c.trade_type or 'Unknown'
            if trade not in trade_totals:
                trade_totals[trade] = {'plan': 0, 'actual': 0, 'count': 0}
            trade_totals[trade]['plan'] += c.plan_cost
            trade_totals[trade]['actual'] += c.actual_cost
            trade_totals[trade]['count'] += 1

        sorted_trades = sorted(trade_totals.items(), key=lambda x: x[1]['plan'], reverse=True)

        lines.append("| Trade Type | Tasks | Plan Cost | Actual Cost | % of Total |")
        lines.append("|------------|-------|-----------|-------------|------------|")

        for trade, totals in sorted_trades[:15]:
            pct = (totals['plan'] / summary['calculated_plan'] * 100) if summary['calculated_plan'] > 0 else 0
            lines.append(
                f"| {trade[:25]} | {totals['count']} | {format_inr(totals['plan'])} | "
                f"{format_inr(totals['actual'])} | {pct:.1f}% |"
            )

        if len(sorted_trades) > 15:
            lines.append(f"| *... {len(sorted_trades) - 15} more* | | | | |")

        lines.append("")
        lines.append("## Data Source Files")
        lines.append("")
        lines.append(f"- **Master JSON:** `output/json/{summary['project']}.json`")
        lines.append(f"- **Staging JSON:** `output/staging/page1-executive-summary.json`")
        lines.append(f"- **CSV Details:** `{output_path.stem}.csv`")
        lines.append("")

        with open(output_path, 'w') as f:
            f.write('\n'.join(lines))


def main():
    parser = argparse.ArgumentParser(description='Trace staging value to source tasks')
    parser.add_argument('--project', required=True, help='Project name (e.g., "Jardinia")')
    parser.add_argument('--period', required=True, help='Period label (e.g., "Wk 47" or "Oct-25")')
    parser.add_argument('--time-mode', choices=['fy', 'quarter', 'month'], required=True,
                       help='Time mode (fy, quarter, month)')
    parser.add_argument('--output-dir', default=None, help='Output directory (default: test/staging)')

    args = parser.parse_args()

    # Setup paths
    script_dir = Path(__file__).parent
    project_dir = script_dir.parent.parent
    project_json_dir = project_dir / 'output' / 'json'
    staging_file = project_dir / 'output' / 'staging' / 'page1-executive-summary.json'

    output_dir = Path(args.output_dir) if args.output_dir else script_dir

    # Create tracer
    tracer = StagingValueTracer(str(project_json_dir), str(staging_file))

    print(f"Tracing staging value...")
    print(f"  Project: {args.project}")
    print(f"  Period: {args.period}")
    print(f"  Time Mode: {args.time_mode}")
    print()

    try:
        contributions, summary = tracer.trace_contributions(
            args.project, args.period, args.time_mode
        )
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}")
        return 1

    # Generate output filenames
    safe_project = args.project.replace(' ', '_').replace('.', '_')
    safe_period = args.period.replace(' ', '_')
    base_name = f"lineage_{safe_project}_{safe_period}_{args.time_mode}"

    csv_path = output_dir / f"{base_name}.csv"
    md_path = output_dir / f"{base_name}.md"

    # Generate outputs
    tracer.generate_csv(contributions, summary, csv_path)
    print(f"Generated CSV: {csv_path}")

    tracer.generate_report(contributions, summary, md_path)
    print(f"Generated Report: {md_path}")

    # Print summary
    print()
    print("=" * 60)
    print("VERIFICATION SUMMARY")
    print("=" * 60)
    print(f"Tasks Contributing: {summary['task_count']}")
    print()
    print(f"Plan Cost:")
    print(f"  Staging:    {summary['staging_plan']:>20,.2f}")
    print(f"  Calculated: {summary['calculated_plan']:>20,.2f}")
    print(f"  Match: {'✅ YES' if summary['plan_match'] else '❌ NO'}")
    print()
    print(f"Actual Cost:")
    print(f"  Staging:    {summary['staging_actual']:>20,.2f}")
    print(f"  Calculated: {summary['calculated_actual']:>20,.2f}")
    print(f"  Match: {'✅ YES' if summary['actual_match'] else '❌ NO'}")

    return 0 if summary['plan_match'] and summary['actual_match'] else 1


if __name__ == '__main__':
    exit(main())
