import re


from operator import add, sub, mul
# from selectors import EpollSelector
from urllib.request import proxy_bypass


def prune_min(t):
    """Prune the tree mutatively.

    >>> t1 = Tree(6)
    >>> prune_min(t1)
    >>> t1
    Tree(6)
    >>> t2 = Tree(6, [Tree(3), Tree(4)])
    >>> prune_min(t2)
    >>> t2
    Tree(6, [Tree(3)])
    >>> t3 = Tree(6, [Tree(3, [Tree(1), Tree(2)]), Tree(5, [Tree(3), Tree(4)])])
    >>> prune_min(t3)
    >>> t3
    Tree(6, [Tree(3, [Tree(1)])])
    """
    if(t.branches == []):
        return 
    else:
        min = t.branches[-1].label
        cur = t.branches[-1]
        for i in t.branches:
            if i.label < min:
                min = i.label
                cur = i
        t.branches = [cur]
    return prune_min(t.branches[-1])

            


def address_oneline(text):
    """
    Finds and returns expressions in text that represent the first line
    of a US mailing address.

    >>> address_oneline("110 Sproul Hall, Berkeley, CA 94720")
    ['110 Sproul Hall']
    >>> address_oneline("What's at 39177 Farwell Dr? Is there a 39177 Nearwell Dr?")
    ['39177 Farwell Dr', '39177 Nearwell Dr']
    >>> address_oneline("I just landed at 780 N McDonnell Rd, and I need to get to 1880-ish University Avenue. Help!")
    ['780 N McDonnell Rd']
    >>> address_oneline("123 Le Roy Ave")
    ['123 Le Roy Ave']
    >>> address_oneline("110 Unabbreviated Boulevard")
    []
    >>> address_oneline("790 lowercase St")
    []
    """
    block_number = r'\d{3,5}'
    cardinal_dir = r'(?:[NESW]? )?'  # whitespace is important!
    street = r'(?:[A-Z]\w+ )+'
    type_abbr = r'\w{2,5}\b'
    street_name = f"{cardinal_dir}{street}{type_abbr}"
    return re.findall(f"{block_number} {street_name}", text)


def make_test_random():
    """A deterministic random function that cycles between
    [0.0, 0.1, 0.2, ..., 0.9] for testing purposes.

    >>> random = make_test_random()
    >>> random()
    0.0
    >>> random()
    0.1
    >>> random2 = make_test_random()
    >>> random2()
    0.0
    """
    rands = [x / 10 for x in range(10)]

    def random():
        rand = rands[0]
        rands.append(rands.pop(0))
        return rand
    return random


random = make_test_random()

# Phase 1: The Player Class


class Player:
    """
    >>> random = make_test_random()
    >>> p1 = Player('Hill')
    >>> p2 = Player('Don')
    >>> p1.popularity
    100
    >>> p1.debate(p2)  # random() should return 0.0
    >>> p1.popularity
    150
    >>> p2.popularity
    100
    >>> p2.votes
    0
    >>> p2.speech(p1)
    >>> p2.votes
    10
    >>> p2.popularity
    110
    >>> p1.popularity
    135

    """

    def __init__(self, name):
        self.name = name
        self.votes = 0
        self.popularity = 100

    def debate(self, other):
        rand = random()
        prob = max(0.1, self.popularity/(self.popularity + other.popularity))
        if(rand > prob):
            self.popularity -= 50
            if(self.popularity < 0):
                self.popularity = 0
        else:
            self.popularity += 50


    def speech(self, other):
        self.votes += self.popularity // 10
        self.popularity += self.popularity // 10
        other.popularity -= other.popularity // 10
        if(other.popularity < 0):
            other.popularity = 0

    def choose(self, other):
        return self.speech(other)


# Phase 2: The Game Class
class Game:
    """
    >>> p1, p2 = Player('Hill'), Player('Don')
    >>> g = Game(p1, p2)
    >>> winner = g.play()
    >>> p1 is winner
    True

    """

    def __init__(self, player1, player2):
        self.p1 = player1
        self.p2 = player2
        self.turn = 0

    def play(self):
        while not self.game_over:
            if(self.turn % 2 == 0):
                cur_player = self.p1
                other_player = self.p2
            else:
                cur_player = self.p2
                other_player = self.p1
            cur_player.choose(other_player)
            self.turn += 1
        return self.winner

    @property
    def game_over(self):
        return max(self.p1.votes, self.p2.votes) >= 50 or self.turn >= 10

    @property
    def winner(self):
        if(self.p1.votes == self.p2.votes):
            return None
        else:
            return self.p1 if(self.p1.votes > self.p2.votes) else self.p2


# Phase 3: New Players
class AggressivePlayer(Player):
    """
    >>> random = make_test_random()
    >>> p1, p2 = AggressivePlayer('Don'), Player('Hill')
    >>> g = Game(p1, p2)
    >>> winner = g.play()
    >>> p1 is winner
    True

    """

    def choose(self, other):
        if(self.popularity <= other.popularity):
            return self.debate(other)
        else:
            return self.speech(other)


class CautiousPlayer(Player):
    """
    >>> random = make_test_random()
    >>> p1, p2 = CautiousPlayer('Hill'), AggressivePlayer('Don')
    >>> p1.popularity = 0
    >>> p1.choose(p2) == p1.debate
    True
    >>> p1.popularity = 1
    >>> p1.choose(p2) == p1.debate
    False

    """

    def choose(self, other):
        if(self.popularity == 0):
            return self.debate(other)
        else:
            return self.speech(other)


