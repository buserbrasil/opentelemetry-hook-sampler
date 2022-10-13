from unittest.mock import Mock

import pytest
from opentelemetry.sdk.trace.sampling import Decision

from opentelemetry_hook_sampler import (
    HoneycombHookSampler,
    HookSampler,
    ParentBasedHoneycombHookSampler,
    ParentBasedHookSampler,
)


@pytest.mark.parametrize(
    "SamplerClass",
    [
        HookSampler,
        ParentBasedHookSampler,
        HoneycombHookSampler,
        ParentBasedHoneycombHookSampler,
    ],
)
def test_always_hook(SamplerClass):
    always_hook = Mock(return_value=1)
    sampler = SamplerClass(always_hook)

    result = sampler.should_sample(
        None,
        0xFFFFFFFFFFFFFFFF,  # last trace id to be sampled
        "span name",
        attributes={"foo": "bar"},
    )

    assert result.decision == Decision.RECORD_AND_SAMPLE
    assert result.attributes["foo"] == "bar"
    assert result.trace_state["sample_rate"] == "1"


@pytest.mark.parametrize(
    "SamplerClass",
    [
        HookSampler,
        ParentBasedHookSampler,
        HoneycombHookSampler,
        ParentBasedHoneycombHookSampler,
    ],
)
def test_never_hook(SamplerClass):
    never_hook = Mock(return_value=0)
    sampler = SamplerClass(never_hook)

    result = sampler.should_sample(
        None,
        0x0,  # first trace id to be sampled
        "span name",
        attributes={"foo": "bar"},
    )

    assert result.decision == Decision.DROP
    assert result.attributes == {}
    assert result.trace_state["sample_rate"] == "0"


@pytest.mark.parametrize(
    "SamplerClass",
    [
        HookSampler,
        ParentBasedHookSampler,
        HoneycombHookSampler,
        ParentBasedHoneycombHookSampler,
    ],
)
def test_falsy_hook(SamplerClass):
    falsy_hook = Mock(return_value=None)
    sampler = SamplerClass(falsy_hook)

    result = sampler.should_sample(
        None,
        0x0,  # first trace id to be sampled
        "span name",
        attributes={"foo": "bar"},
    )

    assert result.decision == Decision.DROP
    assert result.attributes == {}
    assert result.trace_state["sample_rate"] == "0"


@pytest.mark.parametrize(
    "SamplerClass",
    [
        HookSampler,
        ParentBasedHookSampler,
        HoneycombHookSampler,
        ParentBasedHoneycombHookSampler,
    ],
)
def test_partial_hook_sampled(SamplerClass):
    partial_hook = Mock(return_value=2)
    sampler = SamplerClass(partial_hook)

    result = sampler.should_sample(
        None,
        0x7FFFFFFFFFFFFFFF,
        "span name",
        attributes={"foo": "bar"},
    )

    assert result.decision == Decision.RECORD_AND_SAMPLE
    assert result.attributes["foo"] == "bar"
    assert result.trace_state["sample_rate"] == "2"


@pytest.mark.parametrize(
    "SamplerClass",
    [
        HookSampler,
        ParentBasedHookSampler,
        HoneycombHookSampler,
        ParentBasedHoneycombHookSampler,
    ],
)
def test_partial_hook_dropped(SamplerClass):
    partial_hook = Mock(return_value=2)
    sampler = SamplerClass(partial_hook)

    result = sampler.should_sample(
        None,
        0x8000000000000000,
        "span name",
        attributes={"foo": "bar"},
    )

    assert result.decision == Decision.DROP
    assert result.attributes == {}
    assert result.trace_state["sample_rate"] == "2"


def test_description_hook_sampler():
    def foo():
        pass

    sampler = HookSampler(foo)
    assert sampler.get_description() == "HookSampler{foo}"


def test_description_honeycomb_hook_sampler():
    def foo():
        pass

    sampler = HoneycombHookSampler(foo)
    assert sampler.get_description() == "HoneycombHookSampler{foo}"


@pytest.mark.parametrize(
    "SamplerClass",
    [
        HoneycombHookSampler,
        ParentBasedHoneycombHookSampler,
    ],
)
def test_honeycomb_sample_rate_attribute(SamplerClass):
    partial_hook = Mock(return_value=42)
    sampler = SamplerClass(partial_hook)

    result = sampler.should_sample(
        None,
        0x0,
        "span name",
    )

    assert result.attributes["SampleRate"] == "42"
