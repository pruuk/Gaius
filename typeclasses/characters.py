# -*- coding: utf-8 -*-
"""
Characters

Characters are (by default) Objects setup to be puppeted by Accounts.
They are what you "see" in game. The Character class in this module
is setup to be the "default" character type created by the default
creation commands.

"""
from evennia.objects.objects import DefaultCharacter
from .objects import ObjectParent
from evennia.utils import lazy_property
from world.traits import TraitHandler
from world.randomness import return_a_roll as roll


class Character(ObjectParent, DefaultCharacter):
    """
    The Character defaults to reimplementing some of base Object's hook methods with the
    following functionality:

    at_basetype_setup - always assigns the DefaultCmdSet to this object type
                    (important!)sets locks so character cannot be picked up
                    and its commands only be called by itself, not anyone else.
                    (to change things, use at_object_creation() instead).
    at_post_move(source_location) - Launches the "look" command after every move.
    at_post_unpuppet(account) -  when Account disconnects from the Character, we
                    store the current location in the pre_logout_location Attribute and
                    move it to a None-location so the "unpuppeted" character
                    object does not need to stay on grid. Echoes "Account has disconnected"
                    to the room.
    at_pre_puppet - Just before Account re-connects, retrieves the character's
                    pre_logout_location Attribute and move it back on the grid.
    at_post_puppet - Echoes "AccountName has entered the game" to the room.

    """
    # pull in handlers for traits, ability, skills
    @lazy_property
    def traits(self):
        """TraitHandler that manages character traits."""
        return TraitHandler(self)
    
    @lazy_property
    def ability(self):
        """Traithandler that manages ability scores and other attributes for the character"""
        return TraitHandler(self, db_attribute='ability')
    
    # TODO: Add skills
    
    def at_object_creation(self):
        "Called only at object creation and with update command."
        # clear attributes to avoid any conflicts as we change the character class
        self.ability.clear()
        
        # add in ability scores
        self.ability.add(key='Dex', name='Dexterity', type='static', \
            base=roll(False, 80, '2d20'), extra={'progression' : 0})
        self.ability.add(key='Str', name='Strength', type='static', \
            base=roll(False, 80, '2d20'), extra={'progression' : 0})
        self.ability.add(key='Vit', name='Vitality', type='static', \
            base=roll(False, 80, '2d20'), extra={'progression' : 0})
        self.ability.add(key='Per', name='Perception', type='static', \
            base=roll(False, 80, '2d20'), extra={'progression' : 0})
        self.ability.add(key='Wil', name='Willpower', type='static', \
            base=roll(False, 80, '2d20'), extra={'progression' : 0})
        
        # add in secondary abilities
        self.ability.add(key='mass', name='Mass', type='static', \
            base=roll(False, 75))
        self.ability.add(key="enc", name="Encumberance", type='counter', \
            base=0, max=(self.ability.Str.current * .5))
        self.ability.add(key='hp', name='Health', type='gauge', \
            base=int((self.ability.Vit.current * .5) + (self.ability.Wil.current * .5)))
        self.ability.add(key='sp', name='Stamina', type='gauge', \
            base=int((self.ability.Str.current * .25) + (self.ability.Vit.current * .25)+ \
            (self.ability.Wil.current * .25)))
        self.ability.add(key='cp', name='Conviction', type='gauge', \
            base=int((self.ability.Wil.current * .75) + (self.ability.Per.current * .25)))

        # add in storage for other needed info
        self.db.info = {'Target': None, 'Mercy': True, 'Default Attack': 'unarmed_strike', \
                        'In Combat': False, 'Position': 'standing', 'Sneaking' : False, \
                        'Wimpy': 20, 'Yield': 50, 'Title': None}
        self.db.wallet = {'GC': 0, 'SC': 0, 'CC': 100}