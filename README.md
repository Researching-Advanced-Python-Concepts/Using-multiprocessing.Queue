# Using-multiprocessing.Queue

Using multiprocessing.Queue for Interprocess Communication (IPC)

## What we'll do?

- Simulate a computationally intensive task by trying to reverse an MD5 hash value of a short text using the brute-force approach.
- There are better ways to solve this problem, both algorithmically and programmatically, running multiple processes in parallel will reduce the processing time by a noticable amount.

## Multiprocessing module

- `multiprocessing.JoinableQueue` extends the `multiprocessing.Queue` class by adding `.task_done()` and `.join()` methods, allowing us to wait until all enqueued tasks have been processed.
- if we don't need that feature we can use `multiprocessing.Queue`
- `multiprocessing.SimpleQueue` is a separate, significantly streamlined class that only has `.get()`, `.put()` and `.empty()` methods

## Things to keep in mind

1. Sharing a resource, such as a queue, betn os processes is much more expensive and limited than sharing betn threads.
   - Unlike threads, processes don't share a common memory region, so data must be marshaled and unmarshaled (packed and unpacked) at both ends everytime we pass a message from one process to another.

2. Python uses pickle module for data serialization which doesn't handle every data type and is relatively slow and insecure.

=> So we should only conside multiple processes when the performance improvements by running our code in parallel can offset the additional data serialization and bootstrapping overhead.
