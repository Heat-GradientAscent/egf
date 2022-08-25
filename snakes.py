from calendar import c
from typing import OrderedDict
from flying_machines import FlyingMachine
from litemapy import BlockState


class Snake:
    def __init__(self, axis, id = 0) -> None:
        self.count = 0
        self.cache = {}
        self.neighboors = []
        self.blocks = []
        self.stickyblock = []
        self.id = id
        self.threshold = 1
        self.incontact = {}
        self.allblockstates = []
        self.machine = []
        self.axis = axis
        self.waitingline = []
        self.wasmerged = False
        self.toucherBlock = BlockState('minecraft:glass')
        self.name = 'snake:' + str(self.id)
        self.needsMerge = False
        self.hasMerged = False

    def __repr__(self) -> str:
        return self.name
       
    def getmachine(self):
        pass
    
    def assemblesnake(self):
        touchingSnakes = [self.incontact[snake][1] for snake in self.incontact]
        touchingBlocks = []
        for blocks in touchingSnakes:
            for block in blocks:
                if block not in touchingBlocks:
                    touchingBlocks.append(f'{block}')
        for block in self.blocks:
            blockType = self.stickyblock[0]
            if (f'{block}' in touchingBlocks):
                blockType = self.toucherBlock
            self.allblockstates.append([blockType, block])
        self.machine = FlyingMachine(self.axis,self.stickyblock[0],self.blocks[0],90*self.count%360)
        self.machine.create_structure()
        self.allblockstates += self.machine.allblockstates
    
    def addblock(self, block, parentbreaker, skipwaitinglist = False, lookatthreshold = True):
        if (self.threshold > parentbreaker.threshold if lookatthreshold else lookatthreshold) and block not in self.blocks and block not in parentbreaker.usedstickyblocks:
            self.blocks.append(block)
            parentbreaker.usedstickyblocks.append(block)
            self.threshold *= .8
            self.count += 1
            parentbreaker.couldntassignblock = False
            if skipwaitinglist:
                return
            if block in self.waitingline:
                self.waitingline.pop(0)
                return
            hasblock, newblocks = parentbreaker.hasblockaround(block)
            for newblock in newblocks:
                if newblock in parentbreaker.allblockstates and newblock not in self.blocks:# and newblock not in parentbreaker.usedstickyblocks:
                    self.waitingline.append(newblock)
            for _block in self.waitingline:
                if self.threshold > parentbreaker.threshold:
                    self.addblock(_block, parentbreaker)
        else:
            parentbreaker.couldntassignblock = True
    
    def merge(self, othersnake):
        self.allblockstates += othersnake.allblockstates
        self.count += othersnake.count
        self.threshold *= othersnake.threshold**othersnake.count
        newcontacts = {}
        for contact in othersnake.incontact.values():
            if contact[0].id != self.id:
                newcontacts[contact[0].id] = contact[1]
        #     for contacted in contact[0].incontact.values():
        #         contactednewdict = {}
        #         if contacted[0].id != othersnake.id:
        #             contactednewdict[self.id] = contact[0].incontact[othersnake.id]
        #         contacted.incontact = contactednewdict
        self.incontact = {**self.incontact, **newcontacts}