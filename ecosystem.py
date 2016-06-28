#Conor Oliver
#10 May 2016

import sys, pygame, random, time
pygame.init()

WINDOW_HEIGHT = 800
WINDOW_WIDTH = 1200
WINDOW_SIZE = WINDOW_WIDTH, WINDOW_HEIGHT

TILE_SIZE = 50 #size of tiles
H_TILES = WINDOW_WIDTH/TILE_SIZE #number of horizontal tiles
V_TILES = WINDOW_HEIGHT/TILE_SIZE #number of vertical tiles

TRI_SCALE = TILE_SIZE/ 631 #scale of triceratops to fit into tile size
TREX_SCALE = TILE_SIZE/1300 #scale of trex to fit into tile size
GRASS_SCALE = TILE_SIZE/ 300
APPLE_SCALE = TILE_SIZE/ 1300

START_HEALTH = 2500
ACTION_COST = 200
FOOD = 1000

TT_INTERVAL = 1000
TR_INTERVAL = 1200 #slightly slower

NUMBER_TTOPS = 20

WHITE = 135, 206, 250

ttop_arr = [] #array of triceratops objects
trex_arr = [] #array of trex objects
grass_arr = [] #array of grass objects
poison_arr = [] #array of poison objects
allx_arr = []
ally_arr = []

#coordinate lists done for speed (faster than objects probably)
grass_cor = []
ttop_cor = []
trex_cor = []
poison_cor = []

#dead_ttops = []

#################
class Trex(object):
    def __init__(self, x, y, image):
        self.alive = True
        self.x = x
        self.y = y
        self.image = image
    
    def nearest_top(self, ttop_cor):
        #print "rex moving"
        index = 0 #index of closest triceratops
        distance = 1000000
        for n in range(len(ttop_cor)):
            ttopx = ttop_cor[n][0]
            ttopy = ttop_cor[n][1]
            if ttopx == self.x and ttopy == self.y:
                #print self.x, " ", grass.x, " ", self.y, " ", grass.y 
                self.eat_top(n)
                #print "trex eating"
                return (self.x, self.y)
            curr_x_distance = self.x - ttopx
            curr_y_distance = self.y - ttopx
            if abs(curr_x_distance) + abs(curr_y_distance) < distance:
                distance = abs(curr_x_distance) + abs(curr_y_distance)
                index = n
                
        ttopx = ttop_cor[index][0]
        ttopy = ttop_cor[index][1]
        difx = self.x - ttopx
        dify = self.y - ttopy
        if abs(dify) >= abs(difx): #move vertically
            if dify < 0: # move north
                self.move(self.x, self.y  + TILE_SIZE)
            else:
                self.move(self.x, self.y - TILE_SIZE)
        else:
            if difx < 0: # move north
                self.move(self.x + TILE_SIZE, self.y)
            else:
                self.move(self.x - TILE_SIZE, self.y)
        return (self.x, self.y)

    def eat_top(self, index):
        ttop_arr[index].health = 0
        #dead_ttops.append(ttop_arr[index])
        del ttop_arr[index]
        del ttop_cor[index]
        
    def move(self, x, y):
        self.x = x
        self.y = y
        


