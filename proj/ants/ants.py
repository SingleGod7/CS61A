"""CS 61A presents Ants Vs. SomeBees."""

from importlib.abc import TraversableResources
from math import dist
from operator import truediv
import random
from re import A
from sys import implementation
from turtle import distance
from ucb import main, interact, trace
from collections import OrderedDict

################
# Core Classes #
################


class Place:
    """A Place holds insects and has an exit to another Place."""
    is_hive = False

    def __init__(self, name, exit=None):
        """Create a Place with the given NAME and EXIT.

        name -- A string; the name of this Place.
        exit -- The Place reached by exiting this Place (may be None).
        """
        self.name = name
        self.exit = exit
        self.bees = []        # A list of Bees
        self.ant = None       # An Ant
        self.entrance = None  # A Place
        # Phase 1: Add an entrance to the exit
        # BEGIN Problem 2
        if(exit != None):
            exit.entrance = self
        # END Problem 2

    def add_insect(self, insect):
        """
        Asks the insect to add itself to the current place. This method exists so
            it can be enhanced in subclasses.
        """
        insect.add_to(self)

    def remove_insect(self, insect):
        """
        Asks the insect to remove itself from the current place. This method exists so
            it can be enhanced in subclasses.
        """
        insect.remove_from(self)

    def __str__(self):
        return self.name


class Insect:
    """An Insect, the base class of Ant and Bee, has health and a Place."""

    damage = 0
    is_waterproof = False
    # ADD CLASS ATTRIBUTES HERE

    def __init__(self, health, place=None):
        """Create an Insect with a health amount and a starting PLACE."""
        self.health = health
        self.place = place  # set by Place.add_insect and Place.remove_insect

    def reduce_health(self, amount):
        """Reduce health by AMOUNT, and remove the insect from its place if it
        has no health remaining.

        >>> test_insect = Insect(5)
        >>> test_insect.reduce_health(2)
        >>> test_insect.health
        3
        """
        self.health -= amount
        if self.health <= 0:
            self.death_callback()
            self.place.remove_insect(self)

    def action(self, gamestate):
        """The action performed each turn.

        gamestate -- The GameState, used to access game state information.
        """

    def death_callback(self):
        # overriden by the gui
        pass

    def add_to(self, place):
        """Add this Insect to the given Place

        By default just sets the place attribute, but this should be overriden in the subclasses
            to manipulate the relevant attributes of Place
        """
        self.place = place

    def remove_from(self, place):
        self.place = None

    def __repr__(self):
        cname = type(self).__name__
        return '{0}({1}, {2})'.format(cname, self.health, self.place)


class Ant(Insect):
    """An Ant occupies a place and does work for the colony."""

    implemented = False  # Only implemented Ant classes should be instantiated
    food_cost = 0
    is_container = False
    blocks_path = True
    # ADD CLASS ATTRIBUTES HERE

    def __init__(self, health=1):
        """Create an Insect with a HEALTH quantity."""
        self.buffed = False
        super().__init__(health)

    @classmethod
    def construct(cls, gamestate):
        """Create an Ant for a given GameState, or return None if not possible."""
        if cls.food_cost > gamestate.food:
            print('Not enough food remains to place ' + cls.__name__)
            return
        return cls()

    def can_contain(self, other):
        return False

    def store_ant(self, other):
        assert False, "{0} cannot contain an ant".format(self)

    def remove_ant(self, other):
        assert False, "{0} cannot contain an ant".format(self)

    def add_to(self, place):
        if place.ant is None:
            place.ant = self
        elif(isinstance(self, ContainerAnt) and self.can_contain(place.ant)):
            self.store_ant(place.ant)
            place.ant = self
        elif(isinstance(place.ant, ContainerAnt) and place.ant.can_contain(self)):
            place.ant.store_ant(self)
        else:
            assert place.ant is None , 'Two ants in {0}'.format(place)
            # END Problem 8
        Insect.add_to(self, place)

    def remove_from(self, place):
        if place.ant is self:
            place.ant = None
        elif place.ant is None:
            assert False, '{0} is not in {1}'.format(self, place)
        else:
            place.ant.remove_ant(self)
        Insect.remove_from(self, place)

    def buff(self):
        """Double this ants's damage, if it has not already been buffed."""
        # BEGIN Problem 12
        "*** YOUR CODE HERE ***"
        # END Problem 12


