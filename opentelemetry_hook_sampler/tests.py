from opentelemetry_hook_sampler import HookSampler
from opentelemetry.sdk.trace.sampling import Decision, ParentBased


def always_hook():
    return 100


def never_hook():
    return 0


def partial_hook():
    return 20


def test_always_hook(mocker):
    randint_mock = mocker.patch("opentelemetry_hook_sampler.randint", autospec=True)
    sampler = ParentBased(root=HookSampler(always_hook))
    result = sampler.should_sample(None, None, None)
    assert result.decision == Decision.RECORD_AND_SAMPLE
    randint_mock.assert_not_called()


def test_never_hook(mocker):
    randint_mock = mocker.patch("opentelemetry_hook_sampler.randint", autospec=True)
    sampler = ParentBased(root=HookSampler(never_hook))
    result = sampler.should_sample(None, None, None)
    assert result.decision == Decision.DROP
    randint_mock.assert_not_called()


def test_partial_hook_sampled(mocker):
    mocker.patch("opentelemetry_hook_sampler.randint", return_value=10)
    sampler = ParentBased(root=HookSampler(partial_hook))
    result = sampler.should_sample(None, None, None)
    assert result.decision == Decision.RECORD_AND_SAMPLE


def test_partial_hook_dropped(mocker):
    mocker.patch("opentelemetry_hook_sampler.randint", return_value=30)
    sampler = ParentBased(root=HookSampler(partial_hook))
    result = sampler.should_sample(None, None, None)
    assert result.decision == Decision.DROP
