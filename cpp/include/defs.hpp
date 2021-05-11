#pragma once

#ifndef DEFS_HPP
#define DEFS_HPP

#include <vector>

typedef std::vector<unsigned int> uint_vector;
typedef std::vector<uint_vector> inverted_index;
typedef std::vector<std::pair<unsigned int, unsigned int>> result_set;

struct record {
    unsigned int id;
    uint_vector elements;
    record(unsigned int id, uint_vector elements) : id(id), elements(std::move(elements)) {}
};

typedef std::vector<record> records;

#endif // DEFS_HPP