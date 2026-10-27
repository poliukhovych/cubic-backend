#!/usr/bin/env python3
"""Request-log report: counts by status and duration percentiles.

Reads the backend's structured log lines (the app must run with
USE_JSON_LOGS=true) from files or stdin and prints success/failure counts and
p50/p95/p99 duration, optionally restricted to a time window so the same
command can describe the state before, during and after an incident.

Usage:
    docker compose logs --no-color main_api | scripts/log_report.py -
    scripts/log_report.py backend.log --endpoint /api/schedules --since 2026-10-27T18:00:00
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict

# Alert rule from the risk register: more than this share of 5xx is a page.
ERROR_BUDGET = 0.20


def parse(streams):
    """Yield completed-request records; non-JSON and non-request lines are skipped."""
    for stream in streams:
        for line in stream:
            line = line.strip()
            start = line.find("{")
            if start == -1:
                continue
            try:
                entry = json.loads(line[start:])
            except json.JSONDecodeError:
                continue
            if "status_code" in entry and "duration" in entry:
                yield entry


def percentile(values, share):
    if not values:
        return None
    ordered = sorted(values)
    index = min(int(round(share * (len(ordered) - 1))), len(ordered) - 1)
    return ordered[index]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("logs", nargs="*", default=["-"],
                        help="log files, or - for stdin (default)")
    parser.add_argument("--endpoint", help="only endpoints starting with this prefix")
    parser.add_argument("--since", help="ISO timestamp, inclusive lower bound")
    parser.add_argument("--until", help="ISO timestamp, exclusive upper bound")
    parser.add_argument("--top", type=int, default=10, help="slowest endpoints to list")
    args = parser.parse_args()

    streams = [sys.stdin] if args.logs == ["-"] else [open(p, encoding="utf-8") for p in args.logs]

    by_status = Counter()
    durations = []
    per_endpoint = defaultdict(list)

    for entry in parse(streams):
        endpoint = entry.get("endpoint", "")
        timestamp = entry.get("timestamp", "")
        if args.endpoint and not endpoint.startswith(args.endpoint):
            continue
        if args.since and timestamp < args.since:
            continue
        if args.until and timestamp >= args.until:
            continue
        by_status[int(entry["status_code"])] += 1
        durations.append(float(entry["duration"]))
        per_endpoint[endpoint].append(float(entry["duration"]))

    total = sum(by_status.values())
    if not total:
        print("no completed requests matched the filters "
              "(is the backend running with USE_JSON_LOGS=true?)")
        return 1

    failures = sum(count for status, count in by_status.items() if status >= 500)
    client_errors = sum(count for status, count in by_status.items() if 400 <= status < 500)
    success = total - failures - client_errors

    scope = args.endpoint or "all endpoints"
    print(f"window: {args.since or 'start'} .. {args.until or 'end'}   scope: {scope}")
    print(f"requests          {total}")
    print(f"  success (2xx/3xx) {success}")
    print(f"  client errors 4xx {client_errors}")
    print(f"  failures      5xx {failures}  ({failures / total:.1%})")
    print("by status         " + ", ".join(
        f"{status}:{count}" for status, count in sorted(by_status.items())))
    print(f"duration ms       p50 {percentile(durations, 0.50):.1f}   "
          f"p95 {percentile(durations, 0.95):.1f}   "
          f"p99 {percentile(durations, 0.99):.1f}   "
          f"max {max(durations):.1f}")

    slowest = sorted(per_endpoint.items(), key=lambda kv: percentile(kv[1], 0.95), reverse=True)
    print(f"slowest endpoints by p95 (top {args.top}):")
    for endpoint, values in slowest[:args.top]:
        print(f"  {percentile(values, 0.95):8.1f} ms  n={len(values):<5} {endpoint}")

    breached = failures / total > ERROR_BUDGET
    print(f"alert rule >{ERROR_BUDGET:.0%} 5xx: {'BREACHED' if breached else 'ok'}")
    return 2 if breached else 0


if __name__ == "__main__":
    sys.exit(main())
