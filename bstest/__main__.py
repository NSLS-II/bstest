#!/usr/bin/env python3

import bstest
import bstest._utils as UTILS
import argparse
import pytest
import os

def parse_args():
    parser = argparse.ArgumentParser(description='A utility for ' \
                        'leveraging bluesky automation for EPICS device testing')

    parser.add_argument('-p', '--prefix', 
                        help='Specifies the prefix for an existing IOC to test against.')

    args = vars(parser.parse_args())
    return args


def get_welcome_text():
    out_txt =  f'+{"-" * 64}+\n'
    out_txt += f'+ bstest - Version: {bstest.__version__:<45}+\n'
    out_txt += f'+ {bstest.__copyright__:<63}+\n'
    out_txt += f'+ {UTILS.get_environment():<63}+\n'
    out_txt += f'+ {"This software comes with NO warranty!":<63}+\n'
    out_txt += f'+{"-" * 64}+\n'
    return out_txt    

def main():
    args = parse_args()
    print(get_welcome_text())


    bstest.EXTERNAL_PREFIX = args['prefix']
    pytest.main(['-x', '.'])

if __name__ == '__main__':
    main()
