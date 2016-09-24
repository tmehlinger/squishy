import os
from subprocess import call


if __name__ == '__main__':
    if 'CIRCLECI' in os.environ:
        print('running coveralls')
        rc = call('coveralls')
        raise SystemExit(rc)
    print('NOT running coveralls')
