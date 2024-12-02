'''
Hash Function Analysis for CS109, Fall 2024
By: Julian Reed

This file contains the code for my extra credit project, which uses entropy to compare the efficacy of a given hash function.
Specifications for this hash function:
- Must convert from a string to an int

Specifications about the analysis:
- Assumes a hash function relying on separate chaining to resolve collisions instead of linear probing
- Chose to make hash table the size [desired size]. It could also be plausible to make this 1.5x or even 2x the size of the amount of inputs (which is desired size)

Resources:
https://docs.python.org/3/library/hashlib.html 
ChatGPT
https://web.stanford.edu/class/archive/cs/cs106b/cs106b.1244/lectures/23-hashing/
'''

import math
import hashlib
from itertools import product
import string

# helper function to generate a specified number of strings to hash, all differing from the previous by adding the next letter
# in lowercase a-z, written by ChatGPT
def generate_letter_combinations(desired_size):
    count = 0
    length = 0
    while (True):
        length += 1
        for combo in product(string.ascii_lowercase, repeat=length):
            yield ''.join(combo)
            count += 1
            if count >= desired_size:
                return

# helper function to convert chars to ints using ASCII values, based on distance from lowercase a
def custom_char_to_int(c) -> int:
    return ord(c) - ord('a') 

def conduct_analysis(input_hash_function, desired_size):
    # get baseline values from predefined hash functions
    print("Analyzing SHA256...")
    SHA256_stats = {}
    analyze_function(SHA256, desired_size, SHA256_stats)
    print("Analyzing SDBM...")
    SDBM_stats = {}
    analyze_function(SDBM, desired_size, SDBM_stats)
    print("Analyzing basic hash function...")
    basic_stats = {}
    analyze_function(basic, desired_size, basic_stats)
    # then test the user's
    print("Analyzing user's hash function...")
    user_function_stats = {}
    analyze_function(input_hash_function, desired_size, user_function_stats)
    # print out relevant comparison data
    all_stats = {'SHA256':SHA256_stats, 'SDBM':SDBM_stats, 'basic':basic_stats, 'user_function':user_function_stats}
    compare_stats(all_stats)

# helper function to compare the user's hash function in comparison to  the baseline functions
def compare_stats(all_stats):
    # get percentage performance for each stat in user_function_stats
    for stat in all_stats['user_function']:
        if stat == 'pmf':
            continue
        print(f"Current stat: {stat}")
        # iterate through each function, skipping the user
        for function in all_stats:
            current_function = all_stats[function]
            if function != 'user_function':
                print(f"user function is {round(all_stats['user_function'][stat] / current_function[stat], 5)}x larger than {function}")
        print("")
    
    # print all of the stats for each function 
    for function in all_stats:
        print(f"stats for {function}:")
        print_stats(all_stats[function])
        print("")

# helper function to print out stats for a given hash function
def print_stats(function_stats):
    print(f"distance from uniform = {function_stats['distribution difference']}")
    print(f"number of collisions = {function_stats['collisions']}")
    print(f"expected difference from previous string = {function_stats['expected difference per input']}")

# helper function to conduct analysis of a given hash function, with a specified number of values
def analyze_function(hash_function, desired_size, function_stats):
    pmf_stats = {'tot_dist_from_prev':0, 'num_collisions':0}
    hash_pmf = build_pmf(hash_function, desired_size, pmf_stats)
    # normalize this pmf
    for i in range(desired_size):
        hash_pmf[i] = hash_pmf[i] / desired_size
    # test for condition 2: hash function should be uniform
    function_stats['pmf'] = hash_pmf
    function_stats['distribution difference'] = dist_from_uniform(hash_pmf)
    # test for condition 3: function should produce a large range of values (we want to avoid collisions)
    function_stats['collisions'] = pmf_stats['num_collisions']
    # test for condition 4: functions should produce very difference hash codes for similar inputs
    function_stats['expected difference per input'] = pmf_stats['tot_dist_from_prev'] / desired_size

# this helper function builds a PMF from a given hash function, using a generic list of inputs of the specified size
def build_pmf(hash_function, desired_size, state) -> list:
    prev = float('-inf')
    dist_tracker = 0
    collision_count = 0
    count = 0
    # construct a list of desired size representing the PMF of this hash function
    pmf = [0] * desired_size
    for word_to_hash in generate_letter_combinations(desired_size):
        count += 1
        result = hash_function(word_to_hash)
        hashed = result % desired_size
        # detect if we have a collision
        if pmf[hashed] != 0:
            collision_count += 1
        # update PMF
        pmf[hashed] += 1
        # update distance from previous
        if prev != float('-inf'):
            dist_tracker += abs(hashed - prev)
        prev = hashed
    state['num_collisions'] = collision_count
    state['tot_dist_from_prev'] = dist_tracker
    return pmf

# this helper function determines the difference from the given PMF (created from our hash function) and a uniform distribution,
# which is the ideal
def dist_from_uniform(hash_pmf) -> int:
    divergence = 0
    # probability of a uniform will be the same every time
    pr_uni = 1 / len(hash_pmf)
    for i in range(len(hash_pmf)):
        pr_hash = hash_pmf[i]
        # skip if pr_hash is 0
        if pr_hash == 0: 
            continue
        else:
            excess_surprise = math.log(pr_hash / pr_uni)
        divergence += excess_surprise * pr_hash
    return divergence

# write user's hash function here
def basic(s) -> int:
    tot = 0
    for char in s:
        tot += custom_char_to_int(char)
    return tot

# write user's hash function here, this one was generated with ChatGPT
def custom_hash_function(s) -> int:
    return sum((i + 1) * ord(char) for i, char in enumerate(s))

def SDBM(s) -> int:
    # written by ChatGPT
    hash_value = 0
    for char in s:
        # hash(i) = hash(i - 1) * 65599 + char
        hash_value = ord(char) + (hash_value << 6) + (hash_value << 16) - hash_value
        # Ensures hash_value stays within a 32-bit unsigned integer range
        hash_value &= 0xFFFFFFFF
    return hash_value

# modified approach to SHA256 to fit this processors' requirements: converting characters in the encoded string to
# ints (in string format), then converting this entire resulting string to an int
def SHA256(x) -> int:
    hashed_string = hashlib.sha256(x.encode('UTF-8')).hexdigest()
    no_chars = ''
    for c in hashed_string:
        if c.isdigit():
            no_chars += c
        else:
            no_chars +=  str(custom_char_to_int(c))
    return int(no_chars)

def main():
    conduct_analysis(custom_hash_function, 100000)


if __name__ == '__main__':
    main()