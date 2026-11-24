# Rate scheduler regression

Reproduction: two sources, 10 Hz acquisition opportunities, 3 Hz requested average emission, 10 seconds. The first implementation generated 25 rather than 30 updates per source. Integer-divisor cases at 1, 5 and 10 Hz concealed the error.

Root cause: the admission check measured each minimum interval from the last actual emission, repeatedly rounding 333.3 ms up to a 400 ms sensing interval. This compounded the discretization loss.

Correction: preserve the target emission timeline and release at the next available acquisition opportunity. This preserves requested average rate with at most one sensing interval of quantization jitter. It does not guarantee a minimum interval of exactly 1/rate between individual emissions. The configuration rate is an average offered-rate setting, not a packet-by-packet minimum-gap guarantee. Strict minimum-gap standards profiles require a separate generator implementation.

Regression test: test_non_divisor_rate_preserves_requested_average. The original version failed with [25,25]; the corrected version must produce [30,30].

## Deadline boundary classification

A separate overload regression found 300 fully observable deadline failures labeled right_censored. The run-end cleanup unconditionally censored unfinished messages, even when their deadline had already passed. Cleanup now records processing_unfinished for those messages; only deadlines beyond the observation boundary are right-censored. Both remain failures for coverage, so the correction changes diagnostic classification rather than inflating success. The regression first failed and then passed after the one-branch correction.