class HarvesterAnt(Ant):
    """HarvesterAnt produces 1 additional food per turn for the colony."""

    name = 'Harvester'
    implemented = True
    food_cost = 2
    # OVERRIDE CLASS ATTRIBUTES HERE

    def action(self, gamestate):
        """Produce 1 additional food for the colony.

        gamestate -- The GameState, used to access game state information.
        """
        # BEGIN Problem 1
        gamestate.food += 1
        # END Problem 1


class ThrowerAnt(Ant):
    """ThrowerAnt throws a leaf each turn at the nearest Bee in its range."""

    name = 'Thrower'
    implemented = True
    damage = 1
    food_cost = 3
    min_range = 0
    max_range = float('inf')
    # ADD/OVERRIDE CLASS ATTRIBUTES HERE

    def nearest_bee(self):
        """Return the nearest Bee in a Place that is not the HIVE, connected to
        the ThrowerAnt's Place by following entrances.

        This method returns None if there is no such Bee (or none in range).
        """
        # BEGIN Problem 3 and 4
        distance = 0
        ideal_place = None

        place = self.place
        for _ in range(self.min_range):
            if(place.is_hive):
                return ideal_place
            place = place.entrance
            distance += 1
        while(not place.is_hive and distance <= self.max_range):
            if(place.bees != []):
                ideal_place = place
                if(self.name != 'long'):
                    break
            place = place.entrance
            distance += 1
        return random_bee(ideal_place.bees) if ideal_place else ideal_place
        # END Problem 3 and 4

    def throw_at(self, target):
        """Throw a leaf at the TARGET Bee, reducing its health."""
        if target is not None:
            target.reduce_health(self.damage)

    def action(self, gamestate):
        """Throw a leaf at the nearest Bee in range."""
        self.throw_at(self.nearest_bee())


def random_bee(bees):
    """Return a random bee from a list of bees, or return None if bees is empty."""
    assert isinstance(bees, list), "random_bee's argument should be a list but was a %s" % type(bees).__name__
    if bees:
        return random.choice(bees)

##############
# Extensions #
##############


class ShortThrower(ThrowerAnt):
    """A ThrowerAnt that only throws leaves at Bees at most 3 places away."""

    name = 'Short'
    food_cost = 2
    # OVERRIDE CLASS ATTRIBUTES HERE
    # BEGIN Problem 4
    implemented = True   # Change to True to view in the GUI
    max_range = 3
    # END Problem 4


class LongThrower(ThrowerAnt):
    """A ThrowerAnt that only throws leaves at Bees at least 5 places away."""

    name = 'Long'
    food_cost = 2
    # OVERRIDE CLASS ATTRIBUTES HERE
    # BEGIN Problem 4
    implemented = True   # Change to True to view in the GUI
    min_range = 5
    # END Problem 4


class FireAnt(Ant):
    """FireAnt cooks any Bee in its Place when it expires."""

    name = 'Fire'
    damage = 3
    food_cost = 5
    # OVERRIDE CLASS ATTRIBUTES HERE
    # BEGIN Problem 5
    implemented = True   # Change to True to view in the GUI
    # END Problem 5

    def __init__(self, health=3):
        """Create an Ant with a HEALTH quantity."""
        super().__init__(health)

    def reduce_health(self, amount):
        """Reduce health by AMOUNT, and remove the FireAnt from its place if it
        has no health remaining.

        Make sure to reduce the health of each bee in the current place, and apply
        the additional damage if the fire ant dies.
        """
        # BEGIN Problem 5        
        current_bees = list(self.place.bees)
        super().reduce_health(amount)

        if(self.health <= 0):
            attack = self.damage + amount
        else:
            attack = amount

        for i in current_bees:
            i.reduce_health(attack)
        # END Problem 5

# BEGIN Problem 6
class WallAnt(Ant):
    """
    WallAnt is a ant with large health
    """
    name = "Wall"
    food_cost = 4
    implemented = True

    def __init__(self, health=4):
        super().__init__(health)
# END Problem 6

# BEGIN Problem 7
class HungryAnt(Ant):
    """
    HungryAnt can eat a random bee in the same place per 3 round
    """
    name = "Hungry"
    food_cost = 4
    implemented = True
    chew_duration = 3

    def __init__(self, health=1):
        self.chew_countdown = 0
        super().__init__(health)
    
    def action(self, gamestate):
        if(self.chew_countdown == 0):
            if(self.place.bees != []):
                die_bee = random_bee(self.place.bees)
                die_bee.reduce_health(die_bee.health)
                self.chew_countdown += 1
        else:
            self.chew_countdown += 1
        self.chew_countdown = self.chew_countdown % (self.chew_duration + 1)