##################
class TriTop(object):
    def __init__(self, x, y, health, chomosone, image):
        self.alive = True
        self.x = x
        self.y = y
        self.grassP = False #grass present in same tile
        self.health = health
        self.chomosone = chomosone
        self.image = image
        self.actions_list = [] #type: (chomosome index, index of array to perform action)

    def probe(self, trex_cor, grass_cor, poison_cor, ttop_cor):
        if len(poison_cor) > 0:
            poison_index = self.nearest_object(poison_cor, 0)
            if poison_index >= 0: #found rex
                self.actions_list.append((2, poison_index))
        if len(grass_cor) > 0:
            grass_index = self.nearest_object(grass_cor, 1) #index of nearest grass in grass_arr            
            if grass_index >= 0: #founbd grass within range
                self.actions_list.append((3, grass_index))
        if len(ttop_cor) > 0:
            ttop_index = self.nearest_object(ttop_cor, 2)
            if ttop_index >= 0:
                if ttop_cor[ttop_index] != (self.x, self.y): #found ttop
                    self.actions_list.append((4, ttop_index))
        if len(trex_cor) > 0:
            rex_index = self.nearest_object(trex_cor, 2)
            if rex_index >= 0: #found rex
                self.actions_list.append((5, rex_index))   
        
        return self.execute(trex_cor, grass_cor, poison_cor, ttop_cor)
    
    ###########                         
    def execute(self, trex_cor, grass_cor, poison_cor, ttop_cor): 
        
        n = 0
        while n < len(self.actions_list): #filtering out ignores from actionlist
            action = self.actions_list[n]
            if action[0] == 0:
                if self.chomosone[0] == 1:
                    del self.actions_list[n]
                    n -= 1
            elif action[0] == 1:
                if self.chomosone[1] == 1:
                    del self.actions_list[n]
                    n -= 1
            elif action[0] == 3:
                if self.chomosone[3] == 3:
                    del self.actions_list[n]
                    n -= 1
            elif action[0] ==4:
                if self.chomosone[4] == 3:
                    del self.actions_list[n]
                    n -= 1
            elif action[0] == 5:
                if self.chomosone[5] == 3:
                    del self.actions_list[n]
                    n -= 1
            n+= 1

        if len(self.actions_list) == 0: #run default
            self.move_random()
            #print "actions empty"
            return (self.x, self.y)
   
        #print "actions possible = ", self.actions_list
        if len(self.actions_list) > 0:
            m = 7
            found = False
            while m < len(self.chomosone) and found == False:
                for n in range(len(self.actions_list)):
                    action = self.actions_list[n]
                    if self.chomosone[m] == action[0]: #do this action
                        found = True
                        break
                m += 1
        #print "action choice = ", action
        index = action[1]
        action = action[0]
        if action ==  0:
            if self.chomosone[0] == 0:
                self.eat(poison_cor, index, 0)
                return (self.x, self.y)
            else:
                return (self.x, self.y)
        if action == 1:
            if self.chomosone[1] == 0:
                self.eat(grass_cor, index, 1)
                return (self.x, self.y)
            else:
                return (self.x, self.y)
        if action == 2:
            if self.chomosone[2] == 0:
                return self.move_towards(poison_cor, index)
            elif self.chomosone[2] == 1:
                return self.move_away(poison_cor, index)
            elif self.chomosone[2] == 2:
                return self.move_random()
            else:
                return (self.x, self.y)
        if action == 3:
            if self.chomosone[3] == 0:
                return self.move_towards(grass_cor, index)
            elif self.chomosone[3] == 1:
                return self.move_away(grass_cor, index)
            elif self.chomosone[3] == 2:
                return self.move_random()
            else:
                return (self.x, self.y)
        if action == 4:
            if self.chomosone[4] == 0:
                return self.move_towards(ttop_cor, index)
            elif self.chomosone[4] == 1:
                return self.move_away(ttop_cor, index)
            elif self.chomosone[4] == 2:
                return self.move_random()
            else:
                return (self.x, self.y)
        if action == 5:
            if self.chomosone[5] == 0:
                return self.move_towards(trex_cor, index)
            elif self.chomosone[5] == 1:
                return self.move_away(trex_cor, index)
            elif self.chomosone[5] == 2:
                return self.move_random()
            else:
                return (self.x, self.y)

        print "defaulted"
        return (self.x, self.y)
            
            

    def move_random(self):
        r = random.randrange(0, 4)
        if r == 0:
            self.move(self.x, self.y + TILE_SIZE)
        if r == 1:
            self.move(self.x, self.y - TILE_SIZE)
        if r == 2:
            self.move(self.x + TILE_SIZE, self.y)
        if r == 3:
            self.move(self.x - TILE_SIZE, self.y)
        return (self.x, self.y)
            
        
    def move_towards(self, cor, index):
        goalx = cor[index][0]
        goaly = cor[index][1]
        difx = self.x - goalx
        dify = self.y - goaly
        if abs(dify) >= abs(difx): #move vertically
            if dify < 0: # move north
                self.move(self.x, self.y  + TILE_SIZE)
            else:
                self.move(self.x, self.y - TILE_SIZE)
        else:
            if difx < 0: # move north
                self.move(self.x + TILE_SIZE, self.y)
            else:
                self.move(self.x - TILE_SIZE, self.y)
        return (self.x, self.y)
                

    def move_away(self, cor, index):
                  
                
        goalx = cor[index][0]
        goaly = cor[index][1]
        difx = self.x - goalx
        dify = self.y - goaly
        if abs(dify) >= abs(difx): #move vertically
            if dify < 0: 
                self.move(self.x, self.y  - TILE_SIZE)
            else:
                self.move(self.x, self.y + TILE_SIZE)
        else:
            if difx < 0: 
                self.move(self.x - TILE_SIZE, self.y)
            else:
                self.move(self.x + TILE_SIZE, self.y)
        return (self.x, self.y)

        
    def move(self, x, y):
        #print "ttop moving!!"
        if x >= WINDOW_WIDTH - TILE_SIZE:#cant move right
            #print "s1"
            return
        elif x <= -TILE_SIZE:#cant move left
            #print "s2"
            return
        elif y >= WINDOW_HEIGHT - TILE_SIZE:#cant move south
            #print "s3"
            return 
        elif y <= -TILE_SIZE:#cant move north
            #print "s4"
            return
        else:
            self.x = x
            self.y = y
            self.health -= ACTION_COST

    def eat(self, cor_list, index, kind): #0 == poison, 1 = grass
        #print "eating"
        if kind == 1:
            del grass_arr[index]
            del grass_cor[index]
            self.health += FOOD
        else:
            del poison_arr[index]
            del poison_cor[index]
            self.health = 0

    def nearest_object(self, cor, kind): #0 = poison,  1= grass, 2 = other
        index = -1 #index of closest grass
        distance = TILE_SIZE * 20 #within certain range tiles
        found = False
        for n in range(len(cor)):
            #print "cor =", cor[n]
            objectx = cor[n][0]
            objecty = cor[n][1]
            if objectx == self.x and objecty == self.y:
                #print self.x, " ", grass.x, " ", self.y, " ", grass.y
                if kind == 0:#poison
                    self.actions_list.append((0, n))
                elif kind == 1:#grass
                    self.actions_list.append((1, n))
                #print "on grass"
                return n
            curr_x_distance = self.x - objectx
            curr_y_distance = self.y - objecty
            if abs(curr_x_distance) + abs(curr_y_distance) < distance:
                #print "is true"
                distance = abs(curr_x_distance) + abs(curr_y_distance)
                index = n
                found = True

        return index


