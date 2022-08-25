import os
from litemapy import Schematic, Region, BlockState
# from flying_machines import FlyingMachine
from breakers import Breaker

##### START

# Add inputs to these parameters
author = "GradientAscent" # What is your username? (Default is me: GradientAscent) *optional
geode_filename = "example_geode" # Choose your geode file
directionXZ = "southeast" # Which cardinal direction will the machines be coming from? *optional
directionY = "up" # Which vertical direction will the machines be coming from? *optional
schematic_name = f"Geode Farm stickyblocks placed 59" # Choose a name for your schematic *optional
schematic_description = "Generated using litemapy by SmylerMC. Farm solved by GradientAscent." # Describe your schematic *optional
immovableblockchosen = "obsidian" # Choose your immovable block for the walls (Default: obsidian) *optional

# Loads geode to farm
geode = Schematic.load(f"{geode_filename}.litematic")
geode_reg = list(geode.regions.values())[0]

# Parameters for farm direction and geode projection to axes with respect to direction
xDirection, zDirection = {"southeast":(1,1), "southwest":(-1,1), "northeast":(1,-1), "northwest":(-1,-1)}[directionXZ]
yDirection = {"up":1, "down":-1}[directionY]
minX, maxX, minY, maxY, minZ, maxZ = 0, geode.width, 0, geode.height, 0, geode.length
wallsExtraDistance, machinesExtraDistance = 3, 13
totalExtraDistance = wallsExtraDistance + machinesExtraDistance
buddingXYplane, buddingXZplane, buddingYZplane = [], [], []
slimeXYplane, slimeXZplane, slimeYZplane = [], [], []
honeyXYplane, honeyXZplane, honeyYZplane = [], [], []

# Create new region for the new schematic
reg = Region(0, 0, 0, totalExtraDistance + geode.width + 2, totalExtraDistance + geode.height + 2, totalExtraDistance + geode.length + 2)
farm = reg.as_schematic(name=schematic_name, author=author, description=schematic_description)
_x, _y, _z = int((farm.width-1)*(1 - xDirection)/2), int((farm.height-1)*(1 - yDirection)/2), int((farm.length-1)*(1 - zDirection)/2)
dists = {1:[wallsExtraDistance, machinesExtraDistance], -1:[machinesExtraDistance, wallsExtraDistance]}
projsadjust = lambda side, typedist: {1:typedist, -1:side - (typedist + 1)}

# Create the global block palette we are going to use
honeyblock = BlockState("minecraft:honey_block")
slimeblock = BlockState("minecraft:slime_block")
immovableblock = BlockState(f"minecraft:{immovableblockchosen}")
buddingamethyst = BlockState("minecraft:budding_amethyst")

# Calculate the ranges where the sticky blocks will go
xprojectionmachines = farm.width - (machinesExtraDistance - 2) if xDirection == 1 else (machinesExtraDistance - 2)
yprojectionmachines = farm.height - (machinesExtraDistance - 2) if yDirection == 1 else (machinesExtraDistance - 2)
zprojectionmachines = farm.length - (machinesExtraDistance - 2) if zDirection == 1 else (machinesExtraDistance - 2)
xadd = int((farm.width - dists[xDirection][0])*(1 - xDirection)/2) + int((dists[xDirection][0] + 1)*(xDirection + 1)/2)
yadd = int((farm.height - dists[yDirection][1] - 2*yDirection)*(yDirection + 1)/2) + int((dists[yDirection][0] - 9*yDirection)*(1 - yDirection)/2)
zadd = int((farm.length - dists[zDirection][0] - 1)*(1 - zDirection)/2) + int((dists[zDirection][0] + 1)*(zDirection + 1)/2)
for block in geode_reg.allblockpos():
    if geode_reg.getblock(block[0], block[1], block[2]).blockid == "minecraft:budding_amethyst":
        XYcoords = [block[0] + xadd, block[1] + yadd, zprojectionmachines]
        XZcoords = [block[0] + xadd, yprojectionmachines, block[2] + zadd]
        YZcoords = [xprojectionmachines, block[1] + yadd, block[2] + zadd]
        if XYcoords not in buddingXYplane:
            buddingXYplane.append(XYcoords)
        if XZcoords not in buddingXZplane:
            buddingXZplane.append(XZcoords)
        if YZcoords not in buddingYZplane:
            buddingYZplane.append(YZcoords)
        reg.setblock(block[0] + xadd, block[1] + yadd, block[2] + zadd, buddingamethyst)

xbreaker = Breaker(buddingYZplane, f"{'-'*int((xDirection + 1)/2)}x", [farm.width, farm.height, farm.length])
ybreaker = Breaker(buddingXZplane, f"{'-'*int((1 - yDirection)/2)}y", [farm.width, farm.height, farm.length])
zbreaker = Breaker(buddingXYplane, f"{'-'*int((zDirection + 1)/2)}z", [farm.width, farm.height, farm.length])

xbreaker.create_structure()
ybreaker.create_structure()
zbreaker.create_structure()

# Add sticky blocks and flying machines
breakers = xbreaker.allblockstates + ybreaker.allblockstates + zbreaker.allblockstates
for breaker in breakers:
    __x, __y, __z = tuple(breaker[1])
    reg.setblock(__x, __y, __z, breaker[0])

# Add walls
xWall, yWall, zWall = [],[],[]
xrange, yrange, zrange = range(dists[xDirection][0], farm.width - dists[xDirection][1]), range(dists[yDirection][0], farm.height - dists[yDirection][1]), range(dists[zDirection][0], farm.length - dists[zDirection][1])

for z in zrange:
    for y in yrange:
        xWall.append([_x, y, z])
for z in zrange:
    for x in xrange:
        yWall.append([x, _y, z])
for y in yrange:
    for x in xrange:
        zWall.append([x, y, _z])

walls = xWall + yWall + zWall
for wall in walls:
    __x, __y, __z = tuple(wall)
    reg.setblock(__x, __y, __z, immovableblock)

# Save the schematic
path = os.getenv('APPDATA') + '\.minecraft\schematics\geode-farms' # Find .minecraft/schematics
try: 
    os.mkdir(path) 
except:
    pass
farm.save(f"{path}\{schematic_name}.litematic") # Generate .litematic file and create geode-farms folder if not found

##### END