# END Problem 7


class ContainerAnt(Ant):
    """
    ContainerAnt can share a space with other ants by containing them.
    """
    is_container = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ant_contained = None

    def contained_ant(self):
        return True if self.ant_contained else False 

    def can_contain(self, other):
        # BEGIN Problem 8
        if(self.ant_contained == None and not isinstance(other,ContainerAnt)):
            return True
        else:
            return False
        # END Problem 8

    def store_ant(self, ant):
        # BEGIN Problem 8
        self.ant_contained = ant
        # END Problem 8

    def remove_ant(self, ant):
        if self.ant_contained is not ant:
            assert False, "{} does not contain {}".format(self, ant)
        self.ant_contained = None

    def remove_from(self, place):
        # Special handling for container ants (this is optional)
        if place.ant is self:
            # Container was removed. Contained ant should remain in the game
            place.ant = place.ant.ant_contained
            Insect.remove_from(self, place)
        else:
            # default to normal behavior
            Ant.remove_from(self, place)

    def action(self, gamestate):
        # BEGIN Problem 8
        if(self.ant_contained != None):
            self.ant_contained.action(gamestate)
        # END Problem 8


class BodyguardAnt(ContainerAnt):
    """BodyguardAnt provides protection to other Ants."""
    name = 'Bodyguard'
    food_cost = 4
    # OVERRIDE CLASS ATTRIBUTES HERE
    # BEGIN Problem 8
    implemented = True   # Change to True to view in the GUI
    # END Problem 8

    def __init__(self, health = 2):
        super().__init__(health)

# BEGIN Problem 9
class TankAnt(ContainerAnt):
    name = "Tank"
    food_cost = 6
    damage = 1
    implemented = True

    def __init__(self, health = 2):
        super().__init__(health)

    def action(self, gamestate):
        for bee in list(self.place.bees):
            bee.reduce_health(self.damage)
        return super().action(gamestate)
# END Problem 9


class Water(Place):
    """Water is a place that can only hold waterproof insects."""

    def add_insect(self, insect):
        """Add an Insect to this place. If the insect is not waterproof, reduce
        its health to 0."""
        # BEGIN Problem 10
        super().add_insect(insect)
        if(not insect.is_waterproof):
            insect.reduce_health(insect.health)
        # END Problem 10

# BEGIN Problem 11
class ScubaThrower(ThrowerAnt):
    name = 'Scuba'
    food_cost = 6
    is_waterproof = True
    implemented = True
    
    def __init__(self, health=1):
        super().__init__(health)
# END Problem 11

# BEGIN Problem 12


class QueenAnt(ScubaThrower):  # You should change this line
# END Problem 12
    """The Queen of the colony. The game is over if a bee enters her place."""

    name = 'Queen'
    food_cost = 7

    # BEGIN Problem 12
    implemented = True   # Change to True to view in the GUI
    # END Problem 12

    @classmethod
    def construct(cls, gamestate):
        """
        Returns a new instance of the Ant class if it is possible to construct, or
        returns None otherwise. Remember to call the construct() method of the superclass!
        """
        # BEGIN Problem 12
        if(not gamestate.Queen):
            gamestate.Queen = True
            return super().construct(gamestate)
        else:
            return None
        # END Problem 12

    def action(self, gamestate):
        """A queen ant throws a leaf, but also doubles the damage of ants
        in her tunnel.
        """
        # BEGIN Problem 12
        super().action(gamestate)

        current_place = self.place.exit
        while(current_place != None):
            if(current_place.ant != None and not current_place.ant.buffed ):
                current_place.ant.damage *= 2
                current_place.ant.buffed = True
            if(isinstance(current_place.ant,ContainerAnt) and current_place.ant.contained_ant() and not current_place.ant.ant_contained.buffed):
                current_place.ant.ant_contained.damage *= 2
                current_place.ant.ant_contained.buffed = True
            current_place = current_place.exit

        # END Problem 12

    def reduce_health(self, amount):
        """Reduce health by AMOUNT, and if the QueenAnt has no health
        remaining, signal the end of the game.
        """
        # BEGIN Problem 12
        self.health -= amount
        if(self.health <= 0):
            ants_lose()
        # END Problem 12

    def remove_from(self, place):
        pass


class AntRemover(Ant):
    """Allows the player to remove ants from the board in the GUI."""

    name = 'Remover'
    implemented = False

    def __init__(self):
        super().__init__(0)


