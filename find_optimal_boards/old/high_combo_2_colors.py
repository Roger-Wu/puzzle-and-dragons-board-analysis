"""
WLOG, first orb must be in the top row and in the first 3 column
and no orb left to it

total combinations:
P(29, 11) / 2! / 3! / 3! / 3! +
P(28, 11) / 2! / 3! / 3! / 3! +
P(27, 11) / 2! / 3! / 3! / 3!
= 6.38 * 10^12

0 0 0 0 0 0
0 0 0 0 0 0
0 0 0 0 0 0
0 0 0 0 0 0
1 0 0 0 0 0

TODO: consider symmetry. if repeat, don't compute again
    combination -> a integer, each bit represent whether a sub-color orb is there
TODO: generalization
"""

from itertools import combinations, permutations, tee
import sys
# import operator as op
# from scipy.misc import comb, factorial
# from sympy.utilities.iterables import multiset_permutations
import time
from Board import Board


other_orb_colors = [1] * 12
combo_threshold = 8

row_size = 5
col_size = 6
orb_count = row_size * col_size
other_orb_count = len(other_orb_colors)
main_orb_count = orb_count - other_orb_count
other_orb_color_count = len(set(other_orb_colors))


def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)

def comb(n, r):
    r = min(r, n-r)
    res = 1
    for i in range(r):
        res *= (n - i)
        res //= (i + 1)
    return res

class unique_element:
    def __init__(self,value,occurrences):
        self.value = value
        self.occurrences = occurrences

def perm_unique(elements):
    eset=set(elements)
    listunique = [unique_element(i,elements.count(i)) for i in eset]
    u=len(elements)
    return perm_unique_helper(listunique,[0]*u,u-1)

def perm_unique_helper(listunique,result_list,d):
    if d < 0:
        yield tuple(result_list)
    else:
        for i in listunique:
            if i.occurrences > 0:
                result_list[d]=i.value
                i.occurrences-=1
                for g in  perm_unique_helper(listunique,result_list,d-1):
                    yield g
                i.occurrences+=1


def is_sorted(l):
    return all(l[i] <= l[i+1] for i in range(len(l)-1))

def is_sorted_permutation(p):
    # if the indeices of the first 1, 2, 3, ... is sorted
    return is_sorted([p.index(i+1) for i in range(other_orb_color_count)])

row_set = set(list(range(5)))
col_set = set(list(range(6)))

def calc_main_orb_max_combos(other_orb_positions):
    rows_with_other_orbs = set([p // 6 for p in other_orb_positions])
    cols_with_other_orbs = set([p % 6 for p in other_orb_positions])
    # rows_all_main_orbs = list(row_set - rows_with_other_orbs).sort()
    # cols_all_main_orbs = list(col_set - cols_with_other_orbs).sort()
    # lr = len(rows_all_main_orbs)
    # lc = len(cols_all_main_orbs)

    # number of rows with only main orbs
    lr = 5 - len(rows_with_other_orbs)
    # number of cols with only main orbs
    lc = 6 - len(cols_with_other_orbs)

    if lr == lc == 0:
        return main_orb_count // 3

    matched_main_orbs = lr * 6 + lc * 5 - lr * lc

    if lr > 0 and lc > 0:
        return 1 + (main_orb_count - matched_main_orbs) // 3
    else:
        # if lr > 0:
        #     lst = list(rows_with_other_orbs)
        # else:
        #     lst = list(cols_with_other_orbs)
        # lst.sort()

        # combos = 1
        # for idx in range(len(lst) - 1):
        #     if lst[idx] + 1 != lst[idx+1]:
        #         combos += 1

        # combos = lr + lc
        return lr + lc + (main_orb_count - matched_main_orbs) // 3


def calc_other_orb_max_combos(other_orb_positions, other_orb_color_permu):
    pass

# TODO: combine horizontal and vertical
def predict_combos_same_color_orbs(positions):
    rows = set()
    for p in positions:
        row = p // 6
        rows.add(row)
    if len(rows) == 5:
        return 6
    else:
        return len(rows) - 1

def predict_combos_diff_color_orbs(positions, colors):
    color_cols = [[], [], [], []]
    for p, c in zip(positions, colors):
        col = p % 6
        color_cols[c-1].append(col)

    combos = 0
    # different color orbs
    for cols in color_cols:
        cols.sort()
        if cols[0] == cols[1] == cols[2] or cols[0] == cols[1]-1 == cols[2]-2:
            combos += 1
    return combos

def main():
    color_perms = list(perm_unique(other_orb_colors))
    sorted_color_perms = [p for p in color_perms if is_sorted_permutation(p)]
    total_perms = len(sorted_color_perms)

    comb_counter = 0
    found = 0
    b = Board()

    # fixed_pos = (0, 1, 2)
    f = open('logs/orb-18-12_combo-8.txt', 'w')
    f.write('[\n')
    # fixed_count = len(fixed_pos)
    # fixed_max = max(fixed_pos)
    # total_combs = int(comb(30, 12))
    total_combs = comb(29, 11) + comb(28, 11) + comb(27, 11)

    print('total_combinations:', total_combs)
    print('total_permutations:', total_perms)
    print('total:', total_combs * total_perms)


    start = time.time()
    for c in combinations(range(30), 12):
        if c[0] == 3:
            break

        main_orb_max_combos = calc_main_orb_max_combos(c)
        # main_orb_max_combos = predict_combos_same_color_orbs(c)
        if main_orb_max_combos + 4 >= combo_threshold:
            for p in sorted_color_perms:
                # diff_color_combos = predict_combos_diff_color_orbs(c, p)
                # diff_color_combos = 4
                # max_combos = same_color_combos + diff_color_combos
                # if max_combos < combo_threshold:
                #     continue

                b.set_sparse_board(c, p)
                combos, main_combos = b.count_combos()
                if combos >= combo_threshold:
                    found += 1
                    f.write('{{id: {}, combos: {}, main_combos: {}, board: {}}},\n'.format(found, combos, main_combos, b.get_board_string()))

        comb_counter += 1
        if comb_counter % 10000 == 0:
            proportion = comb_counter / total_combs
            elapsed_time = time.time() - start
            remaining_time = elapsed_time / proportion * (1 - proportion)
            print('{:.4f} %, comb: {}, found: {}, elapsed: {:.2f}, remaining: {:.2f}'.format(
                proportion * 100,
                comb_counter,
                found,
                elapsed_time,
                remaining_time),
                end='\r')

    f.write(']\n')

    elapsed_time = time.time() - start
    print('total_combs: {}, combs: {}, found: {}, elapsed: {:.2f}'.format(
        total_combs,
        comb_counter,
        found,
        elapsed_time))
    # print(comb_counter)

    # print(list(permutations([1, 1, 2])))

    # print(list(perm_unique([1, 1, 2])))  # faster
    # print(list(multiset_permutations([1, 1, 2])))

def test():
    positions = range(12)
    print(calc_main_orb_max_combos(positions))
    print(predict_combos_same_color_orbs(positions))

if __name__ == '__main__':
    main()
    # test()