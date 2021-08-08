from collections import Counter
import random
from pgwidget.pgwidget_core import Grid #pip install pgwidget

grid=Grid([10, 10], [20, 20], 60,60)

terrain_color_dict={"flood_plains":(100,255,200),"oasis":(200,200,100),"savanna":(220,220,70),"tropical grassland":(50,250,50),"jungle":(50,200,50),
                    "desert":(220,220,150),"grassland":(120,220,120),"taiga":(150,250,150),"tundra":(220,230,220),
                    "snow":(255,255,255),"deciduous forest":(0  ,250,120),"coniferous forest":(100,180,120),
                    "mountain":(150,130,50),"swamp":(150,170,00),
                    "water":(100,100,250)                  
                    }

terrain_latitude_probability_dict={
                            "flood_plains":[0,0,0,0,0,0,1,2,1,0,0,0,0,0,0],
                                   "oasis":[0,0,0,0,0,0,0,1,2,1,0,0,0,0,0],
                                 "savanna":[0,0,0,0,0,0,0,0,1,2,4,6,2,0,0],
                      "tropical grassland":[0,0,0,0,0,0,0,0,0,0,1,2,4,5,8],
                                  "jungle":[0,0,0,0,0,0,0,0,0,0,1,2,2,8,15],
                                  "desert":[0,0,0,0,0,0,1,3,10,5,0,0,0,0,0],  
                               "grassland":[0,1,3,8,8,5,3,2,0,0,0,0,0,0,0],
                                   "taiga":[0,5,7,3,0,0,0,0,0,0,0,0,0,0,0],
                                  "tundra":[2,8,4,0,0,0,0,0,0,0,0,0,0,0,0],
                                    "snow":[8,4,1,0,0,0,0,0,0,0,0,0,0,0,0],
                        "deciduous forest":[0,0,1,7,6,4,2,0,0,0,0,0,0,0,0],
                       "coniferous forest":[0,2,7,5,2,1,0,0,0,0,0,0,0,0,0],
                                   "swamp":[0,2,4,2,1,0,0,0,0,0,0,0,0,0,0],
                                   "mountain":[0,2,4,3,4,1,1,0,0,0,0,1,1,2,2],
                    } #From northpole to equator - distribution function for each terrain type

GRASS_LEVEL=7
WATER_LEVEL=3

water_latitude_probability_dict={
                            "grassland":[GRASS_LEVEL]*15,
                                   "water":[WATER_LEVEL]*15}

terrain_types=list(terrain_color_dict.keys())

def calculate_latitude(row,total_rows,latitude_levels):
    latitude=row/total_rows*latitude_levels*2
    return(latitude)
     
def generate_latitude_index(latitude,latitude_levels):
    index=int(latitude_levels-abs(latitude-latitude_levels))
    
    if index==latitude_levels:
        index-=1 #0-20 -> 10 is in the middle
    return(index)
        
def generate_latitude_terrains(latitude_index,terrain_latitude_probability_dict):
    
    nested_list_of_terrains=[[k]*v[latitude_index] for k,v in terrain_latitude_probability_dict.items()]
    list_of_terrains=[item for sublist in nested_list_of_terrains for item in sublist]
    return(list_of_terrains)
    
latitude_levels=15  
    
def expand_terrain_type(row,col,excluded_terrain_types):
    global terrain_values
    direction_index=random.randint(0,3)
    choices=[[0,1],[0,-1],[1,0],[-1,0]]
    direction=choices[direction_index]
    print(direction,[row,col])
    terrain_type=terrain_values[row][col]
    
    if terrain_type not in excluded_terrain_types:
        new_coor=[x + y for x, y in zip([row,col], direction)]
        index=grid.find_cell_index(new_coor[0], new_coor[1])
        terrain_values[new_coor[0]][new_coor[1]]=terrain_type
        grid.table_cells[index].color=terrain_color_dict[terrain_type]
        
