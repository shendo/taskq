# TaskQ - Priority queue with task categorisation support
# Copyright (C) 2014 Steve Henderson
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import time

from taskq import Queue
from taskq import policy

def test_fifo():
    q = Queue()
    q.push('test1')
    q.push('test2')
    assert q.pop() == 'test1'
    assert q.pop() == 'test2'

def test_duplicate():
    q = Queue()
    q.push('test')
    try:
        q.push('test')
        assert False
    except ValueError:
        pass
    q.discard('test')
    q.push('test')
    assert len(q) == 1
    
def test_operators():
    q = Queue()
    assert not q
    assert not len(q)
    q.push('test1')
    assert q
    assert len(q)
    q.push('test2')
    assert len(q) == 2
    
def test_priorities():
    q = Queue()
    q.push('test1', 1)
    q.push('test2', 2)
    q.push('test3', 3)
    assert q.pop() == 'test1'
    assert q.pop() == 'test2'
    assert q.pop() == 'test3'
    
    q.push('test3', 3)
    q.push('test2', 2)
    q.push('test1', 1)
    assert q.pop() == 'test1'
    assert q.pop() == 'test2'
    assert q.pop() == 'test3'

    # insert order maintained at same priority
    q.push('test1', 1)
    q.push('test2', 1)
    q.push('test3', 1)
    assert q.pop() == 'test1'
    assert q.pop() == 'test2'
    assert q.pop() == 'test3'

    # complex types supported
    q.push('test1', (1, time.time()))
    q.push('test2', (1, time.time()))
    q.push('test3', (1, time.time()))
    assert q.pop() == 'test1'
    assert q.pop() == 'test2'
    assert q.pop() == 'test3'
    
    q.push('test1', (1, time.time()))
    q.push('test3', (2, time.time()))
    q.push('test2', (1, time.time()))
    assert q.pop() == 'test1'
    assert q.pop() == 'test2'
    assert q.pop() == 'test3'

def test_categories():
    q = Queue()

    q.push('test', category='foo')
    assert q.pop() == 'test'
        
    q.push('test', category='foo')
    assert not q.pop(categories=['bar'])
    assert q.pop(categories=['foo']) == 'test'
    
    q.push('test', category='foo')
    assert q.pop(categories=['bar', 'foo', 'cat']) == 'test'
    
def test_multipop():
    q = Queue()
    q.push('test1')
    assert q.pop(1) == ['test1']
    
    q = Queue()
    q.push('test1')
    q.push('test2')
    assert q.pop(2) == ['test1', 'test2']

    q = Queue()
    q.push('test1')
    assert q.pop(2) == ['test1']
    
    q = Queue()
    q.push('test3', 3)
    q.push('test1', 1)
    q.push('test2', 1)
    assert q.pop(2) == ['test1', 'test2']
    
    q = Queue()
    q.push('test1', category='foo')
    q.push('test2', category='bar')
    q.push('test3', category='foo')
    assert q.pop(2, categories=['fish', 'foo']) == ['test1', 'test3']
    
    q = Queue()
    for x in range(1000):
        q.push(x)
    for i, x in enumerate(q.pop(1000)):
        assert i == x

def test_ratios():
    q = Queue()
    q.push('test1', 1, 'cat')
    q.push('test2', 2, 'cat')
    q.push('test3', 2, 'cat')
    q.push('test4', 3, 'cat')
    assert len(q.pop(2, categories=['cat'], ratios=[0.5])) == 4
    
    q = Queue()
    q.push('test1', 2, 'foo')
    assert len(q.pop(1, categories=['foo'], ratios=[20000])) == 1

    q = Queue()
    assert q.pop(10, categories=['foo'], ratios=[20000]) == []
    
    q = Queue()
    q.push('test1', 1, 'foo')
    q.push('test2', 2, 'bar')
    q.push('test3', 2, 'cat')
    q.push('test4', 3, 'cat')
    assert len(q.pop(3, categories=['cat', 'foo', 'bar'], ratios=[0.5, 1, 1])) == 4
    
def test_discard():
    q = Queue()
    q.push('test1', 1, 'foo')
    q.discard('test1')
    assert not q
    assert not q.pop()

    q = Queue()
    q.push('test1', 1, 'foo')
    q.push('test2', 1, 'bar')
    q.push('test3', 1, 'foo')
    q.discard('test2')
    assert len(q) == 2
    assert q.pop(2) == ['test1', 'test3']
    
def test_policies():
    q = Queue(maxsize=1, full_policy=policy.discard)
    q.push('test1')
    q.push('test2')
    assert len(q) == 1
    assert q.pop() == 'test1'
    
    q = Queue(maxsize=1, full_policy=policy.discard_random)
    q.push('test1')
    q.push('test2')
    assert len(q) == 1
    assert q.pop() == 'test2'
    
    q = Queue(maxsize=3, full_policy=policy.discard_random)
    q.push('test1', 1, 'foo')
    q.push('test2', 2, 'bar')
    q.push('test3', 1, 'foo')
    q.push('test4', 3, 'bar')
    assert len(q) == 3
    assert 'test4' in [ q.pop() for _ in range(3) ]
    
    q = Queue(maxsize=1, full_policy=policy.exception)
    q.push('test1')
    try:
        q.push('test2')
        assert False # should have raised
    except policy.QueueFullException:
        pass
    