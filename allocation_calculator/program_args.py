# Native modules
import os
import sys


def gen_spec_paths(args):
    if args.data_dir is None:
        if args.adventures_path is None or args.funghis_path is None \
                or args.rewards_path is None:
            raise ValueError(
                'If you do not specify "data_dir", please specify'
                ' "adventures_path", "funghis_path" and "rewards_path"')
    else:
        SPEC_NAMES = ['adventures', 'funghis', 'rewards']
        for spec_name in SPEC_NAMES:
            arg_name = '{}_path'.format(spec_name)
            spec_file_name = '{}.yaml'.format(spec_name)
            if getattr(args, arg_name) is None:
                setattr(args, arg_name, os.path.join(
                    args.data_dir, spec_file_name))
            else:
                print('"{}" specified, will override "{}" in "data_dir"'.format(
                    arg_name, spec_file_name), file=sys.stderr)
    return args
