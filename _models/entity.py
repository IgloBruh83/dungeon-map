from _enum.damageType import DamageType
from _enum.entityType import EntityType
from _enum.fraction import Fraction
from _enum.sizeCategory import SizeCategory
from math import ceil

class Entity :
    def __init__(self, location):

        # Identity
        self.id = 0

        # Transform
        self.location = location
        self.x, self.y = 0, 0
        self.scale = 1
        self.rotation = 0
        self.flipX = False

        # Graphics
        self.spriteUrl = "graphics/unitGraphics/PLACEHOLDER.png"

        # Game flags
        self.visible = True
        self.nameVisible = True
        self.movable = True
        self.alive = True
        self.grabbedBy = None

        # Info
        self.name = 'NoName_Entity'
        self.displayName = 'Unnamed Entity'
        self.entityType = EntityType.HUMANOID
        self.fraction = Fraction.NEUTRAL
        self.size = SizeCategory.MEDIUM

        # Stats
        self.armor = 10
        self.initiativeBonus = 0
        self.atr = {'STR':10, 'DEX':10, 'CON':10, 'INT':10, 'WIS':10, 'CHA':10}
        self.resistances = set()
        self.vulnerabilities = set()
        self.immunities = set()

        # Resources
        self.health = self.maxHealth = 1
        self.barrier = self.maxBarrier = 0
        self.movement = self.maxMovement = 9
        self.action = self.maxActions = 1
        self.bonusAction = self.maxBonusActions = 1
        self.reaction = True

    def takeDamage(self, amount: int, dmg_type: str):

        dmgtype = DamageType.from_label(dmg_type)
        mod = 1
        if dmgtype in self.resistances:
            mod *= 0.5
        if dmgtype in self.vulnerabilities:
            mod *= 2
        if dmgtype in self.immunities:
            mod *= 0
        delta = ceil(amount * mod)
        self.health -= delta

        if self.health > self.maxHealth:
            self.health = self.maxHealth
        if self.health < 0:
            self.health = 0

        return delta

    def save (self, forfeit_id=False):
        return {
            'id': 0 if forfeit_id else self.id,
            'spriteUrl': self.spriteUrl,
            'transform': {
                'pos': (self.x, self.y),
                'scale': self.scale,
                'rotation': self.rotation,
                'flipX': self.flipX
            },
            'info': {
                'name': self.name,
                'displayName': self.displayName,
                'entityType': self.entityType.label,
                'fraction': self.fraction.label,
                'size': self.size.label,
            },
            'flags': {
                'visible': self.visible,
                'movable': self.movable,
                'alive': self.alive,
                'nameVisible': self.nameVisible,
            },
            'stats': {
                'armor': self.armor,
                'initiativeBonus': self.initiativeBonus,
                'atr': self.atr,
                'resistances': [i.label for i in self.resistances],
                'vulnerabilities': [i.label for i in self.vulnerabilities],
                'immunities': [i.label for i in self.immunities]
            },
            'resources': {
                'health': (self.health, self.maxHealth),
                'barrier': (self.barrier, self.maxBarrier),
                'movement': (self.movement, self.maxMovement),
                'action': (self.action, self.maxActions),
                'bonusAction': (self.bonusAction, self.maxBonusActions),
                'reaction': self.reaction
            }
        }

    @classmethod
    def load (cls, data, location, entity_id_generator):
        _ = Entity(location)
        if data.get('id', 0) == 0:
            _.id = entity_id_generator()
        else:
            _.id = data.get('id')
        _.x, _.y = data['transform']['pos']
        _.scale = data['transform']['scale']
        _.rotation = data['transform']['rotation']
        _.flipX = data['transform'].get('flipX', False)

        _.spriteUrl = data['spriteUrl']

        _.name = data['info']['name']
        _.displayName = data['info']['displayName']
        _.entityType = EntityType.from_label(data['info']['entityType'])
        _.fraction = Fraction.from_label(data['info']['fraction'])
        _.size = SizeCategory.from_label(data['info']['size'])

        _.visible = data['flags']['visible']
        _.movable = data['flags']['movable']
        _.alive = data['flags']['alive']
        _.nameVisible = data['flags']['nameVisible']

        _.armor = data['stats']['armor']
        _.initiativeBonus = data['stats']['initiativeBonus']
        _.atr = data['stats']['atr']
        _.resistances = set(DamageType.from_label(i) for i in data['stats']['resistances'] )
        _.vulnerabilities = set(DamageType.from_label(i) for i in data['stats']['vulnerabilities'])
        _.immunities = set(DamageType.from_label(i) for i in data['stats']['immunities'])

        _.health, _.maxHealth = data['resources']['health']
        _.barrier, _.maxBarrier = data['resources']['barrier']
        _.movement, _.maxMovement = data['resources']['movement']
        _.action, _.maxActions = data['resources']['action']
        _.bonusAction, _.maxBonusActions = data['resources']['bonusAction']
        _.reaction = data['resources']['reaction']

        return _