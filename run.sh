#!/bin/sh

#if use drive which if=ide, set root to /dev/sda1
#if use drive which if=virtio, set root to /dev/vda1

/usr/bin/qemu-system-x86_64 -nographic -drive file=rootfs.img,format=raw,index=0,if=virtio \
	-enable-kvm \
	-kernel arch/x86_64/boot/bzImage \
	-append "rw console=ttyS0 root=/dev/vda1 init=/bin/bash"
