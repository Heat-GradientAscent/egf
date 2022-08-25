from litemapy import Region, BlockState

def vectorsadd(u, v):
    return [u[i] + v[i] for i in range(3)]

def vectorsaddqueue(U, vecs):
    for vec in vecs:
        U = vectorsadd(U, vec)
    return U

def vectorsnegate(vecs):
    newvecs = []
    for vec in vecs:
        newvecs.append([-n for n in vec])
    return tuple(newvecs)

def vectorscrossproduct(u, v):
    return [u[1]*v[2] - v[1]*u[2], u[0]*v[2] - v[0]*u[2], u[0]*v[1] - v[0]*u[1]]

def facing():
    pass

class FlyingMachine:
    def __init__(self, axis, block, blockpos, angle, machine_type="default"):
        _x, _y, _z = tuple(blockpos)
        self.__frontalblock = block ### CHANGE REGION TO A COORDINATES INPUT
        self.__axis = axis
        self.__origin = blockpos#region.getblock(blockpos)
        self.__angle = angle
        self.__machine_type = machine_type
        self.allblockstates = []
    
    def create_structure(self):
        # Now, some sacrilege
        u, d = posup, posdown = [0, 1, 0], [0, -1, 0]
        l, r = posleft, posright = [0, 0, -1], [0, 0, 1]
        f, b = posfront, posback = [1, 0, 0], [-1, 0, 0]

        facing = {"x":{"up":"up", "down":"down","front":"east", "back":"west", "left":"north", "right":"south"},
                  "-x":{"up":"up", "down":"down","front":"west", "back":"east", "left":"south", "right":"north"},
                  "y":{"up":"north", "down":"south","front":"down", "back":"up", "left":"west", "right":"east"},
                  "-y":{"up":"north", "down":"south","front":"up", "back":"down", "left":"east", "right":"west"},
                  "z":{"up":"up", "down":"down","front":"south", "back":"north", "left":"east", "right":"west"},
                  "-z":{"up":"up", "down":"down","front":"north", "back":"south", "left":"west", "right":"east"}
                }[self.__axis]

        if self.__axis == "-x":
            posup, posdown, posleft, posright, posfront, posback = u, d, r, l, b, f
        elif self.__axis == "y":
            posup, posdown, posleft, posright, posfront, posback = l, r, b, f, d, u
        elif self.__axis == "-y":
            posup, posdown, posleft, posright, posfront, posback = l, r, f, b, u, d
        elif self.__axis == "z":
            posup, posdown, posleft, posright, posfront, posback = u, d, f, b, r, l
        elif self.__axis == "-z":
            posup, posdown, posleft, posright, posfront, posback = u, d, b, f, l, r
        
        fu, fd, fl, fr = facing["up"], facing["down"], facing["left"], facing["right"]
        pu, pd, pl, pr = posup, posdown, posleft, posright
        
        if self.__angle == 90:
            facing["up"], facing["down"], facing["left"], facing["right"] = fl, fr, fd, fu
            posup, posdown, posleft, posright = pl, pr, pd, pu
        elif self.__angle == 180:
            facing["up"], facing["down"], facing["left"], facing["right"] = fd, fu, fr, fl
            posup, posdown, posleft, posright = pd, pu, pr, pl
        elif self.__angle == 270:
            facing["up"], facing["down"], facing["left"], facing["right"] = fr, fl, fu, fd
            posup, posdown, posleft, posright = pr, pl, pu, pd

        origin = vectorsaddqueue(self.__origin,[posback,posback])

        self.allvars = (origin, posup, posdown, posfront, posback, posleft, posright, facing)

        machines = {"default":self.assemble_default}
        machines[self.__machine_type]()

    def assemble_default(self):
        origin, posup, posdown, posfront, posback, posleft, posright, facing = self.allvars
        
        # Create all non-directional blocks (directional blocks are created at moment of machine assembly)
        frontstickyblocks, backstickyblocks = [BlockState(f"minecraft:{'honey' if self.__frontalblock.blockid == 'minecraft:slime_block' else 'slime'}_block") for _ in range(6)], [BlockState(f"minecraft:slime_block") for _ in range(3)]
        noteblock = BlockState("minecraft:note_block", properties={"note":"1", "powered":"false", "instrument":"basedrum"})
        immovableblock = BlockState("minecraft:obsidian")
        redstonelamp = BlockState("minecraft:redstone_lamp", properties={"lit":"false"})

        # Assemble the machine
        # Add all 6 sticky blocks
        self.allblockstates.append([frontstickyblocks[0],vectorsaddqueue(origin,[posup])])
        self.allblockstates.append([frontstickyblocks[1],vectorsaddqueue(origin,[posup,posup])])
        self.allblockstates.append([frontstickyblocks[2],vectorsaddqueue(origin,[posup,posup,posback])])
        self.allblockstates.append([frontstickyblocks[3],vectorsaddqueue(origin,[posup,posup,posback,posback])])
        self.allblockstates.append([frontstickyblocks[4],vectorsaddqueue(origin,[posup,posback,posback])])
        self.allblockstates.append([frontstickyblocks[5],vectorsaddqueue(origin,[posup,posback,posback,posback])])

        # Add all 3 extra sticky blocks
        self.allblockstates.append([backstickyblocks[0],vectorsaddqueue(origin,[posback,posback,posback,posback])])
        self.allblockstates.append([backstickyblocks[1],vectorsaddqueue(origin,[posback,posback,posback,posback,posback])])
        self.allblockstates.append([backstickyblocks[2],vectorsaddqueue(origin,[posback,posback,posback,posback,posback,posback])])

        # Add noteblock
        self.allblockstates.append([noteblock,vectorsaddqueue(origin,[posback,posback,posback,posback,posback,posback,posup])])

        # Add immovable block
        self.allblockstates.append([immovableblock,vectorsaddqueue(origin,[posback,posback,posback,posback,posback,posback,posback])])

        # Add redstone lamp
        self.allblockstates.append([redstonelamp,vectorsaddqueue(origin,[posback])])

        # Add sticky pistons
        self.allblockstates.append([BlockState("minecraft:sticky_piston", {"facing":facing["front"], "extended":"false"}),origin])
        self.allblockstates.append([BlockState("minecraft:sticky_piston", {"facing":facing["back"], "extended":"false"}),vectorsaddqueue(origin,[posback,posback,posback])])
        self.allblockstates.append([BlockState("minecraft:sticky_piston", {"facing":facing["front"], "extended":"false"}),vectorsaddqueue(origin,[posback,posback,posback,posback,posup])])
        
        # Add observers
        self.allblockstates.append([BlockState("minecraft:observer", { "powered":"false", "facing":facing["up"]}),vectorsaddqueue(origin,[posback,posup])])
        self.allblockstates.append([BlockState("minecraft:observer", { "powered":"false", "facing":facing["front"]}),vectorsaddqueue(origin,[posback,posback])])
        self.allblockstates.append([BlockState("minecraft:observer", { "powered":"false", "facing":facing["back"]}),vectorsaddqueue(origin,[posback,posback,posback,posback,posback,posup])])


if __name__ == "__main__":
    flyingmachine1 = FlyingMachine('-y',BlockState("minecraft:slime_block"),[15,15,15],0)
    flyingmachine1.create_structure()