#############        
            

class Poison(object):
    def __init__(self, x, y, image):
        self.x = x
        self.y = y
        self.image = image
#############
class Grass(object):
    def __init__(self, x, y, image):
        self.x = x
        self.y = y
        self.image = image

####
window = pygame.display.set_mode(WINDOW_SIZE) #create graphics window
####

def generateTri(numTris, genes):
    tri_image = pygame.image.load("tritops.gif").convert_alpha()
    tri_image = pygame.transform.scale(tri_image, (TILE_SIZE, TILE_SIZE))#scale image to tile size

    for x in range(0, numTris):
        newX = random.randrange(0, WINDOW_WIDTH - TILE_SIZE, TILE_SIZE)
        newY = random.randrange(0, WINDOW_HEIGHT - TILE_SIZE, TILE_SIZE)
        if len(allx_arr) > 0:
            for n in range(0, len(allx_arr) - 1):
                if newX == allx_arr[n] and newY == ally_arr[n]:
                    newX = random.randrange(0, WINDOW_WIDTH - TILE_SIZE, TILE_SIZE)
                    newY = random.randrange(0, WINDOW_HEIGHT - TILE_SIZE, TILE_SIZE)#pick new random location
        allx_arr.append(newX)
        ally_arr.append(newY)
        health = START_HEALTH
        chomosone = []
        if genes == 0:
            chomosone = [random.randrange(0,1),random.randrange(0,1),random.randrange(0,3),random.randrange(0,3),random.randrange(0,3),random.randrange(0,3),random.randrange(0,4)]
            weight = [0,1,2,3,4,5]
            random.shuffle(weight)
            chomosone = chomosone + weight
        else:
            split_point = random.randrange(0,12)
            n = 0
            while n < split_point:
                chomosone.append(genes[0][n])
                n += 1
            while split_point < 13:
                chomosone.append(genes[1][split_point])
                split_point += 1
            n = 0
            while n < len(chomosone):
                mutation = random.randrange(0, 60)
                if mutation == 7: #change chomosone
                    print "mutate"
                    if n == 0 or n == 1:
                        chomosone[n] = random.randrange(0,1)
                    if n > 1 and n < 5:
                        chomosone[n] = random.randrange(0,3)
                    else:
                        temp = chomosone[n]                        
                        switch = random.randrange(n, len(chomosone))
                        chomosone[n] = chomosone[switch]
                        chomosone[switch] = temp
                n += 1


            
        ttop_arr.append(TriTop(newX, newY, health, chomosone, tri_image))
        ttop_cor.append((newX, newY))
