kernel-test-env-maker
=====================

Introduction
------------
Create a temp qemu image for test the lastest linux kernel.
Tested on ubuntu 16.04 x86_64


files
-----
```
config.qemu-x86_64	the kernel config file can be used as the basic config when use qemu-x86_64
format.sh		format the rootfs rootfs.img
genroot.py		all local files to the rootfs
mount.sh		mount the rootfs
README.md		this file
run.sh			start virtual machine with current kernel
umount.sh		umount the rootfs
```

quick start
-----------
put all files to root of kernel source tree
```
>cp config.qemu-x86_64 .config
>make oldconfig
>make menuconfig 
do your own config
>make

>dd if=/dev/zero of=rootfs.img seek=<the size you like> bs=1024 count=0
>./format.sh
>fdisk rootfs.img
>mkdir rootfs
>./mount.sh
>./genroot.py
>./umount.sh
>./run.sh
```

and read the script for all the detail, make your own change.


Appendix
--------

### perf dependent lib (in Ubuntu 16.04) ###
libdwarf-dev libbfd-dev libelf-dev libnuma-dev libunwind-dev zlib1g-dev
lblzma-dev ibpfm4-dev libdw-dev libaudit-dev libssl-dev libslang2-dev
libgtk2.0-dev libperl-dev binutils-dev libiberty-dev libpython-dev