def smooth_terrain_type(row,col,excluded_terrain_types):
    global terrain_values
    choices=[[0,1],[0,-1],[1,0],[-1,0]]
    terrain_type=terrain_values[row][col]
        
    if terrain_type not in excluded_terrain_types:
        for i,direction in enumerate(choices):
        
            new_coor=[x + y for x, y in zip([row,col], direction)]
            index=grid.find_cell_index(new_coor[0], new_coor[1])
            terrain_values[new_coor[0]][new_coor[1]]=terrain_type
            grid.table_cells[index].color=terrain_color_dict[terrain_type]

def delete_lonely_terrain_type(row,col,excluded_terrain_types):
    global terrain_values
    choices=[[0,1],[0,-1],[1,0],[-1,0]]
    terrain_type=terrain_values[row][col]
        
    surrounding_terrain_types=[]
    if terrain_type not in excluded_terrain_types:
        for i,direction in enumerate(choices):
        
            new_coor=[x + y for x, y in zip([row,col], direction)]
            index=grid.find_cell_index(new_coor[0], new_coor[1])
            surrounding_terrain_type=terrain_values[new_coor[0]][new_coor[1]]
            surrounding_terrain_types.append(surrounding_terrain_type)

        terrain_counts=dict(Counter(surrounding_terrain_types))
        if terrain_type not in surrounding_terrain_types:
            new_terrain_type=[]
        
        maximal_terrain=next(iter(sorted(terrain_counts.items(), key=lambda kv: kv[1],reverse=True)))
        terrain_type=maximal_terrain[0]
        
        terrain_values[new_coor[0]][new_coor[1]]=terrain_type
        grid.table_cells[index].color=terrain_color_dict[terrain_type]

def init_terrain_values(init_terrain_type):
    terrain_values=[]
    for i in range(grid.rows):
        sublist=[]
        for j in range(grid.cols):
            sublist.append(init_terrain_type)
        terrain_values.append(sublist)
        
    return(terrain_values)

terrain_values=init_terrain_values("grassland")

def generate_terrain(new_terrains,overrided_terrains,terrain_latitude_probability_dict):
    global terrain_values
    for i in range(grid.rows):  
        for j in range(grid.cols):  
            
            
            if terrain_values[i][j] in overrided_terrains: #will override only some terrains
                
                latitude=calculate_latitude(i,grid.rows,latitude_levels)
                latitude_index=generate_latitude_index(latitude,latitude_levels)
                list_of_terrains=generate_latitude_terrains(latitude_index,terrain_latitude_probability_dict)
                list_of_possible_terrains=[x for x in list_of_terrains if x in new_terrains]
                
                #RANDOM CHOICE
                #terrain_index=random.randint(0,len(terrain_types)-1)
                #terrain_type=terrain_types[terrain_index]
                
                terrain_type=random.choice(list_of_possible_terrains)
                
                index=grid.find_cell_index(i, j)
                terrain_values[i][j]=terrain_type
                grid.table_cells[index].color=terrain_color_dict[terrain_type]
        
new_terrains=['grassland', 'water']      
overrided_terrains=["grassland"]
generate_terrain(new_terrains,overrided_terrains,water_latitude_probability_dict)


for i in range(5000):
    a=random.randint(1,grid.rows-2)
    b=random.randint(1,grid.cols-2)
    smooth_terrain_type(a,b,[])

for i in range(1,grid.rows-1):
    for j in range(1,grid.cols-1):
        delete_lonely_terrain_type(i,j,[])

new_terrains=['flood_plains', 'oasis', 'savanna', 'tropical grassland', 'jungle', 'desert', 'grassland', 'taiga', 'tundra', 'snow', 'deciduous forest', 'coniferous forest', 'swamp', 'mountain']    
overrided_terrains=["grassland"]
generate_terrain(new_terrains,overrided_terrains,terrain_latitude_probability_dict)

for i in range(500):
    a=random.randint(1,grid.rows-2)
    b=random.randint(1,grid.cols-2)
    expand_terrain_type(a,b,["swamp","oasis"])
    
    a=random.randint(1,grid.rows-2)
    b=random.randint(1,grid.cols-2)
    smooth_terrain_type(a,b,["swamp","oasis","mountain"])
    
