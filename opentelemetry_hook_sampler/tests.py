from opentelemetry_hook_sampler import HookSampler
from opentelemetry.sdk.trace.sampling import Decision, ParentBased
import pytest


def always_hook():
    return 100


def never_hook():
    return 0


def partial_hook():
    return 20


class SubHookSampler(HookSampler):
    pass


@pytest.fixture
def randint_mock(mocker):
    return mocker.patch("opentelemetry_hook_sampler.randint", autospec=True)


def test_always_hook(randint_mock):
    sampler = ParentBased(root=HookSampler(always_hook))
    result = sampler.should_sample(None, None, None)
    assert result.decision == Decision.RECORD_AND_SAMPLE
    randint_mock.assert_not_called()


def test_never_hook(randint_mock):
    sampler = ParentBased(root=HookSampler(never_hook))
    result = sampler.should_sample(None, None, None)
    assert result.decision == Decision.DROP
    randint_mock.assert_not_called()


def test_partial_hook_sampled(randint_mock):
    randint_mock.return_value = 10
    sampler = ParentBased(root=HookSampler(partial_hook))
    result = sampler.should_sample(None, None, None)
    assert result.decision == Decision.RECORD_AND_SAMPLE


def test_partial_hook_dropped(randint_mock):
    randint_mock.return_value = 30
    sampler = ParentBased(root=HookSampler(partial_hook))
    result = sampler.should_sample(None, None, None)
    assert result.decision == Decision.DROP


def test_description():
    hook_sampler = HookSampler(partial_hook)
    assert hook_sampler.get_description() == "HookSampler(sampler=partial_hook)"


def test_subclass_description():
    hook_sampler = SubHookSampler(partial_hook)
    assert hook_sampler.get_description() == "SubHookSampler(sampler=partial_hook)"
