import pygame
import button
import csv
import pickle
from pygame.locals import *

pygame.init()

clock = pygame.time.Clock()
fps = 60
#game window
width = 900
height = 560

lower_margin = 100
side_margin = 550

screen = pygame.display.set_mode((width + side_margin,height + lower_margin))

#define game var
scroll_left = False
scroll_right = False
scroll = 0
scroll_speed = 1
level = 0
ROWS = 16
MAX_COLS = 150
TILE_SIZE = height // ROWS
TILE_TYPES = 21

current_tile = 0
#load image
pine1_img = pygame.image.load('img/Background/pine1.png').convert_alpha() 
pine2_img = pygame.image.load('img/Background/pine2.png').convert_alpha() 
mountain_img = pygame.image.load('img/Background/mountain.png').convert_alpha() 
sky_img = pygame.image.load('img/Background/sky_cloud.png').convert_alpha() 

#store tile in list
img_list = []
for x in range(TILE_TYPES):
	img = pygame.image.load(f'img/tile/{x}.png').convert_alpha()
	img = pygame.transform.scale(img,(TILE_SIZE,TILE_SIZE))
	img_list.append(img)

save_img = pygame.image.load('img/save_btn.jpg').convert_alpha()
load_img = pygame.image.load('img/load_btn.png').convert_alpha()
save_img = pygame.transform.scale(save_img,(100,25))
load_img = pygame.transform.scale(load_img,(100,25))

exit_img = pygame.image.load('img/exit_btn.png').convert_alpha()
exit_img = pygame.transform.scale(exit_img,(100,45))


arrow_img = pygame.image.load('img/arrow.png').convert_alpha()
arrow_img = pygame.transform.scale(arrow_img,(50,50))

larrow_img = pygame.transform.rotate(arrow_img,90)
rarrow_img = pygame.transform.rotate(arrow_img,-90)
uparrow_img = pygame.transform.rotate(arrow_img,0)
downarrow_img = pygame.transform.rotate(arrow_img,180)

GREEN = (144,201,120)
WHITE = (255,255,255)
RED = (200,25,25)

font = pygame.font.SysFont('FUTURA',30)

#create empty tile list
world_data = []
for row in range(ROWS):
	r = [-1] * MAX_COLS
	world_data.append(r)
#create ground
for tile in range(0,MAX_COLS):
	world_data[ROWS - 1][tile] = 0


def draw_text(text,font,text_col,x,y):
	
	img = font.render(text,True,text_col)
	screen.blit(img,(x,y))
	
def draw_bg():
	screen.fill((GREEN))
	widthA = sky_img.get_width()
	for x in range(4):
		screen.blit(sky_img,((x * widthA) - scroll * 0.5,0))
		screen.blit(mountain_img,((x * widthA) - scroll * 0.6,height - mountain_img.get_height() - 300))
		screen.blit(pine1_img,((x * widthA) - scroll * 0.7,height - pine1_img.get_height() - 150))
		screen.blit(pine2_img,((x * widthA) - scroll * 0.8,height - pine2_img.get_height()))
		
def draw_grid():
	#verticle line
	for c in range(MAX_COLS + 1):
		pygame.draw.line(screen,WHITE,(c * TILE_SIZE - scroll, 0),(c * TILE_SIZE - scroll,height))
	#horizontle line
	for c in range(ROWS + 1):
		pygame.draw.line(screen,WHITE,(0,c * TILE_SIZE),(width,c * TILE_SIZE))

def draw_world():
	for y, row in enumerate(world_data):
		for x, tile in enumerate(row):
			if tile >= 0:
				screen.blit(img_list[tile],(x * TILE_SIZE - scroll, y * TILE_SIZE))
				
