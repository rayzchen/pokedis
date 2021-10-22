import os
import json

class LiveDict:
    def __init__(self, d, parent=None):
        self.d = {}
        for name, value in d.items():
            if isinstance(value, dict):
                self.d[name] = LiveDict(value, self)
            elif isinstance(value, list):
                self.d[name] = LiveList(value, self)
            else:
                self.d[name] = value
        self.parent = parent

    def __getitem__(self, item):
        return self.d[str(item)]

    def __setitem__(self, item, value):
        if isinstance(value, dict):
            value = LiveDict(value)
        elif isinstance(value, list):
            value = LiveList(value)
        self.d[str(item)] = value
        if isinstance(value, (LiveDict, LiveList)):
            value.parent = self
        self.update()

    def __delitem__(self, item):
        self.d.pop(str(item))
        self.update()

    def __contains__(self, item):
        return str(item) in self.d

    def __iter__(self):
        return iter(self.d)
    
    def __len__(self):
        return len(self.d)

    def update(self):
        if self.parent is not None:
            self.parent.update()

    def todict(self):
        d = {}
        for name, value in self.d.items():
            if isinstance(value, LiveDict):
                d[name] = value.todict()
            elif isinstance(value, LiveList):
                d[name] = value.tolist()
            else:
                d[name] = value
        return d

    def keys(self):
        return self.d.keys()

    def values(self):
        return self.d.values()

    def items(self):
        return self.d.items()

    def pop(self, item):
        if item in self:
            val = self[item]
            del self[item]
            self.update()
            return val
        raise KeyError(item)

class LiveList:
    def __init__(self, l, parent=None):
        self.l = []
        for item in l:
            if isinstance(item, list):
                self.l.append(LiveList(item, self))
            elif isinstance(item, dict):
                self.l.append(LiveDict(item, self))
            else:
                self.l.append(item)
        self.parent = parent

    def __getitem__(self, item):
        return self.l[item]

    def __setitem__(self, item, value):
        if isinstance(value, dict):
            value = LiveDict(value)
        elif isinstance(value, list):
            value = LiveList(value)
        self.l[item] = value
        if isinstance(value, (LiveDict, LiveList)):
            value.parent = self
        self.update()

    def __delitem__(self, item):
        self.l.pop(item)
        self.update()

    def __contains__(self, item):
        return item in self.l

    def __iter__(self):
        return iter(self.l)
    
    def __len__(self):
        return len(self.l)

    def update(self):
        if self.parent is not None:
            self.parent.update()
    
    def append(self, item):
        if isinstance(item, list):
            self.l.append(LiveList(item, self))
        elif isinstance(item, dict):
            self.l.append(LiveDict(item, self))
        else:
            self.l.append(item)
        self.update()
    
    def insert(self, index, item):
        self.l.insert(index, item)
        self.update()
    
    def count(self, item):
        return self.l.count(item)
    
    def pop(self, index):
        item = self.l.pop(index)
        self.update()
        return item
    
    def index(self, item):
        return self.l.index(item)
    
    def remove(self, item):
        self.l.remove(item)
        self.update()

    def tolist(self):
        l = []
        for item in self.l:
            if isinstance(item, LiveDict):
                l.append(item.todict())
            elif isinstance(item, LiveList):
                l.append(item.tolist())
            else:
                l.append(item)
        return l

class Database(LiveDict):
    def __init__(self, path):
        if not os.path.isfile(path):
            with open(path, "w+") as f:
                f.write("{}")
        super(Database, self).__init__(json.loads(open(path).read()))
        self.path = path

    def update(self):
        with open(self.path, "w+") as f:
            f.write(json.dumps(self.todict()))

    def refresh(self):
        with open(self.path, "w+") as f:
            f.write(json.dumps(self.todict()))

db = Database("db.json")