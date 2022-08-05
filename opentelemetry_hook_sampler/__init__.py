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
        # Sampler return an int N to sample 1/N times.
        rate = self._sampler()
        if rate and (rate == 1 or randint(1, rate) == rate):
            decision = Decision.RECORD_AND_SAMPLE
        else:
            decision = Decision.DROP

        sampling_result = SamplingResult(
            decision,
            self._process_attributes(attributes, decision, rate),
            _get_parent_trace_state(parent_context),
        )
        return sampling_result

    def get_description(self) -> str:
        return f"{self.__class__.__name__}(sampler={self._sampler.__name__})"

    def _process_attributes(self, attributes, decision, rate):
        if decision is Decision.DROP:
            attributes = None
        return attributes


class HoneycombHookSampler(HookSampler):
    def _process_attributes(self, attributes, decision, rate):
        if decision is Decision.DROP:
            attributes = None
        elif decision == Decision.RECORD_AND_SAMPLE:
            if attributes is None:
                attributes = {}
            attributes.update({"SampleRate": rate})
        return attributes
