# lets divide the whole set of letter combinations into a few smaller
# disjoint subsets.
# to ensure that workers don't waste time doing work that's already been
# done by another worker, the sets can't have any overlap
import time
from hashlib import md5
from string import ascii_lowercase

def chunk_indices(length, num_chunks):
    # a total length of 20 divided into 6 chunks yields
    # elements that alternate betn 3 and 4 elements
    start = 0
    while num_chunks > 0:
        num_chunks = min(num_chunks, length)
        chunk_size = round(length / num_chunks)
        yield start, (start := start + chunk_size)
        length -= chunk_size
        num_chunks -= 1 


class Combinations:
    def __init__(self, alphabet, length):
        self.alphatbet = alphabet
        self.length = length
    
    def __len__(self):
        # 26 ** 2 possibility for 2 letters combo
        return len(self.alphatbet) ** self.length
    
    def __getitem__(self, index):
        if index >= len(self):
            raise IndexError
        # formula below determine the character at a given position in a
        # combination specified by an index
        # letters on the right change most and letter on left the least
        return "".join(
            self.alphatbet[
                (index // len(self.alphatbet) ** i) % len(self.alphatbet)
            ]
            for i in reversed(range(self.length))
        )


def reverse_md5(hash_value, alphabet=ascii_lowercase, max_length=6):
    for length in range(1, max_length + 1):
        for combination in Combinations(alphabet, length):
            text_bytes = "".join(combination).encode("utf-8")
            hashed = md5(text_bytes).hexdigest()
            if hashed == hash_value:
                return text_bytes.decode("utf-8")

# for start, stop in chunk_indices(20, 6):
#     print(len(r := range(start, stop)), r)


def main():
    t1 = time.perf_counter()
    text = reverse_md5("a9d1cbf71942327e98b40cf5ef38a960")
    print(f"{text} (found in {time.perf_counter() - t1:.1f}s)")


if __name__ == "__main__":
    main()

# replacing built-in functions implemented in C with a pure Python one
# and doing some calculations in Python makes the code an order of
# magnitude slower