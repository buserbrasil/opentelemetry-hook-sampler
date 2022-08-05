from unittest.mock import Mock

from opentelemetry_hook_sampler import HookSampler, HoneycombHookSampler
from opentelemetry.sdk.trace.sampling import Decision, ParentBased
import pytest


@pytest.fixture
def randint_mock(mocker):
    return mocker.patch("opentelemetry_hook_sampler.randint", autospec=True)


def sample(func, *, _sampler=HookSampler):
    sampler = ParentBased(root=_sampler(func))
    return sampler.should_sample(None, None, None)


def test_always_hook(randint_mock):
    always_hook = Mock(return_value=1)
    result = sample(always_hook)
    assert result.decision == Decision.RECORD_AND_SAMPLE
    # Slow call to randint avoided.
    randint_mock.assert_not_called()


def test_never_hook(randint_mock):
    never_hook = Mock(return_value=0)
    result = sample(never_hook)
    assert result.decision == Decision.DROP
    # Slow call to randint avoided.
    randint_mock.assert_not_called()


def test_null_hook(randint_mock):
    null_hook = Mock(return_value=None)
    result = sample(null_hook)
    assert result.decision == Decision.DROP
    # Slow call to randint avoided.
    randint_mock.assert_not_called()


def test_partial_hook_sampled(randint_mock):
    partial_hook = Mock(return_value=5)
    randint_mock.return_value = 5
    result = sample(partial_hook)
    assert result.decision == Decision.RECORD_AND_SAMPLE


def test_partial_hook_dropped(randint_mock):
    partial_hook = Mock(return_value=5)
    randint_mock.return_value = 3
    result = sample(partial_hook)
    assert result.decision == Decision.DROP


def test_description():
    def foo():
        pass

    hook_sampler = HookSampler(foo)
    assert hook_sampler.get_description() == "HookSampler(sampler=foo)"


def test_subclass_description():
    def foo():
        pass

    class SubHookSampler(HookSampler):
        pass

    hook_sampler = SubHookSampler(foo)
    assert hook_sampler.get_description() == "SubHookSampler(sampler=foo)"


def test_honeycomb_sample_rate_attribute():
    always_hook = Mock(return_value=1)
    result = sample(always_hook, _sampler=HoneycombHookSampler)
    assert result.attributes["SampleRate"] == 1