save_button = button.Button(width // 2, height + lower_margin - 80, save_img,1)
load_button = button.Button(width // 2 + 150, height + lower_margin - 80, load_img,1)
exit_button = button.Button(width // 2 + 300, height + lower_margin - 80, exit_img,1)


larrow_button = button.Button(width // 2 + 500, height + lower_margin - 80, larrow_img,1)
rarrow_button = button.Button(width // 2 + 600, height + lower_margin - 80, rarrow_img,1)

uparrow_button = button.Button(width // 2 - 100, height + lower_margin - 100, uparrow_img,1)
downarrow_button = button.Button(width // 2 - 100, height + lower_margin - 40, downarrow_img,1)

#create button
#buttonlist
button_list = []
button_col = 0
button_row = 0
for i in range(len(img_list)):
	tile_button = button.Button(width + (75 * button_col) + 50,75 * button_row + 50, img_list[i],1)
	button_list.append(tile_button)
	button_col += 1
	if button_col > 3:
		button_row += 1
		button_col = 0

run = True
while run:
	draw_bg()
	draw_grid()
	draw_world()
	draw_text(f'LEVEL : {level}',font,WHITE,10,height+ lower_margin - 90)
	draw_text('presse up down to change level',font,WHITE,10,height+ lower_margin - 60)
	
	clock.tick(fps)
	if uparrow_button.draw(screen):
		level += 1
	if downarrow_button.draw(screen):
		level -= 1
	
	if exit_button.draw(screen):
		run = False
	if larrow_button.draw(screen) == True and scroll > 0:
		scroll -= 300 * scroll_speed
		
	if rarrow_button.draw(screen) == True and scroll < (MAX_COLS * TILE_SIZE) - width:
		scroll += 300 * scroll_speed
		
	if save_button.draw(screen):
		with open(f'level_data{level}.csv','w', newline='') as csvfile:
			writer = csv.writer(csvfile, delimiter = ',')
			for row in world_data:
				writer.writerow(row)
		
	if load_button.draw(screen):
		scroll = 0
		with open(f'level_data{level}.csv',newline='') as csvfile:
			reader = csv.reader(csvfile, delimiter = ',')
			for x, row in enumerate(reader):
				for y, tile in enumerate(row):
					world_data[x][y] = int(tile)
		
	
	#draw side bar
	pygame.draw.rect(screen,GREEN,(width,0,side_margin,height))
	
	button_count = 0
	for button_count, i in enumerate(button_list):
		if i.draw(screen):
			current_tile = button_count
	#highlight selected
	pygame.draw.rect(screen,RED,button_list[current_tile].rect,3)
	if scroll_left == True and scroll > 0:
		scroll -= 30 * scroll_speed
		
	if scroll_right == True and scroll < (MAX_COLS * TILE_SIZE) - width:
		scroll += 30 * scroll_speed
		
	#add new tiles in screen
	pos = pygame.mouse.get_pos()
	x = (pos[0] + scroll) // TILE_SIZE
	y = pos[1] // TILE_SIZE
	#CHECK CORDINATI IN SCREEN\
	
	if pos[0] < width and pos[1] < height:
		if pygame.mouse.get_pressed()[0] == 1:
			if world_data[y][x] != current_tile:
				world_data[y][x] = current_tile
		if pygame.mouse.get_pressed()[2] == 1:
			world_data[y][x] = -1
	
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			run = False
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_ESCAPE:
				run = False
			if event.key == pygame.K_UP:
			    level += 1
			if event.key == pygame.K_DOWN:
			    level -= 1
			
			if event.key == pygame.K_RIGHT:
				scroll_right = True
			if event.key == pygame.K_LEFT:
				scroll_left = True
			if event.key == pygame.K_RSHIFT:
				scroll_speed = 5
			
				
		if event.type == pygame.KEYUP:
			if event.key == pygame.K_RIGHT:
				scroll_right = False
			if event.key == pygame.K_LEFT:
				scroll_left = False
			if event.key == pygame.K_RSHIFT:
				scroll_speed = 1
			
		
			
	pygame.display.update()
	
pygame.quit()
