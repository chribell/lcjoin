import math
from collections import defaultdict
import heapq


class Record:
    def __init__(self, rid, elements):
        self.rid = rid
        self.elements = elements

    def __repr__(self):
        return "%s = %s" % (self.rid, self.elements)


class TrieNode:
    def __init__(self, element):
        self.children = {}
        self.value = element
        self.max_sid = 1
        self.next_max = 1
        self.res_sid = -1
        self.rid_list = []
        self.records = []
        self.is_leaf = False

    def __repr__(self):
        return "Value: %s | next_max: %s | max_sid: %s | rid_list: %s" % (
            self.value, self.next_max, self.max_sid, self.rid_list)


class Trie(object):
    def __init__(self):
        self.root = TrieNode("root")

    def insert(self, record):
        node = self.root
        last_el = list(record.elements)[-1]

        for el in record.elements:
            is_last = el == last_el
            if el in node.children and not is_last:
                node = node.children[el]
            elif str(el) + '\'' in node.children and is_last:
                node = node.children[str(el) + '\'']
            else:  # create node
                new_node = TrieNode(el)
                node.children[str(el) + '\'' if is_last else el] = new_node
                node = new_node
        node.records.append(record.rid)
        node.is_leaf = True


def read_dataset(filename):
    dataset = []
    max_element = 0
    rid = 1
    with open(filename, 'r') as f:
        for line in f:
            r = list(map(int, line.strip().split(' ')))
            if max_element < r[-1]:
                max_element = r[-1]
            dataset.append(Record(rid, set(r)))
            rid += 1
    return dataset, max_element


def index_binary_search(arr, x):
    low = 0
    high = len(arr) - 1
    mid = 0

    while low <= high:
        mid = (high + low) // 2
        if arr[mid] < x:
            low = mid + 1
        elif arr[mid] > x:
            high = mid - 1
        else:
            return mid

    return -1


def successor_binary_search(lst, x):
    start = 0
    end = len(lst) - 1
    successor = -1

    while start <= end:
        mid = (start + end) // 2
        if lst[mid] < x:
            start = mid + 1
        else:  # lst[mid] >= x:
            successor = mid
            end = mid - 1

    return successor, lst[successor] if len(lst) > 0 else -1


def create_inverted_index(records, max_element):
    index = [[] for _ in range(0, max_element)]
    for rec in records:
        for el in rec.elements:
            index[el - 1].append(rec.rid)
    return index


def post_order_traverse(n, next_max, res_sid, index, res):
    if n.is_leaf and n.max_sid == res_sid:
        for i in n.records:
            res.add((i, res_sid))

    next_max = max(next_max, n.next_max)
    for cid in n.children:
        if n.children[cid].max_sid <= n.max_sid:
            n.children[cid] = post_order_traverse(n.children[cid], next_max, res_sid, index, res)

    if n.is_leaf:
        n.max_sid = next_max
    else:
        n.max_sid = min([n.children[c].max_sid for c in n.children])

    if n.value != 'root' and n.max_sid != math.inf:
        inverted_list = index[n.value - 1]
        pos, sid = successor_binary_search(inverted_list, n.max_sid)
        if sid == n.max_sid:
            n.next_max = math.inf if len(inverted_list) - 1 == pos or pos == -1 else inverted_list[pos + 1]
            if n.is_leaf:
                n.rid_list = n.records
        else:  # not found
            n.next_max = math.inf if pos == -1 else sid
            n.rid_list = []
            n = post_order_traverse(n, next_max, res_sid, index, res)

    if n.value == 'root':
        n.res_sid = n.max_sid

    return n


def cross_cutting_framework(records, index):
    ans = set()
    for r in records:
        max_sid = 1
        end = False
        while not end:
            count = 0
            tmp = []
            # search inverted lists
            for el in r.elements:
                inverted_list = index[el - 1]
                pos = index_binary_search(inverted_list, max_sid)
                end |= len(inverted_list) - 1 == pos
                if len(inverted_list) - 1 >= (pos + 1):
                    tmp.append(inverted_list[pos + 1])
                if pos >= 0:
                    count += 1
                # TODO fix bug in case of early termination (deadlock behavior in some cases)
                #  Example:
                #  query = [Record(1, {1, 3, 5})]
                #  dataset = [Record(1, {1, 3, 4, 5, 6}), Record(2, {1, 3, 5}), Record(3, {1, 2, 3, 4, 6}),
                #   Record(4, {2, 4, 5, 6}), Record(5, {2, 3, 4, 5, 6}), Record(6, {2, 3, 4, 6}),
                #   Record(7, {1, 2, 3, 6})]
                # else:
                #     break
            if count == len(r.elements):
                ans.add((r.rid, max_sid))
            if tmp:
                max_sid = max(tmp)
    return ans


def brute_force_join(query, dataset):
    bf_ans = set()
    for q in query:
        for d in dataset:
            if len(q.elements.intersection(d.elements)) == len(q.elements):
                bf_ans.add((q.rid, d.rid))
    return bf_ans


def cross_cut_join(query, dataset, universe):
    inv_index = create_inverted_index(dataset, universe)
    return cross_cutting_framework(query, inv_index)


def tree_based_join(query, dataset, universe):
    tr = Trie()
    for q in query:
        tr.insert(q)
    inv_index = create_inverted_index(dataset, universe)

    tree_ans = set()
    while tr.root.max_sid != math.inf:
        tr.root = post_order_traverse(tr.root, 1, tr.root.res_sid, inv_index, tree_ans)

    return tree_ans


def lcjoin(query, dataset, universe):
    histogram = defaultdict(int)
    for q in query:
        histogram[next(iter(q.elements))] += 1

    frequencies = {k: v for k, v in sorted(histogram.items(), key=lambda item: item[1])}

    index = create_inverted_index(dataset, universe)

    lcjoin_ans = set()

    for i in frequencies:
        partition_query = [rec for rec in query if next(iter(rec.elements)) == i]

        trie = Trie()
        for q in partition_query:
            trie.insert(q)

        # TODO add global vs local index logic

        while trie.root.max_sid != math.inf:
            trie.root = post_order_traverse(trie.root, 1, trie.root.res_sid, index, lcjoin_ans)

    return lcjoin_ans
