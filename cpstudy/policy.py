from dataclasses import dataclass


@dataclass
class Controller:
    rate: float
    low_streak: int = 0

    def update(self, cfg, busy, backlog, stale=False, observed=None, avg_backlog=None):
        mode = cfg["policy"]
        if mode == "fixed":
            return self.rate
        if mode == "calibrated":
            obs = (observed > 0) if observed is not None else (not stale)
            eff_backlog = avg_backlog if avg_backlog is not None else backlog
            q_high = obs and (eff_backlog > cfg["queue_high"])
            q_low = (not obs) or (eff_backlog < cfg["queue_low"])
            r_high = busy > cfg["radio_high"]
            r_low = busy < cfg["radio_low"]
            high = r_high or q_high
            low = r_low and q_low
            if high:
                self.rate = max(cfg["min_rate_hz"], self.rate * cfg["decrease"])
                self.low_streak = 0
            elif low:
                self.low_streak += 1
                if self.low_streak >= 2:
                    self.rate = min(cfg["max_rate_hz"], self.rate + cfg["increase_hz"])
                    self.low_streak = 0
            else:
                self.low_streak = 0
            return self.rate
        use_radio = mode in ("radio", "joint")
        use_queue = mode in ("receiver", "joint")
        high = (use_radio and busy > cfg["radio_high"]) or (
            use_queue and (stale or backlog > cfg["queue_high"]))
        low = (not use_radio or busy < cfg["radio_low"]) and (
            not use_queue or (not stale and backlog < cfg["queue_low"]))
        if high:
            self.rate = max(cfg["min_rate_hz"], self.rate * cfg["decrease"])
            self.low_streak = 0
        elif low:
            self.low_streak += 1
            if self.low_streak >= 2:
                self.rate = min(cfg["max_rate_hz"], self.rate + cfg["increase_hz"])
                self.low_streak = 0
        else:
            self.low_streak = 0
        return self.rate
