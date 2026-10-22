"""Property-based fuzzing with Hypothesis: state what must ALWAYS hold, let the tool hunt."""
import pytest
from hypothesis import given, settings, strategies as st

from sanitize import naive_safe_name, safe_name

# Generate short strings from the characters that matter for paths
paths = st.text(alphabet="./a", max_size=12)


@settings(max_examples=2000)
@given(paths)
def test_naive_never_returns_traversal(name):
    "log the paths into the console to see what Hypothesis is trying"
    print(f"Testing path: {name}")
    assert "../" not in naive_safe_name(name)


@settings(max_examples=2000)
@given(paths)
def test_safe_never_returns_traversal(name):
    try:
        result = safe_name(name)
    except ValueError:
        return                                   # rejecting input is fine
    assert "/" not in result and result not in (".", "..")
