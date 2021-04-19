import math

TOTAL_BINARY_SEARCHES = 0


class Record:
    def __init__(self, rid, elements):
        self.rid = rid
        self.elements = elements


class TrieNode:
    def __init__(self, element):
        self.children = {}
        self.value = element
        self.max_sid = 1
        self.next_max = 1
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


def binary_search(lst, x):
    global TOTAL_BINARY_SEARCHES
    TOTAL_BINARY_SEARCHES = TOTAL_BINARY_SEARCHES + 1
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

    return successor, lst[successor]


def create_inverted_index(records, max_element):
    index = [[] for _ in range(0, max_element)]
    for rec in records:
        for el in rec.elements:
            index[el - 1].append(rec.rid)
    return index


def post_order_traverse(n, next_max, index):
    next_max = max(next_max, n.next_max)
    for cid in n.children:
        if n.children[cid].max_sid <= n.max_sid:
            n.children[cid] = post_order_traverse(n.children[cid], next_max, index)

    if n.is_leaf:
        n.max_sid = next_max
    else:
        n.max_sid = min([n.children[c].max_sid for c in n.children])

    if n.value != 'root':
        inverted_list = index[n.value - 1]
        pos, sid = binary_search(inverted_list, n.max_sid)
        is_last = len(inverted_list) - 1 == pos or pos == -1
        if sid == n.max_sid:
            n.next_max = math.inf if is_last else inverted_list[pos + 1]
            if n.is_leaf:
                n.rid_list = n.records
            else:
                n.rid_list = list(
                    set().union(*[n.children[c].rid_list for c in n.children if n.children[c].max_sid == n.max_sid]))
        else:  # not found
            n.next_max = math.inf if is_last else sid
            n.rid_list = []
    else:  # is root custom
        n.rid_list = list(
            set().union(*[n.children[c].rid_list for c in n.children if n.children[c].max_sid == n.max_sid]))
    return n


def cross_cutting_framework(records, index):
    ans = set()
    for r in records:
        max_sid = 1
        next_max = 1
        end = False
        while not end:
            count = 0
            # search inverted lists
            for el in r.elements:
                inverted_list = index[el - 1]
                pos, sid = binary_search(inverted_list, max_sid)
                end |= len(inverted_list) - 1 == pos or pos == -1
                if sid == max_sid:
                    count += 1
                    if not end:
                        next_max = inverted_list[pos + 1] if inverted_list[pos + 1] > next_max else next_max
                else:
                    next_max = sid if sid > next_max else next_max
                    break
            if count == len(r.elements):
                ans.add((r.rid, max_sid))
            max_sid = next_max
    return ans


if __name__ == '__main__':

    #query = [Record(1, {1, 2, 3, 4}), Record(2, {2, 3, 5}), Record(3, {1, 2, 5, 6}), Record(4, {1, 3, 5}), Record(5, {1, 3, 5}), Record(6, {1, 3, 5, 6})]
    #query = [Record(1, {1, 2, 3, 4}), Record(2, {2, 3, 5}), Record(3, {1, 2, 5, 6}), Record(5, {2, 3})]
    #query = [Record(1, {1, 3, 5}), Record(2, {1, 3, 5}), Record(3, {1, 3, 5, 6}), Record(4, {1}), Record(5, {1, 3, 5, 6})]
    query = [Record(1, {1, 2, 3, 4}), Record(2, {2, 3, 5}), Record(3, {1, 2, 5, 6})]
    dataset = [Record(1, {1, 3, 4, 5, 6}), Record(2, {1, 3, 5}), Record(3, {1, 2, 3, 4, 6}), Record(4, {2, 4, 5, 6}),
               Record(5, {2, 3, 4, 5, 6}), Record(6, {2, 3, 4, 6}), Record(7, {1, 2, 3, 6})]

    universe = 6

    tr = Trie()
    for q in query:
        tr.insert(q)
    inv_index = create_inverted_index(dataset, universe)

    bf_ans = set()
    for q in query:
        for d in dataset:
            if len(q.elements.intersection(d.elements)) == len(q.elements):
                bf_ans.add((q.rid, d.rid))

    print('Brute force: ', bf_ans)

    print('-----------')

    cross_ans = cross_cutting_framework(query, inv_index)

    print('Cross-cutting framework', cross_ans)
    print('Cross-cutting binary searches', TOTAL_BINARY_SEARCHES)
    print("Correct:", "True" if len(bf_ans ^ cross_ans) == 0 else "False")
    
    print('-----------')

    cross_cut_bs = TOTAL_BINARY_SEARCHES

    tree_ans = set()
    while tr.root.max_sid != math.inf:
        tr.root = post_order_traverse(tr.root, 1, inv_index)
        for r in tr.root.rid_list:
            tree_ans.add((r, tr.root.max_sid))

    print('TreeBased: ', tree_ans)
    print('TreeBased binary searches', TOTAL_BINARY_SEARCHES - cross_cut_bs)
    print("Correct:", "True" if len(bf_ans ^ tree_ans) == 0 else "False")

    print('-----------')
