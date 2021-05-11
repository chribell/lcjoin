#pragma once

#ifndef LIB_HPP
#define LIB_HPP

#include <algorithm>
#include "defs.hpp"
#include "trie.hpp"

int indexBinarySearch(const uint_vector& list, unsigned int x)
{
    int start = 0;
    int end = list.size() - 1;

    while (start <= end) {
        int mid = (start + end) / 2;
        if (list[mid] < x) {
            start = mid + 1;
        } else if (list[mid] > x) {
            end = mid - 1;
        } else {
            return mid;
        }
    }

    return -1;
}

int successorBinarySearch(const uint_vector& list, unsigned int x, int& sid)
{
    int start = 0;
    int end = list.size() - 1;
    int successor = -1;

    while (start <= end) {
        int mid = (start + end) / 2;
        if (list[mid] < x) {
            start = mid + 1;
        } else {
            successor = mid;
            end = mid - 1;
        }
    }

    if (list.size() > 0) {
        sid = (int) list[successor];
    } else {
        sid = - 1;
    }

    return successor;
}

inverted_index constructInvertedIndex(const records& records, unsigned int universe)
{
    inverted_index index(universe);
    for (auto& r : records) {
        for (auto& el : r.elements) {
            index[el - 1].emplace_back(r.id);
        }
    }
    return index;
}

void postOrderTraverse(trie_node* node, unsigned int nextMax, int resSid, const inverted_index& index, unsigned long& count)
{
    if (node->is_leaf && node->max_sid == resSid) {
        for (auto& r : node->records) {
            count++;
        }
    }

    nextMax = std::max(nextMax, node->next_max);

    for (auto&& child : node->children) {
        if (child.second->max_sid <= node->max_sid) {
            postOrderTraverse(child.second, nextMax, resSid, index, count);
        }
    }

    if (node->is_leaf) {
        node->max_sid = nextMax;
    } else {
        auto x = std::min_element(node->children.begin(), node->children.end(),
                                  [](const auto& l, const auto& r) { return l.second->max_sid < r.second->max_sid; });
        node->max_sid = x->second->max_sid;
    }

    if (node->value != 0 && node->max_sid != INT32_MAX) { // node it's not root and has not an inf max sid
        int sid = 0;
        int pos = successorBinarySearch(index[node->value - 1], node->max_sid, sid);

        if (sid == node->max_sid) {
            node->next_max = (pos == (index[node->value - 1].size() - 1)) || (pos == -1) ? INT32_MAX : index[node->value - 1][pos + 1];
        } else {
            node->next_max = (pos == -1) ? INT32_MAX : sid;
            postOrderTraverse(node, nextMax, resSid, index, count);
        }
    }

    if (node->value == 0) { // we are at root level
        node->res_sid = (int) node->max_sid;
    }
}

#endif // LIB_HPP