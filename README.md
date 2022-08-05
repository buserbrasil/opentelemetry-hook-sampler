# opentelemetry-hook-sampler

Custom function based sampler for `opentelemetry-python`.

## How to install

```
$ pip install opentelemetry-hook-sampler
```

## How to use

```python
import opentelemetry.trace
from opentelemetry.sdk.resources import SERVICE_NAME
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry_hook_sampler import HookSampler


def sampler_hook():
    """
    Sample every 10 traces.
    
    The example is static, but you can get info from any context available
    in your application. E.g. http request, celery task, etc.
    """
    return 10


resource = Resource(attributes={SERVICE_NAME: "foo"})
sampler = HookSampler(sampler_hook)
provider = TracerProvider(resource=resource, sampler=sampler)
opentelemetry.trace.set_tracer_provider(provider)
```

### Honeycomb specific

[Honeycomb expects](https://docs.honeycomb.io/manage-data-volume/sampling/) a
`SampleRate` attribute to normalize data. It is not OpenTelemetry spec, but
it is supported through `opentelemetry_hook_sampler.HoneycombHookSampler`.
