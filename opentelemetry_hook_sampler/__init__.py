from types import MappingProxyType
from typing import Optional, Sequence

from opentelemetry.context import Context
from opentelemetry.sdk.trace.sampling import (
    ParentBased,
    SamplingResult,
    TraceIdRatioBased,
)
from opentelemetry.trace import Link, SpanKind
from opentelemetry.trace.span import TraceState
from opentelemetry.util.types import Attributes


class HookSampler(TraceIdRatioBased):
    """
    Sampler that makes sampling decisions probabilistically based on a rate
    given by the `hook` function.

    Args:
        hook: A function that must return an int N to sample 1/N times.
            Use `rate=0`, `rate=None`, or any falsy value to drop the span.
            Use `rate=1` to always record the span.
    """

    def __init__(self, hook: callable):
        self._hook = hook

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
        # get dynamic sample rate
        sample_rate = self._hook()
        if sample_rate:
            self._bound = self.get_bound_for_rate(1 / sample_rate)
        else:
            sample_rate = 0
            self._bound = self.get_bound_for_rate(0)

        # make sampling decision
        result = super().should_sample(
            parent_context, trace_id, name, kind, attributes, links, trace_state
        )

        # save sample rate on trace state
        state = TraceState() if result.trace_state is None else result.trace_state
        state = state.update("sample_rate", str(sample_rate))
        result.trace_state = state

        return result

    def get_description(self) -> str:
        return f"{self.__class__.__name__}{{{self._hook.__name__}}}"


class ParentBasedHookSampler(ParentBased):
    """
    Sampler that respects its parent span's sampling decision, but otherwise
    samples probabilistically based on a rate given by the `hook` function.
    """

    def __init__(self, hook: callable):
        root = HookSampler(hook=hook)
        super().__init__(root=root)


class HoneycombMixin:
    """
    Mixin that adds the vendor-specific attribute `SampleRate` based on TraceState.
    The `SampleRate` attribute is used by Honeycomb to show the adjusted count.
    """

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
        # make sampling decision and update trace state
        result = super().should_sample(
            parent_context, trace_id, name, kind, attributes, links, trace_state
        )

        # populate attribute based on trace state
        if result.decision.is_recording():
            state = result.trace_state
            if state is not None and "sample_rate" in state:
                attrs = result.attributes.copy()
                attrs["SampleRate"] = state["sample_rate"]
                result.attributes = MappingProxyType(attrs)

        return result


class HoneycombHookSampler(HoneycombMixin, HookSampler):
    """
    Sampler that makes sampling decisions probabilistically based on a rate
    given by the `hook` function. Also, saves the rate as an attribute that
    Honeycomb uses to show the adjusted count.
    """

    pass


class ParentBasedHoneycombHookSampler(HoneycombMixin, ParentBasedHookSampler):
    """
    Sampler that respects its parent span's sampling decision, but otherwise samples
    probabilistically based on a rate given by the `hook` function. Also, saves the
    rate as an attribute that Honeycomb uses to show the adjusted count.
    """

    pass
