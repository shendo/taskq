taskq
=====

Priority queue with task categorisation support

Overview
--------
``taskq`` is a heap based priority queue that adds support to
partition tasks into categories for selective removal.

The main driver for the project was work/task queueing where jobs
need to be distributed to workers with different capabilities and 
non-uniform processing times (for calculating efficient prefetch).

This library is not thread-safe and is not intended as a replacement
for python's *queue.Queue* class.

|build_status| |pypi_version|

Getting Started
---------------
Install using ``pip``: ::

	pip install taskq


Basic FIFO usage: ::

	>>> from taskq import Queue
	>>> q = Queue()
	>>> q.push('task1')
	>>> q.push('task2')
	>>> q.pop()
	'task1'
	>>> q.pop()
	'task2'

Task priorities (complex types that define __cmp__ are also supported): ::

	>>> from taskq import Queue
	>>> q = Queue()
	>>> q.push('task1', 2)
	>>> q.push('task2', 1)
	>>> q.pop()
	'task2'
	>>> q.pop()
	'task1'

Multi-pop: ::

	>>> from taskq import Queue
	>>> q = Queue()
	>>> q.push('task1')
	>>> q.push('task2')
	>>> q.push('task3')
	>>> q.pop(2)
	['task1', 'task2']

Task categories: :: 

	>>> from taskq import Queue
	>>> q = Queue()
	>>> q.push('task1', category='foo')
	>>> q.push('task2', category='bar')
	>>> q.push('task3', category='foo')
	>>> q.pop(2, categories=['dog', 'foo'])
	['task1', 'task2']

Category ratios: ::

	>>> from taskq import Queue
	>>> q = Queue()
	>>> q.push('task1', category='foo')
	>>> q.push('task2', category='bar')
	>>> q.push('task3', category='foo')
	>>> q.pop(2, categories=['bar', 'foo'], ratios=[1, 0.5])
	['task1', 'task2', 'task3']

The above example is useful when prefetching/distributing tasks that have 
non-uniform processing durations.  If the category ratios represent 
average duration in seconds, the count can be used to pull approximately 
count seconds worth of the higest priority tasks from the queue.

See source documentation for other feature examples.

Issues
------

Source code for ``taskq`` is hosted on `GitHub`_. Any bug reports or feature
requests can be made using GitHub's `issues system`_.

.. _GitHub: https://github.com/shendo/taskq
.. _issues system: https://github.com/shendo/taskq/issues

.. |build_status| image:: https://secure.travis-ci.org/shendo/taskq.png?branch=master
   :target: http://travis-ci.org/#!/shendo/taskq
   :alt: Current build status

.. |pypi_version| image:: https://pypip.in/v/taskq/badge.png
   :target: https://pypi.python.org/pypi/taskq
   :alt: Latest PyPI version
