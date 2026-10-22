# Threads and Concurrency

polyglot3 can be used from many threads at once, for example from a
`ThreadPoolExecutor`, a web server or a reactive pipeline such as
[RxPY](https://github.com/ReactiveX/RxPY). Language detection, tokenization,
part of speech tagging, named entity recognition, polarity and embeddings
return the same results as a single-threaded run.

- Models are loaded once per process. If several threads need a model at the
  same time, one loads it and the others wait for it. Different models load
  in parallel.
- Language detection's fastText model is loaded once, under a lock, and
  predictions are safe to run concurrently.
- Create a `Text` per document instead of sharing one between threads. A
  `Text` caches its results, so two threads reading the same property of a
  new `Text` may both compute it.

## Before starting threads

Download the models in advance (`polyglot3 download LANG:tr`, see
{doc}`Download`). Don't run the downloader from several threads or processes
at the same time.

The first use of a language loads its models from disk, which takes a few
seconds. In a server, do this at startup so the first requests aren't slow:

```python
for doc in ["Ankara'da yaşadı.", "Narodil se v Praze."]:
  Text(doc).entities
```

## Threads or processes

polyglot3 is pure Python and NumPy and runs while holding the Python GIL.
Threads let you process documents concurrently with other work, such as
network I/O, but don't use more than one CPU core. For CPU-bound batch jobs,
use processes (`ProcessPoolExecutor`, `multiprocessing`). Each process loads
its own copy of the models it uses.

## Examples

With a thread pool:

```python
from concurrent.futures import ThreadPoolExecutor

from polyglot3.text import Text

docs = ["Mustafa Kemal Atatürk Ankara'da yaşadı.",
        "Václav Havel se narodil v Praze.",
        "Joko Widodo lahir di Surakarta."]

def entities(doc):
  return [(e.tag, " ".join(e)) for e in Text(doc).entities]

with ThreadPoolExecutor(max_workers=8) as pool:
  for result in pool.map(entities, docs):
    print(result)
```

```text
[('I-PER', 'Mustafa Kemal Atatürk')]
[('I-PER', 'Václav Havel'), ('I-LOC', 'Praze')]
[('I-PER', 'Joko Widodo'), ('I-LOC', 'Surakarta')]
```

With RxPY (`pip install reactivex`), using the `entities` function above:

```python
import reactivex as rx
from reactivex import operators as ops
from reactivex.scheduler import ThreadPoolScheduler

pool = ThreadPoolScheduler(8)

rx.from_iterable(docs).pipe(
    ops.flat_map(lambda doc: rx.start(lambda: entities(doc), scheduler=pool)),
).subscribe(print)
```

Results arrive in completion order, not input order.
