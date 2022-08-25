from litemapy import BlockState
from flying_machines import FlyingMachine
from src.snakes import Snake
from copy import deepcopy as deep

class Breaker:
    def __init__(self, plane, axis, dimensions) -> None:
        self.__plane = plane
        self.__axis = axis
        self.__dimensions = dimensions
        self.allblockstates = []
    
    def create_structure(self):
        slime = BlockState("minecraft:slime_block")
        honey = BlockState("minecraft:honey_block")
        minx, miny, minz = tuple(self.__dimensions)

        # Take every block surrounding the projected plane of amethyst buddings
        for coords in self.__plane:
            for i, j, k in self.planeread():
                newcoords = [coords[0] + i, coords[1] + j, coords[2] + k]
                minx, miny, minz = min(minx, newcoords[0]), min(miny, newcoords[1]), min(minz, newcoords[2])
                self.assignblocktowall(newcoords)
        
        # Remove any blocks that can be surrounded by amethyst buddings from the projection
        for block in self.allblockstates:
            hasblock, aroundblocks = self.hasblockaround(block)
            for aroundblock in aroundblocks:
                if aroundblock in self.allblockstates:
                    hasblock = False
            if hasblock:
                self.allblockstates.remove(block)
        
        # Set threshold for restricting number of blocks per snake
        self.threshold = .05
        self.usedstickyblocks = []

        # Create all the snaking patterns that surround the amethyst buddings projection
        snakes = self.generatesnakes()

        # Connect snakes that touch
        for snake in snakes:
            for block in snake.blocks:
                hasblock, aroundblocks = self.hasblockaround(block)
                for aroundblock in aroundblocks:
                    for othersnake in snakes:
                        if aroundblock in othersnake.blocks and othersnake != snake:
                            othersnake.incontact[snake.id] = [snake, [block,aroundblock]]
                            snake.incontact[othersnake.id] = [othersnake, [aroundblock, block]]
        
        # Merge small snakes that touch
        newsnakes = []
        for snake in snakes:
            if snake.count < 4:
                snake.needsMerge = True
        for snake in snakes:
            if snake.needsMerge and not snake.hasMerged:
                for contact in snake.incontact.values():
                    if snake.count > 3:
                        snake.hasMerged = True
                        snake.needsMerge = False
                        break
                    snake.merge(contact[0])
            if (not snake.needsMerge):
                newsnakes.append(snake)
        snakes = newsnakes

        # Unmerge large snakes


        # Attend discrepancies between snakes
        # ;-;

        # Assign sticky blocks to snakes
        for snake in snakes:
            print (snake.incontact)
            for contacted in snake.incontact:
                if snake.incontact[contacted][0].stickyblock == [slime]:
                    snake.stickyblock = [honey]
                elif snake.incontact[contacted][0].stickyblock == [honey]:
                    snake.stickyblock = [slime]
                elif snake.incontact[contacted][0].stickyblock == []:
                    snake.stickyblock = [slime]
                break
        
        # for snake in snakes:
        #     print (snake.stickyblock[0], snake.incontact)
        # exit()
        
        # Add snakes and machines to the breaker
        self.allblockstates = []
        for snake in snakes:
            print (self.__axis, 'start with', snake)
            snake.assemblesnake()
            self.allblockstates += snake.allblockstates
        print ()
    
    def assignblocktowall(self, newcoords):
        if newcoords not in self.allblockstates and newcoords not in self.__plane:
            self.allblockstates.append(newcoords)
    
    def hasblockaround(self, block):
        blocksaround = []
        ifhasblock = False
        for i, j, k in self.planeread([[-1, -1], [1, -1], [-1, 1], [1, 1]]):
            if [block[0] + i, block[1] + j, block[2] + k] in [[block[0]+1, block[1], block[2]], [block[0]-1, block[1] , block[2]], [block[0], block[1]+1, block[2]], [block[0], block[1]-1, block[2]], [block[0], block[1], block[2]+1], [block[0], block[1], block[2]-1]]:
                ifhasblock = True
                blocksaround.append([block[0] + i, block[1] + j, block[2] + k])
        return True, blocksaround

    def planeread(self, unnecessary = []):
        for a,b in self.doubleloop(unnecessary):
            if self.__axis in ["x", "-x"]:
                yield 0, a, b
            elif self.__axis in ["y", "-y"]:
                yield a, 0, b
            elif self.__axis in ["z", "-z"]:
                yield a, b, 0

    def doubleloop(self, unnecessary = []):
        unnecessary = unnecessary #[[-1, -1], [1, -1], [-1, 1], [1, 1]]
        for i in range(-1, 2):
            for j in range(-1, 2):
                if [i, j] in unnecessary:
                    yield 0, 0
                else:
                    yield i, j
    
    def generatesnakes(self):
        snakes = [Snake(self.__axis, id=_) for _ in range(20)]
        for snake in snakes:
            for block in self.allblockstates:
                if snake.blocks == []:
                    snake.addblock(block, self)
                hasblock, usedblocks = self.hasblockaround(block)
                if hasblock:
                    for usedblock in usedblocks:
                        if usedblock in snake.blocks:
                            snake.addblock(block, self)
        newsnakes = []
        for snake in snakes:
            if snake.count > 0:
                newsnakes.append(snake)
        return newsnakes

    def _generatesnakes1(self, snakes, lookatthreshold = True):
        i = 0
        snake = snakes[i]
        hasblock = False
        self.couldntassignblock = False
        for block in self.allblockstates:
            if block not in self.usedstickyblocks:
                if snake.count == 0:
                    snake.addblock(block, self, lookatthreshold)
                    continue
                else:
                    hasblock, oldblocks = self.hasblockaround(block)
                    for oldblock in oldblocks:
                        if oldblock in snake.blocks:
                            snake.addblock(block, self, lookatthreshold)
                            continue
                if self.couldntassignblock:
                    hasblock, oldblocks = self.hasblockaround(block)
                    for _snake in snakes:
                        for oldblock in oldblocks:
                            if oldblock in _snake.blocks and snake != _snake and block not in _snake.blocks:
                                _snake.threshold /= .8
                                _snake.addblock(block, self)
                    if block not in self.usedstickyblocks:
                        snakes.append(snake := Snake(self.__axis))
                        snake.id = len(snakes) - 1
                        self.couldntassignblock = False
                        snake.addblock(block, self, lookatthreshold)
            if not hasblock and len(self.usedstickyblocks) < len(self.allblockstates):
                continue
        return snakes