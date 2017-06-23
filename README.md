# freon
Keeps your cached data fresh just as freon keeps your food fresh in the fridge.

## Features

* simple, powerful and extensible;
* Redis and memory backends out of the box;
* msgpack, JSON and pickle serializers out of the box;
* dynamic values and TTLs;
* avoids the dog-pile effect.

## Basic usage

```python
from freon.cache import Cache

cache = Cache()
cache.set('foo', 'bar', 123)
# Returns 'bar'

cache.get('foo')
# Returns 'bar'

# approx. 123 seconds later...
cache.get('foo')
# Returns None
```