#######
def generateTrex(numTrex):
    rex_image = pygame.image.load("trex.gif").convert_alpha()
    rex_image = pygame.transform.scale(rex_image, (TILE_SIZE, TILE_SIZE))

    for x in range(0, numTrex):
        newX = random.randrange(0, WINDOW_WIDTH - TILE_SIZE, TILE_SIZE)
        newY = random.randrange(0, WINDOW_HEIGHT - TILE_SIZE, TILE_SIZE)
        if len(allx_arr) > 0:
            for n in range(0, len(allx_arr) - 1):
                if newX == allx_arr[n] and newY == ally_arr[n]:
                    newX = random.randrange(0, WINDOW_WIDTH - TILE_SIZE, TILE_SIZE)
                    newY = random.randrange(0, WINDOW_HEIGHT - TILE_SIZE, TILE_SIZE)#pick new random location
        allx_arr.append(newX)
        ally_arr.append(newY)
        trex_arr.append(Trex(newX, newY, rex_image))
        trex_cor.append((newX, newY))
    
#######
def generateGrass(numGrass):
    grass_image = pygame.image.load("grass.gif").convert_alpha()
    grass_image = pygame.transform.scale(grass_image, (TILE_SIZE, TILE_SIZE))

    for x in range(0, numGrass):
        newX = random.randrange(0, WINDOW_WIDTH - TILE_SIZE, TILE_SIZE)
        newY = random.randrange(0, WINDOW_HEIGHT - TILE_SIZE, TILE_SIZE)
        if len(allx_arr) > 0:
            for n in range(0, len(allx_arr) - 1):
                if newX == allx_arr[n] and newY == ally_arr[n]:
                    newX = random.randrange(0, WINDOW_WIDTH - TILE_SIZE, TILE_SIZE)
                    newY = random.randrange(0, WINDOW_HEIGHT - TILE_SIZE, TILE_SIZE)
        allx_arr.append(newX)
        ally_arr.append(newY)
        grass_arr.append(Grass(newX, newY, grass_image))
        grass_cor.append((newX, newY))

#######        
def generatePoison(numPoison):
    poison_image = pygame.image.load("apple.gif").convert_alpha()
    poison_image = pygame.transform.scale(poison_image, (TILE_SIZE, TILE_SIZE))

    for x in range(0, numPoison):
        newX = random.randrange(0, WINDOW_WIDTH - TILE_SIZE, TILE_SIZE)
        newY = random.randrange(0, WINDOW_HEIGHT - TILE_SIZE, TILE_SIZE)
        if len(allx_arr) > 0:
            for n in range(0, len(allx_arr) - 1):
                if newX == allx_arr[n] and newY == ally_arr[n]:
                    newX = random.randrange(0, WINDOW_WIDTH - TILE_SIZE, TILE_SIZE)
                    newY = random.randrange(0, WINDOW_HEIGHT - TILE_SIZE, TILE_SIZE)
        allx_arr.append(newX)
        ally_arr.append(newY)
        poison_arr.append(Poison(newX, newY, poison_image))
        poison_cor.append((newX, newY))


