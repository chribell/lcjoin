#include <vector>
#include <algorithm>
#include <string>
#include <fmt/core.h>
#include <fmt/ranges.h>
#include <cxxopts.hpp>
#include "input.hpp"
#include "lib.hpp"
#include "timer.hpp"


int main(int argc, char** argv) {
    try {

        cxxopts::Options options(argv[0], "TreeBased Set containment");

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

        timer::Interval* constructTree = t.add("Construct radix trie");
        trie* tr = new trie();
        for (auto& r : query) {
            tr->insert(r);
        }
        timer::finish(constructTree);

        timer::Interval* constructIndex = t.add("Construct inverted index");
        inverted_index  index = constructInvertedIndex(dataset, universe);
        timer::finish(constructIndex);

        unsigned long count = 0;

        timer::Interval* joinTime = t.add("TreeBased Join");

        while (tr->root->max_sid != INT32_MAX) {
            postOrderTraverse(tr->root, 1, tr->root->res_sid, index, count);
        }

        timer::finish(joinTime);

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