class Bee(Insect):
    """A Bee moves from place to place, following exits and stinging ants."""

    name = 'Bee'
    damage = 1
    is_waterproof = True

    # OVERRIDE CLASS ATTRIBUTES HERE
    def __init__(self, health, place=None):
        self.slowed = False
        self.slowed_turn = 0
        self.scared = False
        self.scared_turn = 0
        super().__init__(health, place)

    def sting(self, ant):
        """Attack an ANT, reducing its health by 1."""
        ant.reduce_health(self.damage)

    def move_to(self, place):
        """Move from the Bee's current Place to a new PLACE."""
        self.place.remove_insect(self)
        place.add_insect(self)

    def blocked(self):
        """Return True if this Bee cannot advance to the next Place."""
        # Special handling for NinjaAnt
        # BEGIN Problem Optional 1
        return self.place.ant is not None and self.place.ant.blocks_path
        # END Problem Optional 1

    def action(self, gamestate):
        """A Bee's action stings the Ant that blocks its exit if it is blocked,
        or moves to the exit of its current place otherwise.

        gamestate -- The GameState, used to access game state information.
        """
        destination = self.place.exit

        # Extra credit: Special handling for bee direction
        if self.blocked():
            self.sting(self.place.ant)
            destination = None
        if(self.slowed):
            self.slowed_turn -= 1
            if(self.slowed_turn == 0):
                self.slowed = False
            if(gamestate.time % 2 == 1):
                return
        if(self.scared and self.scared_turn != 0):
            if(self.slowed and gamestate.time % 2 == 1):
                return
            elif(self.place.entrance.is_hive):
                self.scared_turn -= 1
                destination = None
            else:
                self.scared_turn -= 1
                destination = self.place.entrance
        if self.health > 0 and destination is not None:
            self.move_to(destination)

    def add_to(self, place):
        place.bees.append(self)
        Insect.add_to(self, place)

    def remove_from(self, place):
        place.bees.remove(self)
        Insect.remove_from(self, place)

    def slow(self, length):
        """Slow the bee for a further LENGTH turns."""
        # BEGIN Problem EC
        self.slowed = True
        self.slowed_turn += length
        # END Problem EC

    def scare(self, length):
        """
        If this Bee has not been scared before, cause it to attempt to
        go backwards LENGTH times.
        """
        # BEGIN Problem EC
        if(self.scared):
            return 
        else:
            self.scared = True
            self.scared_turn += length
        # END Problem EC


############
# Optional #
############

class NinjaAnt(Ant):
    """NinjaAnt does not block the path and damages all bees in its place.
    This class is optional.
    """

    name = 'Ninja'
    damage = 1
    food_cost = 5
    blocks_path = False
    # BEGIN Problem Optional 1
    implemented = True   # Change to True to view in the GUI
    # END Problem Optional 1

    def action(self, gamestate):
        # BEGIN Problem Optional 1
        if(self.place.bees != []):
            for i in list(self.place.bees):
                i.reduce_health(self.damage)
        # END Problem Optional 1

############
# Statuses #
############


class SlowThrower(ThrowerAnt):
    """ThrowerAnt that causes Slow on Bees."""

    name = 'Slow'
    food_cost = 4
    # BEGIN Problem EC
    implemented = True   # Change to True to view in the GUI
    # END Problem EC

    def throw_at(self, target):
        if target:
            target.slow(3)


class ScaryThrower(ThrowerAnt):
    """ThrowerAnt that intimidates Bees, making them back away instead of advancing."""

    name = 'Scary'
    food_cost = 6
    # BEGIN Problem EC
    implemented = True  # Change to True to view in the GUI
    # END Problem EC

    def throw_at(self, target):
        # BEGIN Problem EC
        if target:
            target.scare(2)
        # END Problem EC


