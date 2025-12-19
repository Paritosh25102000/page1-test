#!/usr/bin/env python3
"""
Interactive Staging Value Lineage Tracer

An interactive CLI tool that traces staging dashboard values back to source tasks.
Supports fuzzy matching for project names and periods.

Usage:
    python trace_runner.py
    python trace_runner.py --project "jard" --period "47"
    python trace_runner.py -p "horizon" -w "oct"
"""

import json
import sys
import argparse
from pathlib import Path
from typing import List, Tuple, Optional
from difflib import SequenceMatcher
import subprocess

# Try to import readchar for interactive selection, fall back to simple input
try:
    import readchar
    HAS_READCHAR = True
except ImportError:
    HAS_READCHAR = False


class FuzzyMatcher:
    """Fuzzy matching for project names and periods."""

    def __init__(self, staging_file: str):
        self.staging_file = Path(staging_file)
        self.staging_data = None
        self.projects = []
        self.periods_by_project = {}
        self._load_data()

    def _load_data(self):
        """Load staging data and extract available projects/periods."""
        with open(self.staging_file) as f:
            self.staging_data = json.load(f)

        dashboard_data = self.staging_data.get('dashboard_data', {})

        for key in dashboard_data.keys():
            if key.startswith('PROJ_'):
                project_name = key[5:]  # Remove 'PROJ_' prefix
                self.projects.append(project_name)

                # Get available periods for this project
                proj_data = dashboard_data[key]
                coc_trend = proj_data.get('coc_trend', {})

                periods = []
                # Collect all unique periods across time modes
                for series_key in ['fy_series', 'quarter_series', 'month_series']:
                    series = coc_trend.get(series_key, [])
                    time_mode = series_key.replace('_series', '')
                    for point in series:
                        label = point.get('label', '')
                        if label:
                            periods.append((label, time_mode, point.get('sort_date', '')))

                self.periods_by_project[project_name] = periods

    def _similarity(self, a: str, b: str) -> float:
        """Calculate similarity ratio between two strings."""
        a_lower = a.lower()
        b_lower = b.lower()

        # Exact match
        if a_lower == b_lower:
            return 1.0

        # Contains match (boost score)
        if a_lower in b_lower or b_lower in a_lower:
            return 0.9 + SequenceMatcher(None, a_lower, b_lower).ratio() * 0.1

        return SequenceMatcher(None, a_lower, b_lower).ratio()

    def find_matches(
        self,
        project_query: str,
        period_query: str,
        top_n: int = 10
    ) -> List[Tuple[str, str, str, float]]:
        """
        Find best matching project-period combinations.

        Returns:
            List of (project, period, time_mode, score) tuples
        """
        matches = []

        for project in self.projects:
            proj_score = self._similarity(project_query, project)

            for period, time_mode, sort_date in self.periods_by_project.get(project, []):
                period_score = self._similarity(period_query, period)

                # Combined score (weighted average)
                combined_score = (proj_score * 0.6) + (period_score * 0.4)

                matches.append((project, period, time_mode, combined_score))

        # Sort by score descending
        matches.sort(key=lambda x: x[3], reverse=True)

        # Remove duplicates (same project-period pair from different time modes)
        seen = set()
        unique_matches = []
        for m in matches:
            key = (m[0], m[1])
            if key not in seen:
                seen.add(key)
                unique_matches.append(m)

        return unique_matches[:top_n]

    def get_exact_match(self, project: str, period: str) -> Optional[Tuple[str, str, str]]:
        """Check if exact match exists."""
        for proj in self.projects:
            if proj.lower() == project.lower():
                for p, tm, sd in self.periods_by_project.get(proj, []):
                    if p.lower() == period.lower():
                        return (proj, p, tm)
        return None


class InteractiveSelector:
    """Interactive CLI selector with arrow key navigation."""

    def __init__(self, options: List[Tuple[str, str, str, float]]):
        self.options = options
        self.selected_index = 0

    def _clear_lines(self, n: int):
        """Clear n lines above cursor."""
        for _ in range(n):
            sys.stdout.write('\033[A')  # Move up
            sys.stdout.write('\033[K')  # Clear line

    def _print_menu(self):
        """Print the selection menu."""
        print("\n  Use ↑/↓ arrows to select, Enter to confirm, 'q' to quit:\n")
        for i, (project, period, time_mode, score) in enumerate(self.options):
            prefix = "→ " if i == self.selected_index else "  "
            highlight = "\033[7m" if i == self.selected_index else ""
            reset = "\033[0m" if i == self.selected_index else ""
            print(f"  {prefix}{highlight}{i+1:2}. {project} - {period} ({time_mode.upper()}) [score: {score:.2f}]{reset}")
        print()

    def select_with_arrows(self) -> Optional[Tuple[str, str, str]]:
        """Interactive selection with arrow keys."""
        if not HAS_READCHAR:
            return self.select_with_number()

        self._print_menu()
        menu_lines = len(self.options) + 4  # options + header + footer

        while True:
            key = readchar.readkey()

            if key == readchar.key.UP:
                self.selected_index = max(0, self.selected_index - 1)
            elif key == readchar.key.DOWN:
                self.selected_index = min(len(self.options) - 1, self.selected_index + 1)
            elif key == readchar.key.ENTER or key == '\r' or key == '\n':
                project, period, time_mode, _ = self.options[self.selected_index]
                return (project, period, time_mode)
            elif key == 'q' or key == readchar.key.ESCAPE:
                return None

            # Redraw menu
            self._clear_lines(menu_lines)
            self._print_menu()

    def select_with_number(self) -> Optional[Tuple[str, str, str]]:
        """Fallback selection with number input."""
        print("\n  Select an option (1-{}) or 'q' to quit:\n".format(len(self.options)))
        for i, (project, period, time_mode, score) in enumerate(self.options):
            print(f"  {i+1:2}. {project} - {period} ({time_mode.upper()}) [score: {score:.2f}]")
        print()

        while True:
            try:
                choice = input("  Enter selection: ").strip()
                if choice.lower() == 'q':
                    return None
                idx = int(choice) - 1
                if 0 <= idx < len(self.options):
                    project, period, time_mode, _ = self.options[idx]
                    return (project, period, time_mode)
                print("  Invalid selection. Try again.")
            except ValueError:
                print("  Please enter a number or 'q' to quit.")


