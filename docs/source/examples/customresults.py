"""An example for handling results in a way that AsyncMapResult doesn't provide

Specifically, out-of-order results with some special handing of metadata.

This just submits a bunch of jobs, waits on the results, and prints the stdout
and results of each as they finish.

Authors
-------
* MinRK
"""

import random

import ipyparallel as ipp

# create client & views
rc = ipp.Client()
dv = rc[:]
v = rc.load_balanced_view()


# scatter 'id', so id=0,1,2 on engines 0,1,2
dv.scatter('id', rc.ids, flatten=True)
print(dv['id'])


def sleep_here(count, t):
    """simple function that takes args, prints a short message, sleeps for a time, and returns the same args"""
    import sys
    import time

    print(f"hi from engine {id}")
    sys.stdout.flush()
    time.sleep(t)
    return count, t


amr = v.map(sleep_here, range(100), [random.random() for i in range(100)], chunksize=2)

pending = set(amr.msg_ids)
while pending:
    try:
        rc.wait(pending, 1e-3)
    except TimeoutError:
        # ignore timeouterrors, since they only mean that at least one isn't done
        pass
    # finished is the set of msg_ids that are complete
    finished = pending.difference(rc.outstanding)
    # update pending to exclude those that just finished
    pending = pending.difference(finished)
    for msg_id in finished:
        # we know these are done, so don't worry about blocking
        ar = rc.get_result(msg_id)
        print(f"job id {msg_id} finished on engine {ar.engine_id}")
        print("with stdout:")
        print('    ' + ar.stdout.replace('\n', '\n    ').rstrip())
        print("and results:")

        # note that each job in a map always returns a list of length chunksize
        # even if chunksize == 1
        for count, t in ar.get():
            print(f"  item {count}: slept for {t:.2f}s")