def sort_chomosone(): #takes ttop list and sorts, picks two chomosones, tournament style
    fittest = ttop_arr[0]
    fittest2 = ttop_arr[0]
    if len(ttop_arr) == 0:
        print "generated random"
        chomosone = [random.randrange(0,1),random.randrange(0,1),random.randrange(0,3),random.randrange(0,3),random.randrange(0,3),random.randrange(0,3),random.randrange(0,4)]
        weight = [0,1,2,3,4,5]
        random.shuffle(weight)
        chomosone = chomosone + weight
        return (chomosone, chomosone)
    if len(ttop_arr) > 20:
        index = random.randrange(0,len(ttop_arr)- 5)
    else:
        index = 0
    n = 0
    while index < len(ttop_arr):
        if ttop_arr[index].health > fittest.health:
            print "here"
            fittest2 = fittest
            fittest = ttop_arr[index]
        elif ttop_arr[index].health > fittest2.health:
            fittest2 = ttop_arr[index]
        index += 1
    ttops = ttop_arr # + dead_ttops
    total_fitness = 0
    for ttop in ttops:
        print ttop.health
        total_fitness += ttop.health
    avg_fitness = total_fitness / NUMBER_TTOPS
    output = str(avg_fitness) + " "
    print avg_fitness, " = avg_fitness and there are ", len(ttop_arr), "left alive"
    text_file.write(output)
    print fittest.health, " ", fittest2.health
    return (fittest.chomosone, fittest2.chomosone)

#def reset_dead_ttops():
    #dead_ttops = []
    #print len(dead_ttops), " = length"
    
#######     
def drawObjectArr(arr): #takes array of objects that have images
    if len(arr) == 0:
       return
    for n in range(0, len(arr)):
        location = arr[n].x, arr[n].y
        window.blit(arr[n].image, location)


print "generated"

font = pygame.font.SysFont("monospace", 60)
label = font.render("finished!!", 1,(168, 45, 93))

run = True
last_time = pygame.time.get_ticks()
last_time1 = pygame.time.get_ticks()

curr_time = pygame.time.get_ticks()
gen_count = 0

text_file = open("averageFitness.txt", "w")

time_modifier = 0
num_moves = 20
while gen_count < 25 and run == True: # run 10 generations
    #reset_dead_ttops()
    #print dead_ttops
    label = font.render(str(gen_count + 1), 1,(168, 45, 93))
    grass_arr = []
    grass_cor = []
    poison_arr = []
    poison_cor = []
    trex_arr = []
    trex_cor = []
    allx_arr = []
    ally_arr = []
    generateTrex(4)
    generateGrass(120)
    generatePoison(20)
    if gen_count == 0:
        generateTri(NUMBER_TTOPS, 0) #generate random 1st gen
    else:
        genes = sort_chomosone()
        print "should generate now"
        ttop_arr = []
        ttop_cor = []
        generateTri(NUMBER_TTOPS, genes) #generate on chomosone
        
    while run == True and curr_time - time_modifier < TT_INTERVAL * num_moves: #loop for animation
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
        curr_time = pygame.time.get_ticks()
        if curr_time - last_time > TT_INTERVAL:
            n = 0
            
            while n < len(ttop_arr):
                #print "dealing with ttop"
                newLoc = ttop_arr[n].probe(trex_cor, grass_cor, poison_cor, ttop_cor)
                ttop_cor[n] = newLoc
                ttop_arr[n].actions_list = []#reset actions list
                if ttop_arr[n].health <= 0: #is dead
                    #dead_ttops.append(ttop_arr[n])
                    del ttop_arr[n] #removed from array
                    del ttop_cor[n]
                    n -= 1
                n += 1
                last_time = curr_time
                
        curr_time = pygame.time.get_ticks()
        if curr_time - last_time1 > TR_INTERVAL:
            m = 0
            #print "dealing with trex"
            while m < len(trex_arr) and len(ttop_arr) > 0:
                rex = trex_arr[m]
                new_loc_trex = rex.nearest_top(ttop_cor)
                trex_cor[m] = new_loc_trex
                last_time1 = curr_time
                m += 1

        window.fill(WHITE)
        drawObjectArr(ttop_arr)
        drawObjectArr(trex_arr)
        drawObjectArr(grass_arr)
        drawObjectArr(poison_arr)
        window.blit(label, (50, 50))
        pygame.display.flip()
    gen_count+= 1
    time_modifier = TT_INTERVAL * num_moves * gen_count

text_file.close()
pygame.quit()


