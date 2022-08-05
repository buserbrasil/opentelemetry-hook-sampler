from random import randint
from typing import Optional, Sequence

from opentelemetry.context import Context
from opentelemetry.trace import Link, SpanKind
from opentelemetry.trace.span import TraceState
from opentelemetry.sdk.trace.sampling import (
    Decision,
    Sampler,
    SamplingResult,
    _get_parent_trace_state,
)
from opentelemetry.util.types import Attributes


class HookSampler(Sampler):
    def __init__(self, sampler: callable):
        self._sampler = sampler

    def should_sample(
        self,
        parent_context: Optional[Context],
        trace_id: int,
        name: str,
        kind: SpanKind = None,
        attributes: Attributes = None,
        links: Sequence[Link] = None,
        trace_state: TraceState = None,
    ) -> SamplingResult:
        decision = Decision.DROP
        # Sampler return an int [0, 100]
        rate = self._sampler()

        if rate and (rate == 100 or randint(0, 100) < rate):
            decision = Decision.RECORD_AND_SAMPLE

        if decision is Decision.DROP:
            attributes = None

        return SamplingResult(
            decision,
            attributes,
            _get_parent_trace_state(parent_context),
        )

    def get_description(self) -> str:
        return f"{self.__class__.__name__}(sampler={self._sampler.__name__})"
