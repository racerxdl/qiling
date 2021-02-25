#!/usr/bin/env python3
# 
# Cross Platform and Multi Architecture Advanced Binary Emulation Framework
#

import sys, unittest, subprocess, string, random, os

from unicorn import UcError, UC_ERR_READ_UNMAPPED, UC_ERR_FETCH_UNMAPPED

sys.path.append("..")
from qiling import *
from qiling.const import *
from qiling.exception import *
from qiling.os.posix import syscall
from qiling.os.mapper import QlFsMappedObject
from qiling.os.posix.stat import Fstat
from qiling.os.const import *
from qiling.os.linux.fncc import linux_kernel_api

class ELF_KO_Test(unittest.TestCase):

    def test_demigod_m0hamed_x86(self):
        @linux_kernel_api(params={
            "format": STRING,
        })        
        def my_printk(ql, address, params):
            print("\n")
            print("=" * 40)
            print(" Enter into my_printk mode")
            print("=" * 40)
            print("\n")
            self.set_api_myprintk = params["format"]
            return 0

        ql = Qiling(["../examples/rootfs/x86_linux/kernel/m0hamed_rootkit.ko"],  "../examples/rootfs/x86_linux", output="disasm")
        try:
            procfile_read_func_begin = ql.loader.load_address + 0x11e0
            procfile_read_func_end = ql.loader.load_address + 0x11fa
            ql.set_api("printk", my_printk)            
            ql.run(begin=procfile_read_func_begin, end=procfile_read_func_end)
        except UcError as e:
            print(e)
            sys.exit(-1)
        self.assertEqual("DONT YOU EVER TRY TO READ THIS FILE OR I AM GOING TO DESTROY YOUR MOST SECRET DREAMS", self.set_api_myprintk)            
        del ql

    def test_demigod_hello_x8664(self):
        def my_onenter(ql, address, params):
            print("\n")
            print("=" * 40)
            print(" Enter into my_onenter mode")
            print("params: %s" % params)
            print("=" * 40)
            print("\n")
            self.set_api_onenter = params["format"]
            return address, params
        
        ql = Qiling(["../examples/rootfs/x8664_linux/kernel/hello.ko"],  "../examples/rootfs/x8664_linux", output="disasm")
        try:
            procfile_read_func_begin = ql.loader.load_address + 0x1064
            procfile_read_func_end = ql.loader.load_address + 0x107e
            ql.set_api("printk", my_onenter, QL_INTERCEPT.ENTER)
            ql.run(begin=procfile_read_func_begin, end=procfile_read_func_end)
        except UcError as e:
            print(e)
            sys.exit(-1)
        self.assertEqual("\x016Hello, World: %p!\n", self.set_api_onenter)            
        del ql

    def test_demigod_hello_mips32(self):
        def my_onexit(ql, address, params):
            print("\n")
            print("=" * 40)
            print(" Enter into my_exit mode")
            print("params: %s" % params)
            print("=" * 40)
            print("\n")
            self.set_api_onexit = params["format"]

        ql = Qiling(["../examples/rootfs/mips32_linux/kernel/hello.ko"],  "../examples/rootfs/mips32_linux", output="debug")
        begin = ql.loader.load_address + 0x1060
        end = ql.loader.load_address + 0x1084
        ql.set_api("printk", my_onexit, QL_INTERCEPT.EXIT)
        ql.run(begin=begin, end=end)

        self.assertEqual("\x016Hello, World!\n", self.set_api_onexit)
        del ql


if __name__ == "__main__":
    unittest.main()
