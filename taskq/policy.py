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

import random

class QueueFullException(Exception):
    pass

def exception(queue):
    """
    Policy for raising an exception when the
    queue is full.
    @param queue: Queue that has reached size limit
    @raise QueueFullException: Raise to force caller to handle
    """
    raise QueueFullException

def discard(queue):
    """
    Policy for discarding the current element
    when the queue is full.
    @param queue: Queue that has reached size limit
    @return: 1 to discontinue processing
    """
    return 1

def discard_random(queue):
    """
    Policy for discarding random elements from
    a queue once full.  This is useful when a queue
    is being used for optional task processing and
    the desire is to get even sampling of the tasks.
    @param queue: Queue that has reached size limit
    @return: 0 to continue processing
    """
    from .queue import DISCARDED
    entry = None
    while not entry or entry[-1] is DISCARDED:
        h = random.choice([ x for x in queue.heaps.values() if x ])
        entry = h[random.randint(0, len(h) -1)]
    queue.discard(entry[-1])
    return 0
