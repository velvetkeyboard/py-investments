import argparse
from sync_real_estate_investment_funds import sync as sync_reif


class BaseAction(argparse.Action):

    def __init__(self, **kwargs):
        super(BaseAction, self).__init__(**kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        self.cmd(namespace)

    def cmd(self, namespace):
        raise NotImplementedError(_('.cmd() not defined'))


class SyncAction(BaseAction):
    def cmd(self, namespace):
        # print(namespace)
        if namespace.entity == 'reif':
            sync_reif(namespace.mode)


class GenAction(BaseAction):
    def cmd(self, namespace):
        print(namespace)


def get_args():
    prsr = argparse.ArgumentParser(
        prog='investments',description='investments cli')
    sb_prsr = prsr.add_subparsers()  # (help=argparse.SUPPRESS)

    sync_prsr = sb_prsr.add_parser('sync', help='%(prog)s sync base json')
    sync_prsr.add_argument('-e', '--entity', help='Entity name')
    sync_prsr.add_argument('-m', '--mode', help='[f]ile or [d]atabase')
    sync_prsr.add_argument('run', nargs=0, action=SyncAction, help=argparse.SUPPRESS)

    gen_prsr = sb_prsr.add_parser('gen', help='%(prog)s generate files')
    gen_prsr.add_argument('-f', '--format', help='Format: csv, xml')
    gen_prsr.add_argument('run', nargs=0, action=GenAction, help=argparse.SUPPRESS)

    args = prsr.parse_args()
    return args


def main():
    args = get_args()
    # print(args)


if __name__ == '__main__':
    main()