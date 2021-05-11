#pragma once

#ifndef TRIE_HPP
#define TRIE_HPP

#include "defs.hpp"

struct trie_node {
    std::map<std::string, trie_node*> children;
    unsigned int value;
    unsigned int max_sid;
    unsigned int next_max;
    int res_sid;
    uint_vector* rid_list;
    uint_vector records;
    bool is_leaf;

    trie_node(unsigned int value) : value(value), max_sid(1), next_max(1), res_sid(-1), is_leaf(false) {}
};


struct trie {
    trie_node* root;

    trie() {
        root = new trie_node(0);
    }

    void insert(record& rec) const {
        trie_node* node = this->root;
        unsigned int lastElement = rec.elements.back();

        for (auto& el : rec.elements) {
            bool isLast = (el == lastElement);
            if (node->children.count(std::to_string(el)) > 0 && !isLast) {
                node = node->children.find(std::to_string(el))->second;
            } else if (node->children.count(std::to_string(el) + "'") > 0 && isLast) {
                node = node->children.find(std::to_string(el) + "'")->second;
            } else {
                trie_node* new_node = new trie_node(el);
                node->children[isLast ? std::to_string(el) + "'" : std::to_string(el)] = new_node;
                node = new_node;
            }
        }
        node->records.emplace_back(rec.id);
        node->is_leaf = true;
    }

    ~trie() = default;
};



#endif // TRIE_HPP