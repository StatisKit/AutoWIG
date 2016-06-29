import os
from argparse import ArgumentParser, RawTextHelpFormatter
import subprocess

def bootstrap_script(args):
    """Compute the minimal boostrap number"""
    subprocess.call(['scons', 'autowig', '-c'])
    subprocess.call(['scons -c'])
    subprocess.call(['scons'] + args.scons)
    subprocess.call(['scons autowig'] + args.scons)
    bootstrap = 0
    while