def run_tracer(project: str, period: str, time_mode: str, output_dir: Path):
    """Run the trace_staging_value.py script."""
    script_path = Path(__file__).parent / 'trace_staging_value.py'

    cmd = [
        sys.executable,
        str(script_path),
        '--project', project,
        '--period', period,
        '--time-mode', time_mode,
        '--output-dir', str(output_dir)
    ]

    print(f"\n{'='*60}")
    print(f"Running tracer for: {project} - {period} ({time_mode.upper()})")
    print('='*60 + '\n')

    result = subprocess.run(cmd, capture_output=False)
    return result.returncode


def main():
    parser = argparse.ArgumentParser(
        description='Interactive Staging Value Lineage Tracer',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python trace_runner.py                          # Interactive mode
  python trace_runner.py -p "jardinia" -w "47"    # Fuzzy match
  python trace_runner.py -p "Horizon" -w "Oct-25" # Exact match
        """
    )
    parser.add_argument('-p', '--project', default='', help='Project name (fuzzy match supported)')
    parser.add_argument('-w', '--period', default='', help='Period/Week label (fuzzy match supported)')
    parser.add_argument('-o', '--output-dir', default=None, help='Output directory')
    parser.add_argument('--top', type=int, default=10, help='Number of suggestions to show (default: 10)')
    parser.add_argument('-y', '--yes', action='store_true', help='Auto-confirm best match without prompting')
    parser.add_argument('-s', '--select', type=int, default=None, help='Auto-select option N from the list (1-based)')

    args = parser.parse_args()

    # Setup paths
    script_dir = Path(__file__).parent
    project_dir = script_dir.parent.parent
    staging_file = project_dir / 'output' / 'staging' / 'page1-executive-summary.json'
    output_dir = Path(args.output_dir) if args.output_dir else script_dir

    if not staging_file.exists():
        print(f"Error: Staging file not found: {staging_file}")
        return 1

    # Initialize fuzzy matcher
    print("\n  Loading staging data...")
    matcher = FuzzyMatcher(str(staging_file))
    print(f"  Found {len(matcher.projects)} projects\n")

    # Get user input if not provided
    project_query = args.project
    period_query = args.period

    if not project_query:
        project_query = input("  Enter project name (or partial): ").strip()
        if not project_query:
            print("  No project specified. Exiting.")
            return 1

    if not period_query:
        period_query = input("  Enter period/week (or partial): ").strip()
        if not period_query:
            print("  No period specified. Exiting.")
            return 1

    # Check for exact match first
    exact = matcher.get_exact_match(project_query, period_query)
    if exact:
        project, period, time_mode = exact
        print(f"\n  ✓ Exact match found: {project} - {period} ({time_mode.upper()})")
        if args.yes:
            confirm = 'y'
        else:
            try:
                confirm = input("  Proceed? [Y/n]: ").strip().lower()
            except EOFError:
                confirm = 'y'
        if confirm in ('', 'y', 'yes'):
            return run_tracer(project, period, time_mode, output_dir)
        else:
            print("  Cancelled.")
            return 0

    # Find fuzzy matches
    print(f"\n  Searching for matches: project='{project_query}', period='{period_query}'...")
    matches = matcher.find_matches(project_query, period_query, top_n=args.top)

    if not matches:
        print("  No matches found.")
        return 1

    # Check if top match is very confident
    top_score = matches[0][3]
    if top_score >= 0.95:
        project, period, time_mode, score = matches[0]
        print(f"\n  ✓ Best match: {project} - {period} ({time_mode.upper()}) [score: {score:.2f}]")
        if args.yes:
            confirm = 'y'
        else:
            try:
                confirm = input("  Proceed? [Y/n]: ").strip().lower()
            except EOFError:
                confirm = 'y'  # Auto-confirm in non-interactive mode
        if confirm in ('', 'y', 'yes'):
            return run_tracer(project, period, time_mode, output_dir)

    # Interactive selection
    print(f"\n  Found {len(matches)} possible matches:")
    selector = InteractiveSelector(matches)

    # Auto-select if specified
    if args.select is not None:
        if 1 <= args.select <= len(matches):
            project, period, time_mode, score = matches[args.select - 1]
            print(f"\n  Auto-selected #{args.select}: {project} - {period} ({time_mode.upper()})")
            return run_tracer(project, period, time_mode, output_dir)
        else:
            print(f"\n  Invalid selection: {args.select}. Must be 1-{len(matches)}.")
            return 1

    if HAS_READCHAR:
        selection = selector.select_with_arrows()
    else:
        print("\n  (Install 'readchar' for arrow-key navigation: pip install readchar)")
        selection = selector.select_with_number()

    if selection is None:
        print("\n  Cancelled.")
        return 0

    project, period, time_mode = selection
    return run_tracer(project, period, time_mode, output_dir)


if __name__ == '__main__':
    sys.exit(main())
