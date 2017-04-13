#!/usr/bin/python

import os
import re
import argparse

def app_exit(ret=0):
	if ret==0: print "complete!"
	else: print "fail with ", ret
	exit(ret)

elfs_to_copy="busybox bash ls mount less mkdir hostname cp mv ifconfig \
        vi sh true cat echo lsmod insmod modprobe rmmod vi rm mknod sshd ssh screen \
        dhclient ln tftp ping ip chown chmod strace which \
        /lib/x86_64-linux-gnu/libnss_files.so.2"
bb_links="getty login init id" 
kernel_elfs_to_copy="tools/perf/perf tools/perf/perf-archive"
dirs_to_mk='proc sys root mnt home/kenny dev tmp var'

#main start
#parse command line options
parser = argparse.ArgumentParser(description='Gernerate a rootfs for qemu debug')
parser.add_argument("-o", "--output_dir", type=str, default="rootfs")
parser.add_argument("-d", "--dry_run", action="store_true", default=False)
args=parser.parse_args()

cfg_files=[
["/etc/init.d/rc","""#!/bin/sh
PATH=/sbin:/usr/sbin:/bin:/usr/bin
export PATH
umask 022

mount /proc
mount /sys
mkdir -p /sys/kernel/debug
mount /sys/kernel/debug
hostname --file /etc/hostname
ifconfig eth0 up
ifconfig lo 127.0.0.1 netmask 255.0.0.0
dhclient eth0 &

"""],

["/etc/fstab","""procfs	/proc	proc	rw	0	0
sysfs	/sys	sysfs	rw	0	0
debugfs /sys/kernel/debug debugfs rw 0 0
"""],

["/root/.profile", """USER=`id -un`
LOGNAME=$USER
HOSTNAME=`/bin/hostname`
PS1="[\u@\h:\W]# "
PATH=/sbin:/usr/sbin:/bin:/usr/bin
export USER LOGNAME PS1 PATH
"""],

["/etc/hosts", """127.0.0.1 localhost
10.0.2.2 host
10.0.2.15 guest
"""],

["/etc/hostname", "debughost"],

["/etc/inittab", """::sysinit:/etc/init.d/rc
::respawn:/bin/getty -L ttyS0 115200
"""],

["/etc/nsswitch.conf", """passwd: files
group: files
hosts: files
networks: files
services: files
ethers: files
"""],

["/etc/passwd", """root::0:0:root:/root:/bin/bash
kenny::1000:1000:KL,,,:/home/kenny:/bin/bash
"""]
]

def tr(path): 
	path=path.lstrip("/")
	return os.path.join(args.output_dir, path)

def run_cmd(cmd):
	print cmd,"...",
	if args.dry_run: 
		print "done(dry run)"
	else:
		print "done"
		ret=os.system(cmd)
		if ret: app_exit(ret)

def sudo_cmd(cmd): run_cmd('sudo '+cmd)

def copy_file(src_path, dst_path=None):
	if not dst_path: dst_path=src_path
	dst_path=tr(dst_path)
	if dst_path.endswith("/"): 
		dst_dir=dst_path
	else:
		dst_dir=os.path.dirname(dst_path)
	if not os.path.exists(dst_dir): 
		sudo_cmd('mkdir -p '+dst_dir)
	sudo_cmd('cp -pu '+src_path+' '+dst_path)

	"copy the real file"
	if os.path.islink(src_path):
		t_link=os.readlink(src_path)
		if not t_link.startswith("/"):
			t_link=os.path.join(os.path.dirname(src_path), t_link)
		#print "----COPY LINK:", src_path, "->", t_link
		copy_file(t_link)

def copy_elf(src_path, dst_path=None):
	res=os.popen("which "+src_path).read().strip()
	if res:
		src_path=res
	else:
		"maybe a so file?"
		if not os.path.exists(src_path):
			print "cannot find", src_path
			app_exit(-2)

	copy_file(src_path, dst_path)
	
	res=os.popen("ldd "+src_path).readlines()
	rex=re.compile('/\S+so\S*')
	for i in res:
		m=rex.search(i)
		if m:
			so=m.group()
			if isinstance(so,str):
				copy_file(so)

for elf in elfs_to_copy.split():
	copy_elf(elf)

for elf in kernel_elfs_to_copy.split():
	copy_elf(elf, "/bin")

for link in bb_links.split():
	sudo_cmd('ln -sf /bin/busybox '+tr('/bin/'+link))

for the_dir in dirs_to_mk.split():
	sudo_cmd("mkdir -p "+tr(the_dir))

for cfg_file,data in cfg_files:
	cfg_file=tr(cfg_file)
	print "generate file", cfg_file, data
	if not args.dry_run:
		sudo_cmd("mkdir -p "+os.path.dirname(cfg_file))
		p=os.popen("sudo tee "+cfg_file, "w", -1)
		p.write(data)
		p.close()

sudo_cmd("mknod -m 600 "+tr("/dev/ttyS0")+" c 4 64;true")
sudo_cmd("mknod -m 600 "+tr("/dev/console")+" c 5 1;true")
sudo_cmd("mknod -m 600 "+tr("/dev/null")+" c 1 3;true")

copy_file("/sbin/dhclient-script");
copy_file("/etc/services");

sudo_cmd("chmod a+x " + tr("/etc/init.d/rc"))
sudo_cmd("make INSTALL_MOD_PATH="+args.output_dir+" modules_install")

"vi:ai:"
