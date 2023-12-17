#! -*- coding: utf-8 -*-

from copy import deepcopy

def validate_boundary(text, start, stop):
    if (start is None) or (stop is None):
        raise ValueError(
            'start and stop of region cannot be None (start=%s, stop=%s)'
            % (repr(start), repr(stop)))
    if start < 0:
        raise ValueError(
            'start of region cannot be less than zero (start=%d)'
            % start)
    if stop > len(text):
        raise ValueError(
            'stop of region cannot be greater than text length (length=%d, stop=%d)'
            % (len(text), stop))
    if start > stop:
        raise ValueError(
            'start cannot be greater than stop (start=%d, stop=%d)'
            % (start, stop))

def validate_tags(text, tags):
    for (tag, regions) in tags.items(): validate_regions(text, tag, regions)
    validate_crossovering(tags)

def validate_regions(text, tag, regions):
    first = None
    for (start, stop) in regions:
        validate_boundary(text, start, stop)
        if first is None: first = text[start:stop]
        elif text[start:stop] != first:
            raise ValueError(
                'inconsistent tag content ("%s"):\n    %s\n    %s'
                % (tag, repr(first), repr(text[start:stop])))

def iterate_regions(tags):
    for (tag, regions) in tags.items():
        for (start, stop) in regions:
            yield tag, start, stop

def crossovering(start1, stop1, start2, stop2):
    if (start1 < start2) and (start2 < stop1) and (stop1 < stop2): return True
    if (start2 < start1) and (start1 < stop2) and (stop2 < stop1): return True
    return False

def iterate_crossovers(tags, start, stop):
    for (tag, tstart, tstop) in iterate_regions(tags):
        if crossovering(start, stop, tstart, tstop):
            yield tag, tstart, tstop

def validate_crossovering(tags):
    for (tag, start, stop) in iterate_regions(tags):
        crossovers = list(iterate_crossovers(tags, start, stop))
        if crossovers:
            raise ValueError(
                'crossovering is not allowed ("%s")[%s]:\n    %s'
                % (tag, repr((start, stop)), repr(crossovers)))

def compute_adjustment(otext, otags, start, stop, content):
    validate_boundary(otext, start, stop)
    nstart = start
    nstop = nstart + len(content)
    ntext = otext[:start] + content + otext[stop:]
    ntags = deepcopy(otags)
    for (tag, regions) in list(ntags.items()):
        deletings = []
        for (i, (rstart, rstop)) in enumerate(regions[:]):
            if (rstart == start) and (rstop == stop):
                # matching region
                regions[i] = (nstart, nstop)
            elif rstop <= start:
                # left region
                pass
            elif stop <= rstart:
                # right region
                delta = (nstop - stop)
                regions[i] = (rstart + delta, rstop + delta)
            elif (rstart <= start) and (stop <= rstop):
                # outer region
                delta = (nstop - stop)
                regions[i] = (rstart, rstop + delta)
            elif (start <= rstart) and (rstop <= stop):
                # inner region
                deletings.append(i)
        # remmove deletings
        for i in deletings: del regions[i]
        # remove empty tag
        if not regions: del ntags[tag]
    return (ntext, ntags)

class Commandment(object):
    text = ''
    regions = None
    def __init__(self, text, tags=None):
        validate_tags(text, tags)
        self.text = text
        self.tags = tags
    def clone(self): return deepcopy(self)
    def __getitem__(self, tag):
        (start, stop) = self.tags[tag][0]
        return self.text[start:stop]
    def __setitem__(self, tag, content):
        ntext = self.text
        ntags = deepcopy(self.tags)
        prev_region = None
        def keyfunc(item):
            (nstart, nstop) = item
            return (-nstart, nstop)
        for (nstart, nstop) in sorted(ntags[tag], key=keyfunc):
            if prev_region == (nstart, nstop): continue
            (ntext, ntags) = compute_adjustment(ntext, ntags, nstart, nstop, content)
            prev_region = (nstart, nstop)
        validate_tags(ntext, ntags)
        self.text = ntext
        self.tags = ntags
    def __contains__(self, tag): return tag in self.tags
    def __len__(self): return len(self.tags)
    def revise(self, settings):
        def keyfunc(item):
            (tag, content, start, stop) = item
            return (-start, stop)
        adjustments = sorted(
            ((tag, content, start, stop)
             for (tag, content) in settings.items()
             for (start, stop) in self.tags[tag]),
            key=keyfunc)
        unique_adjustments = []
        prev_region = None
        prev_content = None
        for (tag, content, start, stop) in adjustments:
            if prev_region == (start, stop):
                if prev_content == content: continue
                else: raise ValueError(
                    'inconsistent settings at (%d, %d):\n    %s\n    %s' %
                    (start, stop, prev_region, content))
            else:
                prev_region = (start, stop)
                prev_content = content
                unique_adjustments.append((tag, content, start, stop))
        ntext = self.text
        ntags = deepcopy(self.tags)
        done = set()
        def keyfunc(item):
            (start, stop) = item
            return (-start, stop)
        for (tag, content, start, stop) in unique_adjustments:
            if tag in done: continue
            for (nstart, nstop) in sorted(ntags[tag], key=keyfunc):
                (ntext, ntags) = compute_adjustment(ntext, ntags, nstart, nstop, content)
            done.add(tag)
        validate_tags(ntext, ntags)
        self.text = ntext
        self.tags = ntags
