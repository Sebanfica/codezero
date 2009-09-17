#! /usr/bin/env python2.6
# -*- mode: python; coding: utf-8; -*-
#
#  Codezero -- a microkernel for embedded systems.
#
#  Copyright © 2009  B Labs Ltd
#
import os, sys, shelve, subprocess
from os.path import join

PROJRELROOT = '../../'

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), PROJRELROOT)))

from config.projpaths import *
from config.configuration import *

# Convert address from python literal to numeric value
def address_remove_literal(address):
    value = hex(int(address, 16) - 0xf0000000)
    if value[-1] in ['l', 'L']:
        value = value[:-1]
    return value

ksym_header = \
'''
/*
 * %s autogenerated from %s.
 * by %s
 *
 * This file is included by the loader sources so that any
 * kernel symbol address can be known in advance and stopped
 * at by debuggers before virtual memory is enabled.
 */
'''

assembler_symbol_definition = \
'''
.section .text
.align 4
.global %s
.type %s, function
.equ %s, %s
'''

def generate_ksym_to_loader(target_path, source_path):
    symbols = ['break_virtual']
    with open(target_path, 'w') as asm_file:
        asm_file.write(ksym_header % (target_path, source_path, sys.argv[0]))
        for symbol in symbols:
            process = subprocess.Popen('arm-none-eabi-objdump -d ' + \
                                        source_path + ' | grep "<' + \
                                        symbol + '>"', shell=True, \
                                        stdout=subprocess.PIPE)
            assert process.wait() == 0
            address, name = process.stdout.read().split()
            assert '<' + symbol + '>:' == name
            asm_file.write(assembler_symbol_definition % \
                           (symbol, symbol, symbol, \
                            address_remove_literal(address)))

decl_sect_asm = \
'''
.align 4
.section %s
.incbin "%s"
'''


def generate_image_S(target_path, images):
    kern_fname = 'kernel.elf'
    conts_fname = 'containers.elf'
    fbody = ''
    with open(target_path, 'w+') as images_S:
        for img in images:
            print os.path.basename(img.path)
            if os.path.basename(img.path) == kern_fname:
                fbody += decl_sect_asm % ('.kernel', img)
            if os.path.basename(img.path) == conts_fname:
                fbody += decl_sect_asm % ('.containers', img)
        images_S.write(fbody)

if __name__ == "__main__":
    if len(sys.argv) == 1:
        generate_ksym_to_loader(join(PROJROOT, 'loader/ksyms.S'), \
                                join(BUILDDIR, 'kernel.elf'))
    elif len(sys.argv) == 3:
        generate_ksym_to_loader(sys.argv[1], sys.argv[1])
    else:
        print "Usage: %s <asm filename> <kernel image filename>" % sys.argv[0]

