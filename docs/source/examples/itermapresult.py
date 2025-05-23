"""Example of iteration through AsyncMapResults, without waiting for all results

When you call view.map(func, sequence), you will receive a special AsyncMapResult
object.  These objects are used to reconstruct the results of the split call.
One feature AsyncResults provide is that they are iterable *immediately*, so
you can iterate through the actual results as they complete.

This is useful if you submit a large number of tasks that may take some time,
but want to perform logic on elements in the result, or even abort subsequent
tasks in cases where you are searching for the first affirmative result.

By default, the results will match the ordering of the submitted sequence, but
if you call `map(...ordered=False)`, then results will be provided to the iterator
on a first come first serve basis.

Authors
-------
* MinRK
"""

import time

import ipyparallel as ipp

# create client & view
rc = ipp.Client()
dv = rc[:]
v = rc.load_balanced_view()

# scatter 'id', so id=0,1,2 on engines 0,1,2
dv.scatter('id', rc.ids, flatten=True)
print("Engine IDs: ", dv['id'])

# create a Reference to `id`. This will be a different value on each engine
ref = ipp.Reference('id')
print("sleeping for `id` seconds on each engine")
tic = time.perf_counter()
ar = dv.apply(time.sleep, ref)
for i, r in enumerate(ar):
    print(f"{i}: {time.perf_counter() - tic:.3f}")


def sleep_here(t):
    import time

    time.sleep(t)
    return id, t


# one call per task
print("running with one call per task")
amr = v.map(sleep_here, [0.01 * t for t in range(100)])
tic = time.perf_counter()
for i, r in enumerate(amr):
    print(f"task {i} on engine {r[0]}: {time.perf_counter() - tic:.3f}")

print("running with four calls per task")
# with chunksize, we can have four calls per task
amr = v.map(sleep_here, [0.01 * t for t in range(100)], chunksize=4)
tic = time.perf_counter()
for i, r in enumerate(amr):
    print(f"task {i} on engine {r[0]}: {time.perf_counter() - tic:.3f}")

print("running with two calls per task, with unordered results")
# We can even iterate through faster results first, with ordered=False
amr = v.map(
    sleep_here, [0.01 * t for t in range(100, 0, -1)], ordered=False, chunksize=2
)
tic = time.perf_counter()
for i, r in enumerate(amr):
    print(f"slept {r[1]:.2f}s on engine {r[0]}: {time.perf_counter() - tic:.3f}")
