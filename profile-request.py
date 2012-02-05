import sys

import timing


def main():
    request = parse_args_or_die()
    pattern = timing.get_pattern()
    profile = timing.Profile()
    for line in sys.stdin:
        line = line.strip()
        match = pattern.match(line)
        if match is None:
            continue
        trace = timing.parse_match(match)
        if trace.request != request:
            continue
        profile.add_trace(trace)
    results = profile.group_results(lambda t: '%s.%s' % (t.module, t.function))
    timing.display_results(results, avg=True, sort='avg')
    results = profile.group_results(lambda t: t.module)
    timing.display_results(results, total=True, sort='total')


def parse_args_or_die():
    if not len(sys.argv) == 2:
        print "Usage: %s <request id>"
        sys.exit()
    return sys.argv[1]

if __name__ == '__main__':
    main()
