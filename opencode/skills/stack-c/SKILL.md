---
name: stack-c
description: C code generation best practices for the AGENTS.md workflow — low-level, embedded, and systems programming with memory safety discipline. Use when the project stack is C and Phase 03 code must be generated.
---

# Stack — C (Low-Level / Embedded / Systems)

Best practices applied when generating C code in Phase 03 Construction. The dominant concern is memory safety and defined behavior.

## Precondition

- Stack confirmed: C (embedded, systems, driver, firmware, library).
- Toolchain/build confirmed (Make, CMake, GCC/Clang, cross-compiler for embedded).
- Requirements traceable to a use case in `docs/02-elaboration/`.

## Language discipline (non-negotiable)

- Compile with warnings as errors: `-Wall -Wextra -Wpedantic` (and `-Werror` for non-embedded builds). On GCC/Clang, enable `-fstack-protector-strong`.
- No undefined behavior: initialize all variables, check all array bounds, never use uninitialized pointers.
- String handling: use bounded functions (`strncpy`/`snprintf`/`strnlen`) or explicit length-tracked buffers — never unbounded `strcpy`/`sprintf`.
- Dynamic memory: every `malloc`/`calloc`/`realloc` must have a paired `free` on a single ownership path; check allocation return before use; prefer caller-owned buffers and stack allocation where the platform allows.
- Integer safety: use fixed-width types (`uint8_t`, `int32_t`) from `stdint.h`; check for overflow on arithmetic that depends on input.
- Const-correctness and `restrict` where semantics allow; avoid global mutable state.
- Error handling: return error codes (or errno-style) consistently; never ignore a function's return value.

## Embedded-specific rules

- Volatile for memory-mapped registers and ISR-shared variables; use `atomic_*` or proper synchronization for cross-context access.
- Keep ISRs short: set flags / enqueue, do the work in the main loop.
- Respect the target's memory budget: no unbounded recursion, no unbounded dynamic allocation in time-critical paths.
- Use the target's toolchain and provided startup/linker files; do not invent ABI conventions.

## Testing rules

- Unit tests with a framework (Unity, Criterion, or CMocka); host-based tests where the target is not available.
- Tests must cover buffer-boundary and error-path cases, not just the happy path.
- Memory-safety checks: run tests under sanitizers (`-fsanitize=address,undefined`) when the target is host-based.
- One test file per source file (host builds). Every Gherkin scenario of the current use case covered.
- `done` = host tests pass under ASan/UBSan && build clean with `-Werror` (embedded: target build + tests where feasible).

## Validation checklist (used by reviewer)

- [ ] Compiles warning-clean with `-Wall -Wextra -Wpedantic -Werror`
- [ ] No unbounded string/integer ops; bounded functions or length-tracked buffers
- [ ] Every allocation has a paired free on a single ownership path; returns checked
- [ ] No undefined behavior (initialized vars, checked bounds)
- [ ] Fixed-width types used; overflow handled
- [ ] Embedded: volatile/atomic for hardware access, ISRs short, memory budget respected
- [ ] Error codes checked — no ignored returns
- [ ] One test file per source file; boundary and error cases covered
- [ ] Host tests pass under ASan/UBSan (reviewer RUNS them)

## Do / Don't

- DO treat memory safety as the primary correctness criterion.
- DO compile with the strictest warning set for the platform.
- DON'T use `strcpy`/`sprintf` on unbounded buffers.
- DON'T ignore return values or allocation failures.
- DON'T generate a whole feature — one use case at a time.
