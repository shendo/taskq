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

from __future__ import unicode_literals
import heapq
import itertools

from .policy import discard

# Discard and consistent sorting implementation
# details taken from priority queue example at
# https://docs.python.org/2/library/heapq.html
DISCARDED = 'DEL'
        
class Queue(object):
    """
    Priority queue with task categorisation support.
    """
    def __init__(self, maxsize=0, full_policy=discard):
        """
        Creates a new empty queue.
        @param maxsize: Maximum number of queue elements across all 
            categories. <= 0 is unbounded.
        @param full_policy: Action to take when attempt to push on
            a full queue.
        """
        self.size = 0
        self.truesize = 0
        self.maxsize = maxsize
        self.full_policy = full_policy
        self.heaps = {}
        self.lookup = {}
        # tie breaker for ordering
        self.counter = itertools.count()
        
    def push(self, item, priority=1, category='default'):
        """
        Push the specified item/task onto the queue.
        Duplicates are not currently supported due to the discard
        implementation.
        @param priority: Priority of item where smaller = higher.
            Any class of object that supports comparison can be used as
            the priority value as long as type is consistent for queue.
        @param category: Optional group categorisation for item.
        """
        if self.maxsize > 0 and self.size >= self.maxsize:
            if self.full_policy(self):
                return
        if item in self.lookup:
            raise ValueError('Duplicate item values are not allowed')
        
        q = self.heaps.get(category, [])
        self.heaps[category] = q
        count = next(self.counter)
        entry = [priority, count, category, item]
        self.lookup[item] = entry
        heapq.heappush(q, entry)
        self.size += 1
        self.truesize += 1
    
    def exists(self, item):
        """
        Does the specified item exist within the queue.
        @param item: Item value to test.
        @return: True if exists, otherwise False.
        """
        return item in self.lookup
    
    def discard(self, item):
        """
        Discards the specified item from the queue.
        @param item: Item to be discarded.
        @raise KeyError: If item was not an element in the queue.
        """
        entry = self.lookup.pop(item)
        entry[-1] = DISCARDED
        self.size -= 1
        
    def compact(self):
        """
        As the dicard() implementation is a soft delete, compact()
        may be used to force reducing the size of the internal state.
        This space would otherwise be (silently) freed as the deleted 
        elements are encountered during pop() operations.
        """
        # drop all discarded and re-heapify
        for cat, q in self.heaps.items():
            newq = [ x for x in q if x[-1] is not DISCARDED ]
            heapq.heapify(newq)
            self.heaps[cat] = newq
    
    def purge(self):
        """
        Resets the internal state of the queue and frees all internal
        structures.
        """
        self.size = 0
        self.truesize = 0
        self.heaps = {}
        self.lookup = {}
    
    def pop(self, count=None, categories=None, ratios=None):
        """
        Pop the highest priority item/s from the queue.
        @param count: Multipop count, None to pop single item only.
            count > 0 to instead pop multiple items and return as a list.
        @param categories: List of item/task categories to pop from queue.
            None = any category.
        @param ratios: List of corresponding weighting ratios for the provided
            categories.  This modifies the returned number of items for the
            requested multipop count.
        @return (count=None) highest priority item or None if no matching.
            (count=i) list of up to i highest priority items or [] if no matching.
        """
        if ratios and not count:
            raise ValueError('Must specify a count threshold when using ratios')
        items = []
        threshold = count or 1
        heaps = [ y for x, y in self.heaps.items()
                     if not categories or x in categories ]
        value = 0
        while value < threshold:
            entry = self._pop(heaps)
            if not entry:
                break
            item = entry[-1]
            cat = entry[-2]
            self.truesize -= 1
            if item is not DISCARDED:
                del self.lookup[item]
                self.size -= 1
                items.append(item)
                if categories and ratios:
                    value += ratios[categories.index(cat)]
                else:
                    value += 1 
        
        if not count:
            return (items and items[0]) or None
        return items
    
    def _pop(self, heaps):
        # peek at next across categories
        smallest = [ x[0] for x in heaps if x ]
        if not smallest:
            return None
        entry = min(smallest)
        return heapq.heappop(self.heaps[entry[-2]])
        
    def __len__(self):
        return self.size
    
    def __nonzero__(self):
        return self.size > 0
    
    def __bool__(self):
        return self.__nonzero__()
    
        
