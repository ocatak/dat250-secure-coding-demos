#!/usr/bin/env bash
# Does every package the assistant suggested actually exist on PyPI?
while read -r pkg; do
  [ -z "$pkg" ] && continue
  code=$(curl -s -o /dev/null -w '%{http_code}' "https://pypi.org/pypi/$pkg/json")
  if [ "$code" = "200" ]; then echo "  OK        $pkg"; else echo "  MISSING   $pkg   <- hallucinated? someone could register it"; fi
done < "${1:-requirements-ai.txt}"
