# ADR 0002: cppcheck as the Phase 3 C++ SAST gate

- Status: Accepted
- Date: 2026-07-11

## Context

CodeQL C++ analysis requires tracing a ROS/colcon C++ build and introduces additional setup and runtime. Phase 3 needs a reproducible C++ security gate that runs inside the existing ROS CI image.

## Decision

Use Semgrep with repository-owned rules for Python and cppcheck for C++. Keep CodeQL C++ as a future hardening item.

## Limits

cppcheck is pattern- and flow-oriented static analysis, but it does not provide the same whole-program query model or GitHub code-scanning experience as CodeQL. It may miss cross-component data-flow vulnerabilities and can report false positives. Compiler warnings, gtests, configuration validation, and review remain required complementary controls.
