# -*- coding: utf-8 -*-
"""
Room

Rooms are simple containers that has no location of their own.

"""

from evennia.objects.objects import DefaultRoom
from .objects import ObjectParent
from evennia.utils import lazy_property
from world.traits import TraitHandler


class Room(ObjectParent, DefaultRoom):
    """
    Rooms are like any Object, except their location is None
    (which is default). They also use basetype_setup() to
    add locks so they cannot be puppeted or picked up.
    (to change that, use at_object_creation instead)

    See mygame/typeclasses/objects.py for a list of
    properties and methods available on all Objects.
    """

    # pull in handlers for traits, ability, skills
    @lazy_property
    def traits(self):
        """TraitHandler that manages character traits."""
        return TraitHandler(self)
    
    # TODO: Add biomes
    
    def at_object_creation(self):
        "Called only at object creation and with update command."
        # clear traits to avoid any conflicts as we change the room class
        self.traits.clear()
        
        # set traits at room creation
        self.traits.add(key="elevation", name="Elevation", type="static", \
            base=1000) # elevation above sea level in meters
        # ruggedness of terrain from 0.01 to 1. How hard is it to move across
        # this room? combination of slope and terrain obstacles
        self.traits.add(key="rot", name="Ruggedness of Terrain", \
                        type="static", base=0.05)
        # size of room, rough measure in square meters, default is large outdoor
        # room 100m X 100m
        self.traits.add(key="size", name="Room Size", \
                        type="static", base=10000)
        # maximum number of tracks to store. Some terrain allows for tracks to
        # be readable even with a large amount of foot traffic.
        self.traits.add(key="trackmax", name="Maximum Readable Tracks", \
                        type="static", base=(round(self.traits.size.actual / 500))) # default of 20
        # add encumberance to room to limit the amount of junk that can be
        # dropped in a given room
        self.traits.add(key="enc", name="Encumberance", type='counter', \
                        base=0, max=(self.traits.size.actual * 10))
        # Info traits of the room. Zone and environment type should be None or a stored object
        self.db.info = {'Non-Combat Room': False, 'Outdoor Room': True, \
                        'Zone': None, 'Environment Type': None}
        # empty db attribute dictionary for storing track objects
        self.db.tracks = {}