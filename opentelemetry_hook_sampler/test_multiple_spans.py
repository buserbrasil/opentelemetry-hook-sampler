from unittest.mock import Mock

import pytest
from opentelemetry import trace
from opentelemetry.sdk.trace.sampling import Decision

from opentelemetry_hook_sampler import (
    ParentBasedHoneycombHookSampler,
    ParentBasedHookSampler,
)


@pytest.mark.parametrize(
    "SamplerClass",
    [
        ParentBasedHookSampler,
        ParentBasedHoneycombHookSampler,
    ],
)
def test_parent_based_sampled(SamplerClass):
    never_hook = Mock(return_value=0)
    sampler = SamplerClass(never_hook)
    parent_context = trace.set_span_in_context(
        trace.NonRecordingSpan(
            trace.SpanContext(
                0x1234,
                0x5678,
                is_remote=False,
                trace_flags=trace.TraceFlags(trace.TraceFlags.SAMPLED),
            )
        )
    )

    result = sampler.should_sample(
        parent_context,
        0x8000000000000000,
        "span name",
        attributes={"foo": "bar"},
    )

    assert result.decision == Decision.RECORD_AND_SAMPLE
    assert result.attributes["foo"] == "bar"


@pytest.mark.parametrize(
    "SamplerClass",
    [
        ParentBasedHookSampler,
        ParentBasedHoneycombHookSampler,
    ],
)
def test_parent_based_dropped(SamplerClass):
    always_hook = Mock(return_value=1)
    sampler = SamplerClass(always_hook)
    parent_context = trace.set_span_in_context(
        trace.NonRecordingSpan(
            trace.SpanContext(
                0x1234,
                0x5678,
                is_remote=False,
                trace_flags=trace.TraceFlags(trace.TraceFlags.DEFAULT),
            )
        )
    )

    result = sampler.should_sample(
        parent_context,
        0x8000000000000000,
        "span name",
        attributes={"foo": "bar"},
    )

    assert result.decision == Decision.DROP
    assert result.attributes == {}


def test_parent_based_honeycomb_sample_rate_attribute():
    hook = Mock()
    sampler = ParentBasedHoneycombHookSampler(hook)
    parent_context = trace.set_span_in_context(
        trace.NonRecordingSpan(
            trace.SpanContext(
                0x1234,
                0x5678,
                is_remote=False,
                trace_flags=trace.TraceFlags(trace.TraceFlags.SAMPLED),
                trace_state=trace.TraceState([("sample_rate", "42")]),
            )
        )
    )

    result = sampler.should_sample(
        parent_context,
        0x8000000000000000,
        "span name",
    )

    assert result.attributes["SampleRate"] == "42"