class LaserAnt(ThrowerAnt):
    # This class is optional. Only one test is provided for this class.

    name = 'Laser'
    food_cost = 10
    damage = 2
    # BEGIN Problem Optional 2
    implemented = True  # Change to True to view in the GUI
    # END Problem Optional 2

    def __init__(self, health=1):
        super().__init__(health)
        self.insects_shot = 0

    def insects_in_front(self):
        # BEGIN Problem Optional 2
        distance = 0
        ant_dir = {}
        if(self.place.ant != self):
            ant_dir[self.place.ant] = distance #container
        if(self.place.bees != []):
            for i in self.place.bees:
                ant_dir[i] = distance
        place_now = self.place.entrance
        while(place_now != None and not place_now.is_hive):
            distance += 1
            if(place_now.ant != None):
                ant_dir[place_now.ant] = distance
            if(place_now.bees != []):
                for i in place_now.bees:
                    ant_dir[i] = distance
            place_now = place_now.entrance
        return ant_dir
        # END Problem Optional 2

    def calculate_damage(self, distance):
        # BEGIN Problem Optional 2
        attack = self.damage - 0.25 * distance - 0.0625 * self.insects_shot
        return 0 if attack <= 0 else attack
        # END Problem Optional 2

    def action(self, gamestate):
        insects_and_distances = self.insects_in_front()
        for insect, distance in insects_and_distances.items():
            damage = self.calculate_damage(distance)
            insect.reduce_health(damage)
            if damage:
                self.insects_shot += 1


##################
# Bees Extension #
##################

class Wasp(Bee):
    """Class of Bee that has higher damage."""
    name = 'Wasp'
    damage = 2


class Hornet(Bee):
    """Class of bee that is capable of taking two actions per turn, although
    its overall damage output is lower. Immune to statuses.
    """
    name = 'Hornet'
    damage = 0.25

    def action(self, gamestate):
        for i in range(2):
            if self.health > 0:
                super().action(gamestate)

    def __setattr__(self, name, value):
        if name != 'action':
            object.__setattr__(self, name, value)


class NinjaBee(Bee):
    """A Bee that cannot be blocked. Is capable of moving past all defenses to
    assassinate the Queen.
    """
    name = 'NinjaBee'

    def blocked(self):
        return False


class Boss(Wasp, Hornet):
    """The leader of the bees. Combines the high damage of the Wasp along with
    status immunity of Hornets. Damage to the boss is capped up to 8
    damage by a single attack.
    """
    name = 'Boss'
    damage_cap = 8
    action = Wasp.action

    def reduce_health(self, amount):
        super().reduce_health(self.damage_modifier(amount))

    def damage_modifier(self, amount):
        return amount * self.damage_cap / (self.damage_cap + amount)


class Hive(Place):
    """The Place from which the Bees launch their assault.

    assault_plan -- An AssaultPlan; when & where bees enter the colony.
    """
    is_hive = True

    def __init__(self, assault_plan):
        self.name = 'Hive'
        self.assault_plan = assault_plan
        self.bees = []
        for bee in assault_plan.all_bees:
            self.add_insect(bee)
        # The following attributes are always None for a Hive
        self.entrance = None
        self.ant = None
        self.exit = None

    def strategy(self, gamestate):
        exits = [p for p in gamestate.places.values() if p.entrance is self]
        for bee in self.assault_plan.get(gamestate.time, []):
            bee.move_to(random.choice(exits))
            gamestate.active_bees.append(bee)


class GameState:
    """An ant collective that manages global game state and simulates time.

    Attributes:
    time -- elapsed time
    food -- the colony's available food total
    places -- A list of all places in the colony (including a Hive)
    bee_entrances -- A list of places that bees can enter
    """

    def __init__(self, strategy, beehive, ant_types, create_places, dimensions, food=2):
        """Create an GameState for simulating a game.

        Arguments:
        strategy -- a function to deploy ants to places
        beehive -- a Hive full of bees
        ant_types -- a list of ant classes
        create_places -- a function that creates the set of places
        dimensions -- a pair containing the dimensions of the game layout
        """
        self.time = 0
        self.food = food
        self.strategy = strategy
        self.beehive = beehive
        self.ant_types = OrderedDict((a.name, a) for a in ant_types)
        self.dimensions = dimensions
        self.active_bees = []
        self.configure(beehive, create_places)
        self.Queen = False

    def configure(self, beehive, create_places):
        """Configure the places in the colony."""
        self.base = AntHomeBase('Ant Home Base')
        self.places = OrderedDict()
        self.bee_entrances = []

        def register_place(place, is_bee_entrance):
            self.places[place.name] = place
            if is_bee_entrance:
                place.entrance = beehive
                self.bee_entrances.append(place)
        register_place(self.beehive, False)
        create_places(self.base, register_place, self.dimensions[0], self.dimensions[1])

    def simulate(self):
        """Simulate an attack on the ant colony (i.e., play the game)."""
        num_bees = len(self.bees)
        try:
            while True:
                self.beehive.strategy(self)         # Bees invade
                self.strategy(self)                 # Ants deploy
                for ant in self.ants:               # Ants take actions
                    if ant.health > 0:
                        ant.action(self)
                for bee in self.active_bees[:]:     # Bees take actions
                    if bee.health > 0:
                        bee.action(self)
                    if bee.health <= 0:
                        num_bees -= 1
                        self.active_bees.remove(bee)
                if num_bees == 0:
                    raise AntsWinException()
                self.time += 1
        except AntsWinException:
            print('All bees are vanquished. You win!')
            return True
        except AntsLoseException:
            print('The ant queen has perished. Please try again.')
            return False

    def deploy_ant(self, place_name, ant_type_name):
        """Place an ant if enough food is available.

        This method is called by the current strategy to deploy ants.
        """
        ant_type = self.ant_types[ant_type_name]
        ant = ant_type.construct(self)
        if ant:
            self.places[place_name].add_insect(ant)
            self.food -= ant.food_cost
            return ant

    def remove_ant(self, place_name):
        """Remove an Ant from the game."""
        place = self.places[place_name]
        if place.ant is not None:
            place.remove_insect(place.ant)

    @property
    def ants(self):
        return [p.ant for p in self.places.values() if p.ant is not None]

    @property
    def bees(self):
        return [b for p in self.places.values() for b in p.bees]

    @property
    def insects(self):
        return self.ants + self.bees

    def __str__(self):
        status = ' (Food: {0}, Time: {1})'.format(self.food, self.time)
        return str([str(i) for i in self.ants + self.bees]) + status


