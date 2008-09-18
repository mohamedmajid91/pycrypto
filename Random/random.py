# -*- coding: utf-8 -*-
#
#  Random/random.py : Strong alternative for the standard 'random' module
#
# Copyright (C) 2008  Dwayne C. Litzenberger <dlitz@dlitz.net>
#
# =======================================================================
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# =======================================================================

"""A cryptographically strong version of Python's standard "random" module."""

__revision__ = "$Id$"
__all__ = ['StrongRandom', 'getrandbits', 'randrange', 'randint', 'choice', 'shuffle', 'sample']

from Crypto import Random

from Crypto.Util.python_compat import *

class StrongRandom(object):
    def __init__(self, rng=None, randfunc=None):
        if randfunc is None and rng is None:
            self._randfunc = None
        elif randfunc is not None and rng is None:
            self._randfunc = randfunc
        elif randfunc is None and rng is not None:
            self._randfunc = rng.read
        else:
            raise ValueError("Cannot specify both 'rng' and 'randfunc'")

    def getrandbits(self, k):
        """Return a python long integer with k random bits."""
        if self._randfunc is None:
            self._randfunc = Random.new().read
        mask = (1L << k) - 1
        return mask & bytes_to_long(self._randfunc(ceil_div(k, 8)))

    def randrange(self, *args):
        """randrange([start,] stop[, step]):
        Return a randomly-selected element from range(start, stop, step)."""
        if len(args) == 3:
            (start, stop, step) = args
        elif len(args) == 2:
            (start, stop) = args
            step = 1
        elif len(args) == 1:
            (stop,) = args
            start = 0
            step = 1
        else:
            raise TypeError("randrange expected at most 3 arguments, got %d" % (len(args),))
        if (not isinstance(start, (int, long))
                or not isinstance(stop, (int, long))
                or not isinstance(step, (int, long))):
            raise TypeError("randrange requires integer arguments")
        if step == 0:
            raise ValueError("randrange step argument must not be zero")

        num_choices = ceil_div(stop - start, step)
        if num_choices < 0:
            num_choices = 0
        if num_choices < 1:
            raise ValueError("empty range for randrange(%r, %r, %r)" % (start, stop, step))

        # Pick a random number in the range of possible numbers
        r = num_choices
        while r >= num_choices:
            r = self.getrandbits(size(num_choices))

        return start + (step * r)

    def randint(self, a, b):
        """Return a random integer N such that a <= N <= b."""
        if not isinstance(a, (int, long)) or not isinstance(b, (int, long)):
            raise TypeError("randint requires integer arguments")
        N = self.randrange(a, b+1)
        assert a <= N <= b
        return N

    def choice(self, seq):
        """Return a random element from a (non-empty) sequence.

        If the seqence is empty, raises IndexError.
        """
        if len(seq) == 0:
            raise IndexError("empty sequence")
        return seq[self.randrange(len(seq))]

    def shuffle(self, x):
        """Shuffle the sequence in place."""
        # Make a (copy) of the list of objects we want to shuffle
        items = list(x)

        # Choose a random item (without replacement) until all the items have been
        # chosen.
        for i in xrange(len(x)):
            p = self.randint(len(items))
            x[i] = items[p]
            del items[p]

    def sample(self, population, k):
        """Return a k-length list of unique elements chosen from the population sequence."""

        num_choices = len(population)
        if k > num_choices:
            raise ValueError("sample larger than population")

        retval = []
        selected = {}  # we emulate a set using a dict here
        for i in xrange(k):
            r = None
            while r is None or r in selected:
                r = self.randrange(num_choices)
            retval.append(population[r])
            selected[r] = 1
        return retval

_r = StrongRandom()
getrandbits = _r.getrandbits
randrange = _r.randrange
randint = _r.randint
choice = _r.choice
shuffle = _r.shuffle
sample = _r.sample

# These are at the bottom to avoid problems with recursive imports
from Crypto.Util.number import ceil_div, bytes_to_long, long_to_bytes, size

# vim:set ts=4 sw=4 sts=4 expandtab:
