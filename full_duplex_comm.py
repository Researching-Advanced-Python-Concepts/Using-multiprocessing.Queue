# each worker process will have a reference to the input queue with
# jobs to consume and a reference to the output queue for the
# prospective solution.
# this references enable simultaneous 2-way communication betn workers
# and the main process, full-duplex communication
from dataclasses import dataclass
from into_chunks import Combinations, chunk_indices
from hashlib import md5
from string import ascii_lowercase

import argparse
import multiprocessing
import time
import queue


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
# when there's no matching solution, the loop will never stop becuz our
# workers are still alive, waiting for more jobs to process even after
# having consumed all of them, stuck on the queue_in.get() call, which is
# blocking