# Copyright 2013-2014 The Rust Project Developers. See the COPYRIGHT
# file at the top-level directory of this distribution and at
# http://rust-lang.org/COPYRIGHT.
#
# Licensed under the Apache License, Version 2.0 <LICENSE-APACHE or
# http://www.apache.org/licenses/LICENSE-2.0> or the MIT license
# <LICENSE-MIT or http://opensource.org/licenses/MIT>, at your
# option. This file may not be copied, modified, or distributed
# except according to those terms.

import os
import sys
import subprocess
import itertools
from os import path

f = open(sys.argv[1], 'wb')

components = sys.argv[2].split(' ')
components = [i for i in components if i]  # ignore extra whitespaces
enable_static = sys.argv[3]
llconfig = sys.argv[4]

f.write("""// Copyright 2013 The Rust Project Developers. See the COPYRIGHT
// file at the top-level directory of this distribution and at
// http://rust-lang.org/COPYRIGHT.
//
// Licensed under the Apache License, Version 2.0 <LICENSE-APACHE or
// http://www.apache.org/licenses/LICENSE-2.0> or the MIT license
// <LICENSE-MIT or http://opensource.org/licenses/MIT>, at your
// option. This file may not be copied, modified, or distributed
// except according to those terms.

// WARNING: THIS IS A GENERATED FILE, DO NOT MODIFY
//          take a look at src/etc/mklldeps.py if you're interested
""")

def run(args):
    proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = proc.communicate()

    if err:
        print("failed to run llconfig: args = `{}`".format(args))
        print(err)
        sys.exit(1)
    return out

# LLVM version
version = run([llconfig, '--version']).strip()

# LLVM libs
if version < '3.5':
    args = [llconfig, '--libs']
else:
    args = [llconfig, '--libs', '--system-libs']
args.extend(components)
libs = run(args)

# LLVM ldflags
ldflags = run([llconfig, '--ldflags'])

# C++ runtime library
cxxflags = run([llconfig, '--cxxflags'])

for target in sys.argv[5:]:
    f.write("\n")

    arch, os = target.split('-', 1)
    arch = 'x86' if arch == 'i686' or arch == 'i386' else arch
    if 'darwin' in os:
        os = 'macos'
    elif 'linux' in os:
        os = 'linux'
    elif 'freebsd' in os:
        os = 'freebsd'
    elif 'dragonfly' in os:
        os = 'dragonfly'
    elif 'android' in os:
        os = 'android'
    elif 'win' in os or 'mingw' in os:
        os = 'windows'
    cfg = [
        "target_arch = \"" + arch + "\"",
        "target_os = \"" + os + "\"",
    ]

    f.write("#[cfg(all(" + ', '.join(cfg) + "))]\n")

    # LLVM libs
    for lib in libs.strip().replace("\n", ' ').split(' '):
        lib = lib.strip()[2:] # chop of the leading '-l'
        f.write("#[link(name = \"" + lib + "\"")
        # LLVM libraries are all static libraries
        if 'LLVM' in lib:
            f.write(", kind = \"static\"")
        f.write(")]\n")

    # llvm-config before 3.5 didn't have a system-libs flag
    if version < '3.5':
      if os == 'win32':
        f.write("#[link(name = \"imagehlp\")]")

    # LLVM ldflags
    for lib in ldflags.strip().split(' '):
        if lib[:2] == "-l":
            f.write("#[link(name = \"" + lib[2:] + "\")]\n")

    # C++ runtime library
    if enable_static == '1':
      assert('stdlib=libc++' not in cxxflags)
      f.write("#[link(name = \"stdc++\", kind = \"static\")]\n")
    else:
      if 'stdlib=libc++' in cxxflags:
        f.write("#[link(name = \"c++\")]\n")
      else:
        f.write("#[link(name = \"stdc++\")]\n")

# Attach everything to an extern block
f.write("extern {}\n")
