#! /usr/bin/env python2.6
# -*- mode: python; coding: utf-8; -*-
#
#  Codezero -- a microkernel for embedded systems.
#
#  Copyright © 2009  B Labs Ltd
#
import os, sys, shelve
from os.path import join

PROJRELROOT = '../../'

SCRIPTROOT = os.path.abspath(os.path.dirname("."))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), PROJRELROOT)))

from config.projpaths import *
from config.configuration import *


containers_assembler_body = \
'''
.align 4
.section .cont.%d
.incbin "%s"
'''

containers_lds_start = \
'''/*
 * Autogenerated linker script that packs all containers
 * in a single image.
 *
 * Copyright (C) 2009 B Labs Ltd.
 */

SECTIONS
{'''

containers_lds_body = \
'''
	.cont.%d : { *(.cont.%d) }'''

containers_lds_end = \
'''
}
'''

class AllContainerPacker:
    def __init__(self, image_list, container_list):
        self.cont_images_in = image_list
        self.cont_images_in.sort()
        self.containers = container_list

        self.CONTAINERS_BUILDDIR = join(PROJROOT, 'build/conts')
        self.containers_lds_out = join(self.CONTAINERS_BUILDDIR, \
                                      'containers.lds')
        self.containers_S_out = join(self.CONTAINERS_BUILDDIR, 'containers.S')
        self.containers_elf_out = join(self.CONTAINERS_BUILDDIR, \
                                      'containers.elf')

    def generate_container_S(self, target_path):
        with open(target_path, 'w+') as f:
            file_body = ""
            img_i = 0
            for img in self.cont_images_in:
                file_body += containers_assembler_body % (img_i, img)
                img_i += 1

            f.write(file_body)

    def generate_container_lds(self, target_path):
        with open(target_path, 'w+') as f:
            img_i = 0
            file_body = containers_lds_start
            for img in self.cont_images_in:
                file_body += containers_lds_body % (img_i, img_i)
                img_i += 1
            file_body += containers_lds_end
            f.write(file_body)

    def pack_all(self):
        self.generate_container_lds(self.containers_lds_out)
        self.generate_container_S(self.containers_S_out)
        os.system("arm-none-linux-gnueabi-gcc " + "-nostdlib -o %s -T%s %s" \
                  % (self.containers_elf_out, \
                     self.containers_lds_out,
                     self.containers_S_out))

        # Return the final image to calling script
        return self.containers_elf_out

    def clean(self):
        if os.path.exists(self.containers_elf_out):
            shutil.rmtree(self.containers_elf_out)
        if os.path.exists(self.containers_lds_out):
            shutil.rmtree(self.containers_lds_out)
        if os.path.exists(self.containers_S_out):
            shutil.rmtree(self.containers_S_out)

if __name__ == "__main__":
    all_cont_packer = AllContainerPacker([], [])
