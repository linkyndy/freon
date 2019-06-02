# freon

[![Build Status](https://travis-ci.org/linkyndy/freon.svg?branch=master)](https://travis-ci.org/linkyndy/freon)

Keeps your cached data fresh just as freon keeps your food fresh in the fridge.

## It is plain simple!

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

# way later...
for _ in range(10):
  # Avoids the dog-pile effect
  cache.get_or_set('foo', 'baz')
```

## Features

* simple, powerful and extensible;
* Redis and memory backends out of the box;
* msgpack, JSON and pickle serializers out of the box;
* dynamic values and TTLs;
* avoids the dog-pile effect.

## Installation

```bash
pip install freon
```

## Configuration

By default, freon uses the `memory` backend, together with the `json` serializer. If you wish to work with something else, it's as easy as:

```python
cache = Cache(backend='redis', serializer='msgpack')
```

> Don't forget to install the necessary packages for this (`redis` and `msgpack`). freon will then happily import them!

## Cookbook

### Dynamic values and TTLs

```python
cache = Cache()

def expensive_operation():
  # A very expensive operation
  return 'bar'

# Set a different TTL based on the cached value
dynamic_ttl = lambda value: 60 if value == 'bar' else 3600

cache.set('foo', expensive_operation, dynamic_ttl)
# Returns 'bar'
```

## Motivation

The main reason for freon's existence was the need of a very simple and light-weight caching library, one that handles dynamic values and TTLs, one that avoids the dog-pile effect and one that can be easily extended with various backends and serializers.

## Status

freon is production-ready. It was successfully used in my [Master's Thesis](https://github.com/linkyndy/master-thesis), "A Predictive Caching Strategy for Ticket Availability Information", hosted by the University of Amsterdam and Tiqets.com.

## How to contribute?

Any contribution is **highly** appreciated! See [CONTRIBUTING.md](CONTRIBUTING.md) for more details.

## License

See [LICENSE](LICENSE)
