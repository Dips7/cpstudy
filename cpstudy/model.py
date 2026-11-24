"""Analytical screening results with explicit units and validity domains."""
from dataclasses import dataclass
import math


def offered_load_bps(sources: int, rate_hz: float, wire_bytes: int) -> float:
    if sources < 0 or rate_hz < 0 or wire_bytes < 0:
        raise ValueError("Load inputs cannot be negative")
    return 8 * sources * rate_hz * wire_bytes


@dataclass(frozen=True)
class QueuePrediction:
    utilization: float
    stable: bool
    mean_wait_s: float | None
    mean_sojourn_s: float | None


def mg1(arrival_hz: float, service_mean_s: float, service_second_s2: float) -> QueuePrediction:
    """Infinite FCFS M/G/1, independent iid service, Poisson input, one worker.

    Not a finite-queue or deadline distribution prediction. None marks overload.
    """
    vals = (arrival_hz, service_mean_s, service_second_s2)
    if any(not math.isfinite(x) or x < 0 for x in vals):
        raise ValueError("Finite nonnegative queue parameters required")
    if service_second_s2 + 1e-18 < service_mean_s**2:
        raise ValueError("Second moment cannot be less than squared mean")
    rho = arrival_hz * service_mean_s
    if rho >= 1:
        return QueuePrediction(rho, False, None, None)
    wait = arrival_hz * service_second_s2 / (2 * (1 - rho))
    return QueuePrediction(rho, True, wait, wait + service_mean_s)


def muhammad2019_mean(rate_hz: float, neighbors: int, sender_service_s: float,
                      radio_service_s: float, receiver_service_s: float,
                      fixed_s: float = 0.0) -> float | None:
    """Reproduce equations (2)-(3) of DOI 10.1007/978-3-030-26250-1_20.

    N is the paper's common radio/receiver contention population, not necessarily
    the total physical-node count (self reception is excluded in our simulator).
    Three infinite M/M/1 stages. This does not predict finite-queue delivery.
    """
    if neighbors < 0 or fixed_s < 0:
        raise ValueError("Nonnegative population and fixed delay required")
    predictions = [mg1(arrival,mean,2*mean**2) for arrival,mean in (
        (rate_hz,sender_service_s),(neighbors*rate_hz,radio_service_s),
        (neighbors*rate_hz,receiver_service_s))]
    if not all(p.stable for p in predictions):return None
    return fixed_s + sum(p.mean_sojourn_s for p in predictions)
