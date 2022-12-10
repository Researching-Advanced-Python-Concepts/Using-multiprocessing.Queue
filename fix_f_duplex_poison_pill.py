# since we know the no. of jobs to consume is known up front, we can tell
# the workers to shut down gracefully after draining the queue

# a typical pattern to request a thread or process stop working is by
# putting a special sentinel value at the end of the queue.
# when worker finds that sentinel, it'll do the necessary cleanup and
# escape the infinite loop.
# such sentinel is known as poison pill because it kills the worker

# it is rather tricky for multiprocessing module because of how it handles
# the global namespace
# it's probably safe to stick to a predefined value such as None, which
# has a known identity everywhere
from dataclasses import dataclass
from into_chunks import Combinations, chunk_indices
from hashlib import md5
from string import ascii_lowercase

import argparse
import multiprocessing
import time
import queue


POISON_PILL = None
# if we use a custom oject instance defined as a global variable, then
# each of our worker processes would have its own copy of that object
# with a unique identity.
# A sentinel object enqueued by one worker would be deserialized into an
# entirely new instance in another worker, having a diff. identity than
# its global variable. Ergo, we wouldn't be able to detect a poison pill
# in the queue

# we also need to take care of putting the poison pill back in the source
# queue after consuming it


@dataclass(frozen=True)
class Job:
    combinations: Combinations
    start_index: int
    stop_index: int
    
    # by using call we make objects of our class callable
    # now workers can call these jobs just like regular functions when
    # they receive them
    def __call__(self, hash_value):
        for index in range(self.start_index, self.stop_index):
            text_bytes = self.combinations[index].encode("utf-8")
            hashed = md5(text_bytes).hexdigest()
            if hashed == hash_value:
                return text_bytes.decode("utf-8")


class Worker(multiprocessing.Process):
    def __init__(self, queue_in, queue_out, hash_value):
        super().__init__(daemon=True)
        self.queue_in = queue_in
        self.queue_out = queue_out
        self.hash_value = hash_value

    def run(self):
        while True:
            job = self.queue_in.get()
            if job is POISON_PILL:
                # this give other workers a chance to consume the poison
                # pill. if we know exact np. of our workers we can 
                # enqueue that many poison pills, one for each of them.
                self.queue_in.put(POISON_PILL)
                # after consuming and returning the sentinel to the
                # queue, a worker breaks out of the infinite loop,
                # ending its life
                break
            if plaintext := job(self.hash_value):
                self.queue_out.put(plaintext)
                break


def main(args):
    t1 = time.perf_counter()
    queue_in = multiprocessing.Queue()
    queue_out = multiprocessing.Queue()
    
    workers = [
        Worker(queue_in, queue_out, args.hash_value)
        for _ in range(args.num_workers)
    ]
    
    for worker in workers:
        worker.start()

    for text_length in range(1, args.max_length + 1):
        combinations = Combinations(ascii_lowercase, text_length)
        for indices in chunk_indices(len(combinations), len(workers)):
            queue_in.put(Job(combinations, *indices))

    # adding poison pill as the last element in the input queue
    queue_in.put(POISON_PILL)
    
    while any(worker.is_alive() for worker in workers):
        try:
            # dequeue it from output queue
            solution = queue_out.get(timeout=0.1)
            if solution:
                t2 = time.perf_counter()
                print(f"{solution} (found in {t2 - t1:.1f}s")
                break
        except queue.Empty:
            pass
    else:
        print("Unable to find a solution")


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("hash_value")
    parser.add_argument("-m", "--max-length", type=int, default=6)
    parser.add_argument(
        "-w",
        "--num-workers",
        type=int,
        default=multiprocessing.cpu_count(),
    )
    return parser.parse_args()


if __name__ == "__main__":
    main(parse_args())