def add_trees(t1, t2):
    """
    >>> numbers = Tree(1,
    ...                [Tree(2,
    ...                      [Tree(3),
    ...                       Tree(4)]),
    ...                 Tree(5,
    ...                      [Tree(6,
    ...                            [Tree(7)]),
    ...                       Tree(8)])])
    >>> print(add_trees(numbers, numbers))
    2
      4
        6
        8
      10
        12
          14
        16
    >>> print(add_trees(Tree(2), Tree(3, [Tree(4), Tree(5)])))
    5
      4
      5
    >>> print(add_trees(Tree(2, [Tree(3)]), Tree(2, [Tree(3), Tree(4)])))
    4
      6
      4
    >>> print(add_trees(Tree(2, [Tree(3, [Tree(4), Tree(5)])]), \
    Tree(2, [Tree(3, [Tree(4)]), Tree(5)])))
    4
      6
        8
        5
      5
    """
    if not t1:
        return t2
    elif not t2:
        return t1
    else:
        label = t1.label + t2.label
        branch1 = t1.branches
        branch2 = t2.branches
        length1 = len(branch1)
        length2 = len(branch2)
    if(length1 < length2):
        branch1 += [None for _ in range(length1,length2)]
    if(length1 > length2):
        branch2 += [None for _ in range(length2,length1)]
    return Tree(label,[add_trees(branches1,branches2) for branches1,branches2 in zip(branch1,branch2)])

def foldl(link, fn, z):
    """ Left fold
    >>> lst = Link(3, Link(2, Link(1)))
    >>> foldl(lst, sub, 0) # (((0 - 3) - 2) - 1)
    -6
    >>> foldl(lst, add, 0) # (((0 + 3) + 2) + 1)
    6
    >>> foldl(lst, mul, 1) # (((1 * 3) * 2) * 1)
    6
    """
    if link is Link.empty:
        return z
    return foldl(link.rest, fn, fn(z, link.first))


def foldr(link, fn, z):
    """ Right fold
    >>> lst = Link(3, Link(2, Link(1)))
    >>> foldr(lst, sub, 0) # (3 - (2 - (1 - 0)))
    2
    >>> foldr(lst, add, 0) # (3 + (2 + (1 + 0)))
    6
    >>> foldr(lst, mul, 1) # (3 * (2 * (1 * 1)))
    6
    """
    if link is Link.empty:
        return z
    return fn(link.first,foldr(link.rest, fn, z))


def match_url(text):
    """
    >>> match_url("https://cs61a.org/resources/#regular-expressions")
    True
    >>> match_url("https://pythontutor.com/composingprograms.html")
    True
    >>> match_url("https://pythontutor.com/should/not.match.this")
    False
    >>> match_url("https://link.com/nor.this/")
    False
    >>> match_url("http://insecure.net")
    True
    >>> match_url("htp://domain.org")
    False
    """
    scheme = r'(http|https)\:\/\/'
    domain = r'(\w+\.)+\w+'
    path = r'(\/\w+)+(\.html)?'
    anchor = r'\/#[\w\d\-\_]+'
    return bool(re.match(rf"^(?:{scheme})?{domain}(?:{path})?(?:{anchor})?$", text))


class Tree:
    """
    >>> t = Tree(3, [Tree(2, [Tree(5)]), Tree(4)])
    >>> t.label
    3
    >>> t.branches[0].label
    2
    >>> t.branches[1].is_leaf()
    True
    """

    def __init__(self, label, branches=[]):
        for b in branches:
            assert isinstance(b, Tree)
        self.label = label
        self.branches = list(branches)

    def is_leaf(self):
        return not self.branches

    def __repr__(self):
        if self.branches:
            branch_str = ', ' + repr(self.branches)
        else:
            branch_str = ''
        return 'Tree({0}{1})'.format(self.label, branch_str)

    def __str__(self):
        def print_tree(t, indent=0):
            tree_str = '  ' * indent + str(t.label) + "\n"
            for b in t.branches:
                tree_str += print_tree(b, indent + 1)
            return tree_str
        return print_tree(self).rstrip()


class Link:
    """A linked list.

    >>> s = Link(1)
    >>> s.first
    1
    >>> s.rest is Link.empty
    True
    >>> s = Link(2, Link(3, Link(4)))
    >>> s.first = 5
    >>> s.rest.first = 6
    >>> s.rest.rest = Link.empty
    >>> s                                    # Displays the contents of repr(s)
    Link(5, Link(6))
    >>> s.rest = Link(7, Link(Link(8, Link(9))))
    >>> s
    Link(5, Link(7, Link(Link(8, Link(9)))))
    >>> print(s)                             # Prints str(s)
    <5 7 <8 9>>
    """
    empty = ()

    def __init__(self, first, rest=empty):
        assert rest is Link.empty or isinstance(rest, Link)
        self.first = first
        self.rest = rest

    def __repr__(self):
        if self.rest is not Link.empty:
            rest_repr = ', ' + repr(self.rest)
        else:
            rest_repr = ''
        return 'Link(' + repr(self.first) + rest_repr + ')'

    def __str__(self):
        string = '<'
        while self.rest is not Link.empty:
            string += str(self.first) + ' '
            self = self.rest
        return string + str(self.first) + '>'
