"""Adaptive DCC core from ETSI TS 102 687 V1.2.1, clause 5.4.

Research single-service mapping; not an ITS-G5 conformance implementation.
"""
from dataclasses import dataclass


def airtime_s(application_bytes):
    """802.11p 6 Mbps, 10 MHz: non-QoS MAC/IP/UDP/LLC overhead 64 B.

    40 us preamble/header, 8 us symbol, 48 data bits/symbol, service/tail 22 bits.
    No aggregation, fragmentation, ACK or retransmission included.
    """
    import math
    return .00004+.000008*math.ceil((22+8*(application_bytes+64))/48)


@dataclass
class AdaptiveDcc:
    delta: float = .005
    estimate: float = 0.

    def update(self,current,previous,application_bytes,max_rate):
        self.estimate=.5*self.estimate+.25*(current+previous)
        offset=min(.0005,max(-.00025,.0012*(.68-self.estimate)))
        self.delta=min(.03,max(.0006,.984*self.delta+offset))
        gap=min(1.,max(.025,airtime_s(application_bytes)/self.delta))
        return min(max_rate,1/gap)
