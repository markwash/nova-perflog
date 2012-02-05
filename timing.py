from datetime import datetime
import re


def get_pattern():
    pattern_parts = [
        '(\S+\s+\S+)',
        'INFO',
        '(\S+)',
        '\[(\S+)',
        '(\S+)',
        '.*',
        'MJW(?: (finish))?',
        '(\S+).*',
    ]
    pattern = '\s+'.join(pattern_parts)
    return re.compile(pattern)


def parse_match(match):
    groups = match.groups()
    start = groups[4] is None
    return Trace(groups[2], groups[0], groups[3], groups[1], groups[5], start)


class Trace(object):

    def __init__(self, request, time, thread, module, function, start=True):
        self.request = request
        time = '%s000' % time # convert milliseconds to microseconds
        self.time = datetime.strptime(time, '%Y-%m-%d %H:%M:%S,%f')
        self.thread = thread
        self.module = module
        self.function = function
        self.start = start

    @property
    def key(self):
        return '%s:%s:%s.%s' % (self.request, self.thread, self.module, self.function)


class Profile(object):

    def __init__(self):
        self.incomplete = {}
        self.completed = {}
        pass

    def add_trace(self, trace):
        if trace.key in self.incomplete:
            self.complete(trace)
        else:
            self.incomplete[trace.key] = trace

    def complete(self, trace):
        key = trace.key
        first = self.incomplete.pop(key)
        assert first.start
        assert not trace.start
        if key not in self.completed:
            self.completed[key] = [first, []]
        self.completed[key][1].append(trace.time - first.time)

    def group_results(self, extract_key):
        grouped_results = {}
        for parts in self.completed.itervalues():
            trace, times = parts
            key = extract_key(trace)
            if key not in grouped_results:
                grouped_results[key] = []
            grouped_results[key].extend(times)
        return grouped_results

def display_results(results, total=False, avg=False, sort='count'):
        max_key_len = 0
        extracted_results = []
        for key, times in results.iteritems():
            if len(key) > max_key_len:
                max_key_len = len(key)
            seconds = [t.seconds + t.microseconds / 1000000.0 for t in times]
            result = {}
            result['key'] = key
            count = len(seconds)
            result['count'] = count
            if total:
                result['total'] = sum(seconds)
            if avg:
                result['avg'] = sum(seconds) / count
            extracted_results.append(result)
        key = lambda result: result[sort]
        extracted_results.sort(key=key, reverse=True)
        key_format = '%%(key)-%ds' % max_key_len
        header_fmt_parts = []
        header_fmt_parts.append(key_format)
        row_fmt_parts = []
        row_fmt_parts.append(key_format)
        header_fmt_parts.append('count')
        row_fmt_parts.append('%(count)5d')
        if total:
            header_fmt_parts.append('total')
            row_fmt_parts.append('%(total).3f')
        if avg:
            header_fmt_parts.append('  avg')
            row_fmt_parts.append('%(avg).3f')
        header_fmt = '  '.join(header_fmt_parts)
        row_fmt = '  '.join(row_fmt_parts)
        print header_fmt % dict(key='key')
        for result in extracted_results:
            print row_fmt % result
        print

