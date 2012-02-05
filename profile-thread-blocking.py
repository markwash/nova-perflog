import sys

import timing


def main():
    request, module, function = parse_args_or_die()
    pattern = timing.get_pattern()
    profile = timing.Profile()
    capture = False
    for line in sys.stdin:
        line = line.strip()
        match = pattern.match(line)
        if match is None:
            continue
        trace = timing.parse_match(match)
        if (trace.request == request and trace.module == module
            and trace.function == function and trace.start):
            capture = True
        if capture:
            profile.add_trace(trace)
        if (trace.request == request and trace.module == module
            and trace.function == function and not trace.start):
            capture = False
    key = lambda t: '%s:%s' % (t.request, t.module)
    results = profile.group_results(key)
    timing.display_results(results, total=True, sort='total')
    key = lambda t: t.module
    results = profile.group_results(key)
    timing.display_results(results, total=True, sort='total')


def parse_args_or_die():
    if not len(sys.argv) == 4:
        print "Usage: %s <request id> <module> <function>"
        sys.exit()
    return sys.argv[1:4]

if __name__ == '__main__':
    main()
