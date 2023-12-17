#! -*- coding: utf-8 -*-

def punctuation(x):
    if not isinstance(x, str): return None
    return not any(c.isalnum() for c in x)

class Visitor(object):
    def roster(self, rst): raise NotImplementedError()
    def section(self, sct): raise NotImplementedError()
    def list(self, lst): raise NotImplementedError()
    def scope(self, scp): raise NotImplementedError()
    def line(self, ln): raise NotImplementedError()
    def tag(self, tg): raise NotImplementedError()

class Structure(object):
    inline = False
    def __bool__(self): raise NotImplementedError()
    __nonzero__ = __bool__
    def __str__(self): return self.pretty()
    def plain(self):
        v = PlainVisitor()
        self.visit(v)
        return v.generate()
    def pretty(self, tab='  '):
        v = PrettyVisitor(tab)
        self.visit(v)
        return v.generate()

class Tag(Structure):
    @property
    def inline(self):
        if isinstance(self.item, Structure): return self.item.inline
        else: return True
    def __init__(self, item, tag):
        self.item = item
        self.tag = tag
    def visit(self, visitor): visitor.tag(self)

tag = Tag

class Roster(Structure):
    def __init__(self): self.subs = []
    def __bool__(self): return bool(self.subs)
    __nonzero__ = __bool__
    def visit(self, visitor): visitor.roster(self)
    def add(self, sub):
        assert isinstance(sub, Structure)
        assert not sub.inline
        self.subs.append(sub)
    def roster(self):
        r = Roster()
        self.subs.append(r)
        return r
    def section(self):
        r = Section()
        self.subs.append(r)
        return r
    def titled(self, title):
        s = self.section()
        s.header.line(title)
        return s.content
    def list(self, sep):
        r = List(sep)
        self.subs.append(r)
        return r
    def scope(self, beginning, ending):
        r = Scope(beginning, ending)
        self.subs.append(r)
        return r
    def line(self, *words):
        r = Line(*words)
        self.subs.append(r)
        return r

class Section(Structure):
    def __init__(self):
        self.header = Roster()
        self.content = Roster()
    def __bool__(self): return bool(self.header) or bool(self.content)
    __nonzero__ = __bool__
    def visit(self, visitor): visitor.section(self)

class List(Roster):
    def __init__(self, sep):
        Roster.__init__(self)
        assert not isinstance(sep, Structure)
        self.sep = sep
        self.condense = bool(punctuation(sep))
    def visit(self, visitor): visitor.list(self)

class Scope(Roster):
    def __init__(self, beginning, ending):
        Roster.__init__(self)
        assert not isinstance(beginning, Structure)
        assert not isinstance(ending, Structure)
        self.beginning = beginning
        self.ending = ending
        punc = bool(punctuation(beginning) and punctuation(ending))
        self.condense = punc
        self.inline = punc
    def visit(self, visitor): visitor.scope(self)

class Line(Structure):
    def __init__(self, *args):
        self.words = []
        self.word(*args)
    def __bool__(self): return bool(self.words)
    __nonzero__ = __bool__
    def visit(self, visitor): visitor.line(self)
    def word(self, *args):
        for x in args:
            if isinstance(x, Line): self.words.extend(x.words)
            else: self.words.append(x)
    def list(self, sep):
        r = List(sep)
        self.words.append(r)
        return r
    def scope(self, beginning, ending):
        r = Scope(beginning, ending)
        self.words.append(r)
        return r
    def __add__(self, other):
        r = Line()
        r.words.extend(self.words)
        if isinstance(other, Line): r.words.extend(other.words)
        else: r.words.append(other)
        return r
    def __radd__(self, other):
        r = Line()
        if isinstance(other, Line): r.words.extend(other.words)
        else: r.words.append(other)
        r.words.extend(self.words)
        return r
    @staticmethod
    def join(sep, S):
        line = Line()
        first = True
        for x in S:
            if sep and not first: line.word(sep)
            if isinstance(x, Line): line.words.extend(x.words)
            else: line.word(x)
            first = False
        return line

class CommonVisitor(Visitor):
    def generate(self): raise NotImplementedError()

