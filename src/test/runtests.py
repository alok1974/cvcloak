import os
import sys
import subprocess


def main():
    for root, dirs, files in os.walk(
            os.path.abspath(os.path.dirname(__file__))):
        for file in files:
            fp = os.path.join(root, file)
            if fp == __file__ or not file.startswith('test'):
                continue
            sys.stdout.write('Running tests for "{0}"\n'.format(fp))
            subprocess.call(['python', fp])
            sys.stdout.write('\n')


if __name__ == '__main__':
    main()
