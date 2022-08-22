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
    Sample 1 in 10 traces.
    
    The example is static, but you can get info from any context available
    in your application. E.g. http request, celery task, thread locals, etc.
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


### Sampler examples

#### [django-threadlocals](https://pypi.org/project/django-threadlocals/)

Be careful, threadlocals module don't work with async Django.

```python
from threadlocals.threadlocals import get_current_request


def sampler_hook():
    request = get_current_request()
    # 10% /foo requests
    if request.path == '/foo':
        return 10
    return 1
```

#### [django-g](https://pypi.org/project/django-g/)

```python
from django_g import get_current_request


def sampler_hook():
    request = get_current_request()
    # 10% /foo requests
    if request.path == '/foo':
        return 10
    return 1
```

#### [celery](https://pypi.org/project/celery/)

```python
import celery


def sampler_hook():
    task_name = celery.current_app.current_worker_task.request.task
    # 10% foo.bar.baz tasks
    if task_name == 'foo.bar.baz':
        return 10
    return 1
```
