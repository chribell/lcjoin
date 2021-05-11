#include <vector>
#include <algorithm>
#include <string>
#include <fmt/core.h>
#include <fmt/ranges.h>
#include <cxxopts.hpp>
#include "input.hpp"
#include "lib.hpp"
#include "timer.hpp"

typedef std::vector<std::pair<unsigned int, unsigned int>> frequency_pairs;

frequency_pairs countElementFrequency(records& query)
{
    std::map<unsigned int, unsigned int> frequencyMap;

    for(auto& r : query) {
        if (frequencyMap.find(r.elements[0]) == frequencyMap.end()) {
            frequencyMap[r.elements[0]] = 1;
        } else {
            frequencyMap[r.elements[0]]++;
        }
    }

    frequency_pairs pairs;

    for (auto& i : frequencyMap) {
        pairs.push_back(i);
    }

    // sort in ascending order
    std::sort(pairs.begin(), pairs.end(),
              [](const auto& a, const auto& b) { return a.second < b.second; });

    return pairs;
}


int main(int argc, char** argv)
{
    try {
        cxxopts::Options options(argv[0], "LCJoin: Set containment");

        options.add_options()
                ("query", "Input query file", cxxopts::value<std::string>())
                ("dataset", "Input dataset file", cxxopts::value<std::string>())
                ("help", "Print help");

        auto result = options.parse(argc, argv);

        if (result.count("help")) {
            fmt::print("{}\n", options.help());
            exit(0);
        }

        if (!result.count("query")) {
            fmt::print("ERROR: No input query given! Exiting...\n");
            exit(1);
        }

        if (!result.count("dataset")) {
            fmt::print("ERROR: No input dataset given! Exiting...\n");
            exit(1);
        }

        timer t;

        std::string queryPath = result["query"].as<std::string>();
        std::string datasetPath = result["dataset"].as<std::string>();
        unsigned int universe = 0;

        timer::Interval* readQuery = t.add("Read query");
        std::vector<record> query = readRecords(queryPath, universe);
        timer::finish(readQuery);

        timer::Interval* readDataset = t.add("Read dataset");
        std::vector<record> dataset = readRecords(datasetPath, universe);
        timer::finish(readDataset);

        timer::Interval* queryFrequencies = t.add("Count query frequency");
        frequency_pairs frequencies = countElementFrequency(query);
        timer::finish(queryFrequencies);

        timer::Interval* constructIndex = t.add("Construct global index");
        inverted_index  index = constructInvertedIndex(dataset, universe);
        timer::finish(constructIndex);

        unsigned long count = 0;

        for (auto i : frequencies) {
            records partitionQuery;
            for (auto& rec : query) {
                if (rec.elements[0] == i.first) {
                    partitionQuery.push_back(rec);
                }
            }

            timer::Interval* constructTree = t.add("Construct radix trie");
            trie* tr = new trie();
            for (auto& r : partitionQuery) {
                tr->insert(r);
            }
            timer::finish(constructTree);

            // TODO add global vs local index logic

            timer::Interval* joinTime = t.add("LCJoin");
            while (tr->root->max_sid != INT32_MAX) {
                postOrderTraverse(tr->root, 1, tr->root->res_sid, index, count);
            }
            timer::finish(joinTime);
        }

        t.print();

        fmt::print("┌{0:─^{1}}┐\n"
                   "|{2: ^{1}}|\n"
                   "└{3:─^{1}}┘\n", "Result count", 51, count, "");

        return 0;
    } catch (const cxxopts::OptionException& e) {
        fmt::print("Error parsing options: {}\n", e.what());
        return 1;
    }
}