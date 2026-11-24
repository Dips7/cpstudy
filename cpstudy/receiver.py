"""Event-based finite receiver queues, independent of the radio implementation."""
from collections import deque
from dataclasses import dataclass


@dataclass(frozen=True)
class Update:
    source: int
    receiver: int
    opportunity: str
    message: str
    acquired: int
    deadline: int
    payload: int
    wire: int
    kind: str = "data"
    feedback_depth: int | None = None


class Receiver:
    def __init__(self, receiver_id, capacity, verify_ns, fusion_ns,
                 schedule, emit, terminal, service=None):
        self.id = receiver_id
        self.capacity = capacity
        self.verify_ns = verify_ns
        self.fusion_ns = fusion_ns
        self.schedule = schedule
        self.emit = emit
        self.terminal = terminal
        self.service = service
        self.waiting = deque()
        self.active = None
        self.latest = {}

    @property
    def depth(self):
        return len(self.waiting) + int(self.active is not None)

    def receive(self, now, update):
        self.emit(now, "reception", update, self.depth)
        # Pre-verification expiry uses controlled experiment truth only; the
        # production implementation must not trust unauthenticated metadata.
        # Thus expiry is checked only AFTER verification in this reference path.
        if self.active is None:
            self._start(now, update)
        elif len(self.waiting) >= self.capacity:
            self.terminal(now, update, "queue_overflow")
        else:
            self.waiting.append(update)
            self.emit(now, "enqueue", update, self.depth)

    def _start(self, now, update):
        self.active = update
        self.emit(now, "verification_start", update, self.depth)
        duration = self.service(update) if self.service else self.verify_ns
        self.schedule(now + duration, self._verified, update)

    def _verified(self, now, update):
        self.emit(now, "verification_end", update, self.depth)
        if now > update.deadline:
            self.terminal(now, update, "verification_expired")
        elif update.kind == "feedback":
            self.terminal(now, update, "feedback_ready")
        else:
            # Fusion is a distinct single worker-free delay in the initial
            # model. Its queue must be added before making CPU-sharing claims.
            self.schedule(now + self.fusion_ns, self._ready, update)
        self.active = None
        if self.waiting:
            self._start(now, self.waiting.popleft())

    def _ready(self, now, update):
        if now > update.deadline:
            self.terminal(now, update, "fusion_expired")
            return
        previous = self.latest.get(update.source)
        if previous is None or update.acquired > previous:
            self.latest[update.source] = update.acquired
        self.emit(now, "fusion_ready", update, self.depth)
        self.terminal(now, update, "success")
