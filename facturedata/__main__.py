#!/usr/bin/env python3

import argparse
import json
import logging
import os
import sys
try:
    from .core import *
except ImportError:
    from core import *

parser = argparse.ArgumentParser()
parser.add_argument('-v', action="count", default=0)
parser.add_argument('--conf-dir', type=str)
parser.add_argument('--output-type', type=str, choices=['json', 'sql'])
parser.add_argument('--skip-targets', action="store_true")
parser.add_argument('--flexible-group-names', action="store_true")
args = parser.parse_args()

if args.v >= 2:
    logging.basicConfig(level=logging.DEBUG)
elif args.v >= 1:
    logging.basicConfig(level=logging.INFO)



if args.conf_dir:
    if not os.path.isdir(args.conf_dir):
        raise ConfError("conf-dir {} does not exist".format(args.conf_dir))
    sys.path.insert(0, args.conf_dir)
else:
    if not os.path.isfile("factureconf.py"):
        raise ConfError("Either put a factureconf.py file in this directory or set --conf-dir")
    else:
        sys.path.insert(0, os.getcwd())

import factureconf # noqa


def main():
    seq_for = {}

    logging.debug("setting up data")

    conf_tables = factureconf.conf_tables()

    d = factureconf.conf_data()

    d = normalize_structure(d)

    consistency_checks_or_immediately_die(d, flexible_group_names=args.flexible_group_names)

    logging.debug("generating data")

    d = enhance_with_generated_data(d, seq_for, conf_tables)

    d = add_table_defaults(d, conf_tables)

    d = combine_all_into_result(d)

    logging.debug("adding sql output")

    d = add_sql_output(d, conf_tables)

    logging.debug("annotating with target information")

    targets = factureconf.conf_targets()
    targets = annotate_targets_with_positional_data_from_file(targets)
    d = add_target_info(d, conf_tables, targets)

    if args.output_type and args.output_type == 'json':
        print(json.dumps(d, indent=4, sort_keys=True, default=str))

    if args.skip_targets:
        logging.debug("skipping exporting to targets because of --skip-targets")
    else:
        logging.debug("exporting to targets")
        if len(targets) < 1:
            raise ConfError(
                "You have no targets specified in the conf_targets function."
                " Use --skip-targets if that is intentional."
            )

        targets = annotate_targets_with_output_values(targets, d)
        write_to_actual_target_files(targets)


#############################################################################


def config_for(table):
    return factureconf.conf_tables()[table]


seq_for = None

if __name__ == '__main__':
    main()
