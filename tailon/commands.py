# -*- coding: utf-8; -*-

import logging
import subprocess
from . import compat

from tornado import process


STREAM = process.Subprocess.STREAM
log = logging.getLogger('tailon')


class ToolPaths:
    command_names = {'grep', 'awk', 'sed', 'tail'}

    def __init__(self, overwrites=None):
        self.cmd_grep  = self.first_in_path('grep')
        self.cmd_sift  = self.first_in_path('sift')
        self.cmd_awk   = self.first_in_path('gawk', 'awk')
        self.cmd_sed   = self.first_in_path('gsed', 'sed')
        self.cmd_tail  = self.first_in_path('gtail', 'tail')
        self.cmd_zcat  = self.first_in_path('zcat')


        if overwrites:
            for name, value in overwrites.items():
                setattr(self, name, value)

    def first_in_path(self, *cmds):
        for cmd in cmds:
            path = compat.which(cmd)
            if path:
                return path


#-----------------------------------------------------------------------------
class CommandControl:
    def __init__(self, toolpaths, follow_names=False):
        self.toolpaths = toolpaths
        self.follow_names = follow_names

    def awk(self, script, fn, stdout, stderr, **kw):
        cmd = [self.toolpaths.cmd_awk, '--sandbox', script]
        if fn:
            cmd.extend(fn)
        proc = process.Subprocess(cmd, stdout=stdout, stderr=stderr, **kw)
        log.debug('running awk %s, pid: %s', cmd, proc.proc.pid)
        return proc

    def grep(self, regex, fn, stdout, stderr, **kw):
        cmd = [self.toolpaths.cmd_grep, '--text', '--line-buffered', '--color=never', '-e', regex]
        if fn:
            cmd.extend(fn)
        proc = process.Subprocess(cmd, stdout=stdout, stderr=stderr, **kw)
        log.debug('running grep %s, pid: %s', cmd, proc.proc.pid)
        return proc

    def sift(self, regex, fn, stdout, stderr, **kw):
        cmd = [self.toolpaths.cmd_sift, '--zip','--binary-skip', '--no-color','--recursive', '--no-filename', '-e', regex]
        if fn:
            cmd.append(fn)
        proc = process.Subprocess(cmd, stdout=stdout, stderr=stderr, **kw)
        log.debug('running sift %s, pid: %s', cmd, proc.proc.pid)
        return proc

    def sed(self, script, fn, stdout, stderr, **kw):
        cmd = [self.toolpaths.cmd_sed, '-u', '-e', script]
        if fn:
            cmd.extend(fn)
        proc = process.Subprocess(cmd, stdout=stdout, stderr=stderr, **kw)
        log.debug('running sed %s, pid: %s', cmd, proc.proc.pid)
        return proc

    def tail(self, n, fn, stdout, stderr, **kw):
        flag_follow = '-F' if self.follow_names else '-f'
        cmd = [self.toolpaths.cmd_tail, '--silent', '-n', str(n), flag_follow]
        cmd.extend(fn)
        proc = process.Subprocess(cmd, stdout=stdout, stderr=stderr, bufsize=1, **kw)
        log.debug('running tail %s, pid: %s', cmd, proc.proc.pid)
        return proc

    def grep_tail(self, n, stdout, stderr, **kw):
        cmd = [self.toolpaths.cmd_tail, '-n', str(n)]
        proc = process.Subprocess(cmd, stdout=stdout, stderr=stderr, bufsize=1, **kw)
        log.debug('running tail %s, pid: %s', cmd, proc.proc.pid)
        return proc

    def zcat(self, fn, stdout, stderr, **kw):
        cmd = [self.toolpaths.cmd_zcat, '-f', '-r']
        cmd.append(fn)
        proc = process.Subprocess(cmd, stdout=stdout, stderr=stderr, bufsize=1, **kw)
        log.debug('running zcat %s, pid: %s', cmd, proc.proc.pid)
        return proc

    def tail_awk(self, n, fn, script, stdout, stderr):
        tail = self.tail(n, fn, stdout=subprocess.PIPE, stderr=STREAM)
        awk = self.awk(script, None, stdout=STREAM, stderr=STREAM, stdin=tail.stdout)
        return tail, awk

    def tail_grep(self, n, fn, regex, stdout, stderr):
        tail = self.tail(n, fn, stdout=subprocess.PIPE, stderr=STREAM)
        grep = self.grep(regex, None, stdout=STREAM, stderr=STREAM, stdin=tail.stdout)
        tail.stdout.close()
        return tail, grep

    def tail_sed(self, n, fn, script, stdout, stderr):
        tail = self.tail(n, fn, stdout=subprocess.PIPE, stderr=STREAM)
        sed = self.sed(script, None, stdout=STREAM, stderr=STREAM, stdin=tail.stdout)
        tail.stdout.close()
        return tail, sed

    def all_awk(self, fn, script, stdout, stderr):
        zcat = self.zcat(fn, stdout=subprocess.PIPE, stderr=STREAM)
        awk = self.awk(script, None, stdout=STREAM, stderr=STREAM, stdin=zcat.stdout)
        return zcat, awk

    def all_grep(self, grep_lines, fn, regex, stdout, stderr):
        if self.toolpaths.cmd_sift:
            grep = self.sift(regex, fn, stdout=subprocess.PIPE, stderr=STREAM)
            tail = self.grep_tail(grep_lines, stdout=STREAM, stderr=STREAM, stdin=grep.stdout)
            return grep, tail
        else:
            zcat = self.zcat(fn, stdout=subprocess.PIPE, stderr=STREAM)
            grep = self.grep(regex, None, stdout=subprocess.PIPE, stderr=STREAM, stdin=zcat.stdout)
            tail = self.grep_tail(grep_lines, stdout=STREAM, stderr=STREAM, stdin=grep.stdout)
            return zcat, grep, tail

    def all_sed(self, fn, script, stdout, stderr):
        zcat = self.zcat(fn, stdout=subprocess.PIPE, stderr=STREAM)
        sed = self.sed(script, None, stdout=STREAM, stderr=STREAM, stdin=zcat.stdout)
        tail.stdout.close()
        return zcat, sed