class AntHomeBase(Place):
    """AntHomeBase at the end of the tunnel, where the queen resides."""

    def add_insect(self, insect):
        """Add an Insect to this Place.

        Can't actually add Ants to a AntHomeBase. However, if a Bee attempts to
        enter the AntHomeBase, a AntsLoseException is raised, signaling the end
        of a game.
        """
        assert isinstance(insect, Bee), 'Cannot add {0} to AntHomeBase'
        raise AntsLoseException()


def ants_win():
    """Signal that Ants win."""
    raise AntsWinException()


def ants_lose():
    """Signal that Ants lose."""
    raise AntsLoseException()


def ant_types():
    """Return a list of all implemented Ant classes."""
    all_ant_types = []
    new_types = [Ant]
    while new_types:
        new_types = [t for c in new_types for t in c.__subclasses__()]
        all_ant_types.extend(new_types)
    return [t for t in all_ant_types if t.implemented]


class GameOverException(Exception):
    """Base game over Exception."""
    pass


class AntsWinException(GameOverException):
    """Exception to signal that the ants win."""
    pass


class AntsLoseException(GameOverException):
    """Exception to signal that the ants lose."""
    pass


def interactive_strategy(gamestate):
    """A strategy that starts an interactive session and lets the user make
    changes to the gamestate.

    For example, one might deploy a ThrowerAnt to the first tunnel by invoking
    gamestate.deploy_ant('tunnel_0_0', 'Thrower')
    """
    print('gamestate: ' + str(gamestate))
    msg = '<Control>-D (<Control>-Z <Enter> on Windows) completes a turn.\n'
    interact(msg)

###########
# Layouts #
###########


def wet_layout(queen, register_place, tunnels=3, length=9, moat_frequency=3):
    """Register a mix of wet and and dry places."""
    for tunnel in range(tunnels):
        exit = queen
        for step in range(length):
            if moat_frequency != 0 and (step + 1) % moat_frequency == 0:
                exit = Water('water_{0}_{1}'.format(tunnel, step), exit)
            else:
                exit = Place('tunnel_{0}_{1}'.format(tunnel, step), exit)
            register_place(exit, step == length - 1)


def dry_layout(queen, register_place, tunnels=3, length=9):
    """Register dry tunnels."""
    wet_layout(queen, register_place, tunnels, length, 0)


#################
# Assault Plans #
#################

class AssaultPlan(dict):
    """The Bees' plan of attack for the colony.  Attacks come in timed waves.

    An AssaultPlan is a dictionary from times (int) to waves (list of Bees).

    >>> AssaultPlan().add_wave(4, 2)
    {4: [Bee(3, None), Bee(3, None)]}
    """

    def add_wave(self, bee_type, bee_health, time, count):
        """Add a wave at time with count Bees that have the specified health."""
        bees = [bee_type(bee_health) for _ in range(count)]
        self.setdefault(time, []).extend(bees)
        return self

    @property
    def all_bees(self):
        """Place all Bees in the beehive and return the list of Bees."""
        return [bee for wave in self.values() for bee in wave]