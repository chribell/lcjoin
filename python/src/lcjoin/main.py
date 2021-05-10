#!/usr/bin/env python3

import typer
import lib
from timeit import default_timer as timer
from datetime import timedelta
import sys


def main(
    dataset: str = typer.Option("", help="Input dataset path"),
    query: str = typer.Option("", help="Input query path"),
    out: str = typer.Option("", help="Output path"),
    algo: str = typer.Option("lcjoin", help="Algorithm to run"),
    partitions: int = typer.Option(2, help="Number of partitions for LCJoin")
):
    read_start = timer()
    dataset, dataset_universe = lib.read_dataset(dataset)
    query, query_universe = lib.read_dataset(query)
    read_end = timer()

    universe = max(dataset_universe, query_universe)

    res = set()
    join_start = timer()
    if algo == "brute_force":
        res = lib.brute_force_join(query, dataset)
    elif algo == "tree_based":
        res = lib.tree_based_join(query, dataset, universe)
    elif algo == "lcjoin":
        res = lib.lcjoin(query, dataset, universe, partitions)
    else:
        typer.echo(f"Wrong algorithm given", err=True)
        exit(1)
    join_end = timer()

    typer.echo(f"Result count {len(res)}")
    typer.echo(f"Read time {timedelta(seconds=read_end-read_start)}")
    typer.echo(f"Join time {timedelta(seconds=join_end-join_start)}")

    if not out:
        out = "out.txt"
    with open(out, "w") as f:
        f.write("Q D\n")
        for pair in res:
            f.write(str(pair[0]) + " " + str(pair[1]) + "\n")


if __name__ == "__main__":
    sys.setrecursionlimit(2000)  # for larger tries
    typer.run(main)
