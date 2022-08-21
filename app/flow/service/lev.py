from functools import lru_cache


# Original source
# https://gist.github.com/vatsal220/6aefbc245216bc9f2da8556f42e1c89c#file-lev_dist-py

def lev_dist(a, b):
    """
    This function will calculate the levenshtein distance between two input
    strings a and b

    params:
        a (String) : The first string you want to compare
        b (String) : The second string you want to compare

    returns:
        This function will return the distnace between string a and b.

    example:
        a = 'stamp'
        b = 'stomp'
        lev_dist(a,b)
        >> 1.0
    """

    @lru_cache(None)  # for memorization
    def min_dist(s1, s2):

        if s1 == len(a) or s2 == len(b):
            return len(a) - s1 + len(b) - s2

        # no change required
        if a[s1] == b[s2]:
            return min_dist(s1 + 1, s2 + 1)

        return 1 + min(
            min_dist(s1, s2 + 1),  # insert character
            min_dist(s1 + 1, s2),  # delete character
            min_dist(s1 + 1, s2 + 1),  # replace character
        )

    return min_dist(0, 0)


def lev_percentage(a, b):
    if b is None:
        return 0
    dist = lev_dist(a, b)
    return 1 - dist / len(a)


if __name__ == '__main__':
    print(round(lev_percentage("ИНОК", "ЕНУХ"), 2))