class PlainVisitor(CommonVisitor):
    def __init__(self):
        self.items = []
        self.adjwrite = False
    def generate(self): return ' '.join(self.items)
    def write_item(self, x):
        assert not isinstance(x, Structure)
        if not x: return
        prev = self.items[-1] if self.items else None
        if (prev is not None) and self.adjwrite:
            self.items[-1] = ''.join([prev, x])
        else:
            self.items.append(x)
        self.adjwrite = False
    def write(self, x):
        if isinstance(x, Structure): x.visit(self)
        else: self.write_item(x)
    def roster(self, rst):
        for x in rst.subs: self.write(x)
    def section(self, sct):
        sct.header.visit(self)
        sct.content.visit(self)
    def list(self, lst):
        if not lst.subs: return
        for x in lst.subs[:-1]:
            self.write(x)
            self.adjwrite = lst.condense
            self.write(lst.sep)
        self.write(lst.subs[-1])
    def scope(self, scp):
        self.adjwrite = scp.condense
        self.write(scp.beginning)
        self.adjwrite = scp.condense
        for x in scp.subs: self.write(x)
        self.adjwrite = scp.condense
        self.write(scp.ending)
        self.adjwrite = scp.condense
    def line(self, ln):
        for x in ln.words:
            self.write(x)
    def tag(self, tg): self.write(tg.item)

class PrettyVisitor(CommonVisitor):
    tab = '  '
    def __init__(self, tab=None):
        self.level = 0
        self.lines = []
        self.tags = []
        self.taggings = []
        self.sealed = -1
        self.sealed_len = 0
        if tab is not None: self.tab = tab
    def generate(self):
        try:
            return '\n'.join(
                (self.tab * tab) + ''.join(line)
                for (tab,line) in self.lines)
        except:
            raise Exception(repr(self.lines))
    def line_len(self, index):
        (tab, line) = self.lines[index]
        return (tab * len(self.tab)) + sum(len(x) for x in line)
    def update_sealed(self):
        newsealed = len(self.lines) - 2
        if newsealed < 0: return
        acc = 0
        for i in range(self.sealed + 1, newsealed + 1):
            acc += self.line_len(i) + 1
        self.sealed = newsealed
        self.sealed_len += acc
    def add(self, x): self.lines[-1][1].append(x)
    def write(self, x):
        if isinstance(x, Structure): x.visit(self)
        elif x: self.add(x)
    def openline(self, indent=0):
        if self.lines:
            prev = self.lines[-1][1]
            if not prev: return
            prev[-1] = prev[-1].rstrip()
        self.level += indent
        self.lines.append([self.level, []])
    def current(self):
        if not self.lines: return 0
        self.update_sealed()
        return self.sealed_len + self.line_len(len(self.lines) - 1)
    def begin_tag(self, tg):
        self.taggings.append(tg)
        state = [tuple(self.taggings), self.current(), None]
        self.tags.append(state)
        return state
    def end_tag(self, state):
        state[2] = self.current()
        self.taggings.pop()
    def begin_structure(self, s):
        if (not self.lines) or (not s.inline): self.openline()
        return self.level
    def end_structure(self, state): self.level = state
    def roster(self, rst):
        state = self.begin_structure(rst)
        for x in rst.subs: self.write(x)
        self.end_structure(state)
    def section(self, sct):
        state = self.begin_structure(sct)
        sct.header.visit(self)
        self.openline(1)
        sct.content.visit(self)
        self.end_structure(state)
    def list(self, lst):
        state = self.begin_structure(lst)
        try:
            if not lst.subs: return
            for x in lst.subs[:-1]:
                self.write(x)
                if not lst.condense: self.write(' ')
                self.write(lst.sep)
                self.openline()
            self.write(lst.subs[-1])
        finally:
            self.end_structure(state)
    def scope(self, scp):
        state = self.begin_structure(scp)
        self.write(scp.beginning)
        self.openline(1)
        for x in scp.subs: self.write(x)
        self.openline(-1)
        self.write(scp.ending)
        self.end_structure(state)
    def line(self, ln):
        state = self.begin_structure(ln)
        for x in ln.words:
            if isinstance(x, Structure) and not x.inline: self.openline(1)
            self.write(x)
        self.end_structure(state)
    def tag(self, tg):
        s1 = self.begin_structure(tg)
        s2 = self.begin_tag(tg)
        self.write(tg.item)
        self.end_tag(s2)
        self.end_structure(s1)
