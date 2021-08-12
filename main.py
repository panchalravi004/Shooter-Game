import pygame
from pygame import mixer
import os
import random
import csv
import button

mixer.init()
pygame.init()


width = 1400
height = 740

screen = pygame.display.set_mode((width, height))
pygame.display.set_caption('Shooter')

#set framerate
clock = pygame.time.Clock()
FPS = 60


#TILE_SIZE = 40
#game variable
gravity = 0.75
scroll_thresh = 300
ROWS = 16
COLS = 150
level = 1
start_game = False
MAX_LEVEL = 3

screen_scroll = 0
bg_scroll = 0

TILE_SIZE = height // ROWS
TILE_TYPES = 21

#define player action variables
moving_left = False
moving_right = False
shoot = False
grenade = False
grenade_thrown = False
start_intro = False
#load music
pygame.mixer.music.load('audio/music2.mp3')
pygame.mixer.music.set_volume(0.2)
pygame.mixer.music.play(-1,0.0, 5000)

jump_fx = pygame.mixer.Sound('audio/jump.wav')
jump_fx.set_volume(0.5)
shot_fx = pygame.mixer.Sound('audio/shot.wav')
shot_fx.set_volume(0.5)
grenade_fx = pygame.mixer.Sound('audio/grenade.wav')
grenade_fx.set_volume(0.5)

#store tile in list
img_list = []
for x in range(TILE_TYPES):
	img = pygame.image.load(f'img/tile/{x}.png').convert_alpha()
	img = pygame.transform.scale(img,(TILE_SIZE,TILE_SIZE))
	img_list.append(img)

#load image
bullet_img = pygame.image.load('img/icons/bullet.png').convert_alpha()
grenade_img = pygame.image.load('img/icons/grenade.png').convert_alpha()

#pick up boxes
heal_box_img = pygame.image.load('img/icons/health_box.png').convert_alpha()
ammo_box_img = pygame.image.load('img/icons/ammo_box.png').convert_alpha()
grenade_box_img = pygame.image.load('img/icons/grenade_box.png').convert_alpha()

item_boxes = {
	'Health' : heal_box_img,
	'Ammo' : ammo_box_img,
	'Grenade' : grenade_box_img
	
}

#define colours
BG = (144, 201, 120)
red = (255,0,0)
green = (0,255,0)
WHITE = (255,255,255)
black = (0,0,0)
PINK = (235,65,64)
#define font
font = pygame.font.SysFont('Futura', 30)

#bg
#load image
pine1_img = pygame.image.load('img/Background/pine1.png').convert_alpha() 
pine2_img = pygame.image.load('img/Background/pine2.png').convert_alpha() 
mountain_img = pygame.image.load('img/Background/mountain.png').convert_alpha() 
sky_img = pygame.image.load('img/Background/sky_cloud.png').convert_alpha() 

#load button img
start_img = pygame.image.load('img/start_btn.png').convert_alpha()
exit_img = pygame.image.load('img/exit_btn.png').convert_alpha()
restart_img = pygame.image.load('img/restart_btn.png').convert_alpha()

def reset_level():
	enemy_group.empty()
	bullet_group.empty()
	grenade_group.empty()
	explosion_group.empty()
	item_box_group.empty()
	decoration_group.empty()
	water_group.empty()
	exit_group.empty()
	
	#create empty tilw listreset all
	data = []
	for row in range(ROWS):
		r = [-1] * COLS
		data.append(r)
		
	return data
	
	

def draw_text(text, font, text_col, x, y):
	img = font.render(text,True,text_col)
	screen.blit(img, (x,y))

def draw_bg():
	screen.fill(BG)
	widtha = sky_img.get_width()
	#screen.fill((GREEN))
	for x in range(5):
		screen.blit(sky_img,((x * widtha) - bg_scroll * 0.5,0))
		screen.blit(mountain_img,((x * widtha) - bg_scroll * 0.6,height - mountain_img.get_height() - 300))
		screen.blit(pine1_img,((x * widtha) - bg_scroll * 0.7,height - pine1_img.get_height() - 150))
		screen.blit(pine2_img,((x * widtha) - bg_scroll * 0.8,height - pine2_img.get_height()))
		#pygame.draw.line(screen,red,(0,300),(width,300))
		
class Soldier(pygame.sprite.Sprite):
	def __init__(self, char_type, x, y, scale, speed, ammo, grenades):
		pygame.sprite.Sprite.__init__(self)
		self.alive = True
		self.shoot_cooldown = 0
		self.grenades = grenades
		self.ammo = ammo
		self.start_ammo = ammo
		self.health = 100
		self.max_health = self.health
		self.speed = speed # its for speed of player
		self.direction = 1 #its just for chehck left right movement
		self.flip = False #for flip when left right move
		#for jump player
		self.jump = False
		self.vel_y = 0
		self.in_air = True
		#below is for anime and char
		self.char_type = char_type
		self.action = 0
		self.anime_list = []
		self.index = 0
		self.update_time = pygame.time.get_ticks()
		#creat ai var
		self.move_counter = 0
		self.vision = pygame.Rect(0,0,150,20)
		self.idling = False
		self.idling_counter = False
		
		animation_type = ['Idle','Run','Jump','Death']
		for animation in animation_type:
			temp_list = []
			#count how many file in folder
			num_of_frame = len(os.listdir(f'img/{self.char_type}/{animation}'))
			for i in range(num_of_frame):
				img = pygame.image.load(f'img/{self.char_type}/{animation}/{i}.png').convert_alpha()
				img = pygame.transform.scale(img, (int(img.get_width() * scale), int(img.get_height() * scale)))
				temp_list.append(img)
			self.anime_list.append(temp_list)
			
		self.image = self.anime_list[self.action][self.index]
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)
		self.width = self.image.get_width()
		self.height = self.image.get_height()
		
		
	def update(self):
		self.update_anime()
		self.check_alive()
		
		if self.shoot_cooldown > 0:
			self.shoot_cooldown -= 1
			
	def move(self, moving_left, moving_right):
		screen_scroll = 0
		
		#reset movement variables
		dx = 0
		dy = 0

		#assign movement variables if moving left or right
		if moving_left:
			dx = -self.speed
			self.flip = True
			self.direction = -1
			self.action = 1
		if moving_right:
			dx = self.speed
			self.flip = False
			self.direction = 1
			self.action = 1
			
		if self.jump == True and self.in_air == False:
			self.vel_y -= 13
			self.jump = False
			self.in_air = True
			
		#add gravity
		self.vel_y += gravity
		if self.vel_y > 30:
			self.vel_y = 30
		dy += self.vel_y
		
		#check for collision
		for tile in world.obstacle_list:
			#check collision in x direction
			if tile[1].colliderect(self.rect.x + dx, self.rect.y, self.width,self.height):
				dx = 0
				#if ai ia hit the walll 
				if self.char_type == 'enemy':
					self.direction *= -1
					self.move_counter = 0
			#check for y direction
			if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width,self.height):
				#check if below the ground
				if self.vel_y < 0:
					self.vel_y = 0
					dy = tile[1].bottom - self.rect.top
				#check if above the ground
				elif self.vel_y >=0:
					self.vel_y = 0
					self.in_air = False
					dy = tile[1].top - self.rect.bottom
					
		#check collision with water
		if pygame.sprite.spritecollide(self,water_group,False):
			self.health = 0
		
		#exit collisio
		level_complete = False
		if pygame.sprite.spritecollide(self,exit_group,False):
			level_complete = True
			
		
		#fall down
		if self.rect.bottom > height:
			self.health = 0
		
		#check if going edge of screen
		if self.char_type == 'player':
			if self.rect.left + dx < 0 or self.rect.right + dx > width:
					dx = 0
					
		'''	
		if self.rect.bottom + dy > 300:
			dy = 300 - self.rect.bottom
			self.in_air = False
		'''
		#update rectangle position
		self.rect.x += dx
		self.rect.y += dy
		
		#update scroll based on player position
		if self.char_type == 'player':
			if (self.rect.right > 1000 - scroll_thresh and bg_scroll < (world.level_length * TILE_SIZE) - 1300)  or (self.rect.left < scroll_thresh and bg_scroll  > abs(dx)):
				self.rect.x -= dx
				screen_scroll = -dx
				
		return screen_scroll,level_complete
		
	def shoot(self):
		if self.shoot_cooldown == 0 and self.ammo > 0:
			self.shoot_cooldown = 5
			bullet = Bullet(self.rect.centerx + (0.75 * self.rect.size[0] * self.direction),self.rect.centery,self.direction)
			bullet_group.add(bullet)
			self.ammo -= 1
			shot_fx.play()
		
	def ai(self):
		if self.alive and player.alive:
			if self.idling == False and random.randint(1,200) == 1:
				self.idling = True
				self.idling_counter = 100
				self.update_action(0)
			#check if ai in near thhe player
			if self.vision.colliderect(player.rect):
				self.update_action(0)
				self.shoot()
			else:
				if self.idling == False:
					if self.direction == 1:
						ai_moving_right  = True
					else:
						ai_moving_right = False
					ai_moving_left = not ai_moving_right
					self.move(ai_moving_left,ai_moving_right)
					self.update_action(1)
					self.move_counter += 1
					#update ai vision
					self.vision.center = (self.rect.centerx + 75 * self.direction,self.rect.centery)
					#pygame.draw.rect(screen,red,self.vision)
					
					if self.move_counter > TILE_SIZE:
						self.direction *= -1
						self.move_counter *= -1
				else:
					self.idling_counter -= 1
					if self.idling_counter <= 0:
						self.idling = False
		self.rect.x   += screen_scroll
						
	
	def update_anime(self):
		
		anime_cooldown = 100
		#update image
		self.image = self.anime_list[self.action][self.index]
		#check if enough time is pass
		if pygame.time.get_ticks() - self.update_time > anime_cooldown:
			self.update_time = pygame.time.get_ticks()
			self.index += 1
		'''
		if self.index > 4:
			self.index = 0
			#below and this are some
		'''
		if self.index >= len(self.anime_list[self.action]):
			if self.action == 3:
				self.index = len(self.anime_list[self.action]) - 1
			else:
				self.index = 0
			
	def update_action(self,new_action):
		#check action different withh previous one
		if new_action != self.action:
			self.action = new_action
			#update anime settings
			self.index = 0
			self.update_time = pygame.time.get_ticks()
	
	def check_alive(self):
		if self.health <= 0:
			self.health = 0
			self.speed = 0
			self.alive = False
			self.update_action(3)
		
	def draw(self):
		screen.blit(pygame.transform.flip(self.image, self.flip, False), self.rect)
		#pygame.draw.rect(screen, red, self.rect, 1)

class World():
	def __init__(self):
		self.obstacle_list = []
		
	def process_data(self,data):
		self.level_length = len(data[0])
			
		#iterate each value in level
		for y, row in enumerate(data):
			
			for x, tile in enumerate(row):
				if tile >= 0:
					img = img_list[tile]
					img_rect = img.get_rect()
					img_rect.x = x * TILE_SIZE
					img_rect.y = y * TILE_SIZE
					tile_data = (img,img_rect)
					if tile >= 0 and tile <= 8:
						self.obstacle_list.append(tile_data)
					elif tile >= 9 and tile <= 10:
						water = Water(img,x * TILE_SIZE, y * TILE_SIZE)
						water_group.add(water)
						
					elif tile >= 11 and tile <= 14:
						decoration = Decoration(img,x * TILE_SIZE, y * TILE_SIZE)
						decoration_group.add(decoration)
						
					elif tile == 15:
						player = Soldier('player',x * TILE_SIZE,y * TILE_SIZE, 1.65, 10, 20,5)
						health_bar = HealthBar(10,10, player.health,player.health)
					elif tile == 16:
						enemy = Soldier('enemy',x * TILE_SIZE, y * TILE_SIZE, 1.65, 2, 20,0)
						enemy_group.add(enemy)
					elif tile == 17:
						item_box = ItemBox('Ammo',x * TILE_SIZE, y * TILE_SIZE)
						item_box_group.add(item_box)
						
					elif tile == 18:
						item_box = ItemBox('Grenade',x * TILE_SIZE, y * TILE_SIZE)
						item_box_group.add(item_box)
						
					elif tile == 19:
						#temp for create  item box
						item_box = ItemBox('Health',x * TILE_SIZE, y * TILE_SIZE)
						item_box_group.add(item_box)
						
					elif tile == 20:
						exit = Exit(img,x * TILE_SIZE, y * TILE_SIZE)
						exit_group.add(exit)
						
						
		return player, health_bar
		
	def draw(self):
		for tile in self.obstacle_list:
			tile[1][0] += screen_scroll
			screen.blit(tile[0],tile[1])


class Decoration(pygame.sprite.Sprite):
	def __init__(self,img,x,y):
		pygame.sprite.Sprite.__init__(self)
		self.image = img
		self.rect = self.image.get_rect()
		self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))
	def update(self):
		self.rect.x += screen_scroll
	
class Water(pygame.sprite.Sprite):
	def __init__(self,img,x,y):
		pygame.sprite.Sprite.__init__(self)
		self.image = img
		self.rect = self.image.get_rect()
		self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))
	def update(self):
		self.rect.x += screen_scroll
		
class Exit(pygame.sprite.Sprite):
	def __init__(self,img,x,y):
		pygame.sprite.Sprite.__init__(self)
		self.image = img
		self.rect = self.image.get_rect()
		self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))
	def update(self):
		self.rect.x += screen_scroll
	

class ItemBox(pygame.sprite.Sprite):
	def __init__(self,item_type,x,y):
		pygame.sprite.Sprite.__init__(self)
		self.item_type = item_type
		self.image = item_boxes[self.item_type]
		self.rect = self.image.get_rect()
		self.rect.midtop = (x + TILE_SIZE // 2, y + (TILE_SIZE - self.image.get_height()))
	
	def update(self):
		self.rect.x += screen_scroll
		if pygame.sprite.collide_rect(self,player):
			#check what kind of box it was
			if self.item_type == 'Health':
				player.health += 25
				
				if player.health > player.max_health:
					player.health = player.max_health
					
			elif self.item_type == 'Ammo':
				player.ammo += 15
			elif self.item_type == 'Grenade':
				player.grenades += 3
				
			self.kill()
			
class HealthBar():
	def __init__(self,x,y,health, max_health):
		self.x = x
		self.y = y
		self.health = health
		self.max_health = max_health
	def draw(self,health):
		self.health = health
		
		#calculate health ratio
		ratio = self.health / self.max_health
		pygame.draw.rect(screen, black, (self.x, self.y,154,24))
		
		pygame.draw.rect(screen, red, (self.x,self.y,150,20))
		pygame.draw.rect(screen, green, (self.x,self.y,150 * ratio,20))
		
		
class Bullet(pygame.sprite.Sprite):
	def __init__(self,x,y,direction):
		pygame.sprite.Sprite.__init__(self)
		self.speed = 40
		self.image = bullet_img
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)
		self.direction = direction
		
	def update(self):
		#move bullet\
		self.rect.x += (self.direction * self.speed) + screen_scroll
		#check bullet of the screen
		if self.rect.right < 0 or self.rect.left > width - 100:
			self.kill
		#check collision with level
		for tile in world.obstacle_list:
			if tile[1].colliderect(self.rect):
				self.kill()
		#check collide anemy
		if pygame.sprite.spritecollide(player, bullet_group, False):
			if player.alive:
				player.health -= 5
				self.kill()
		for enemy in enemy_group:
			if pygame.sprite.spritecollide(enemy, bullet_group, False):
				if player.alive:
					enemy.health -= 25
					self.kill()
			
class Grenade(pygame.sprite.Sprite):
	def __init__(self,x,y,direction):
		pygame.sprite.Sprite.__init__(self)
		self.timer = 40
		self.vel_y = -12
		self.speed = 10
		self.image = grenade_img
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)
		self.width = self.image.get_width()
		self.height = self.image.get_height()
		
		self.direction = direction
		
	def update(self):
		self.vel_y += gravity
		dx = self.direction * self.speed
		dy = self.vel_y
		#check colision with level
		for tile in world.obstacle_list:
			#check grenade of the screen
			if tile[1].colliderect(self.rect.x + dx, self.rect.y,self.width,self.height):
				self.direction *= -1
				dx = self.direction * self.speed
			
			#check for y direction
			if tile[1].colliderect(self.rect.x, self.rect.y + dy, self.width,self.height):
				self.speed = 0
				#check if below the ground
				if self.vel_y < 0:
					self.vel_y = 0
					dy = tile[1].bottom - self.rect.top
				#check if above the ground
				elif self.vel_y >=0:
					self.vel_y = 0
					dy = tile[1].top - self.rect.bottom
			
		
		self.rect.x += dx + screen_scroll
		self.rect.y += dy
		
		#countdown timer
		self.timer -= 1
		if self.timer <= 0:
			self.kill()
			grenade_fx.play()
			explosion = Explosion(self.rect.x,self.rect.y, 0.5)
			explosion_group.add(explosion)
			#do damege on enemy 
			if abs(self.rect.centerx - player.rect.centerx) < TILE_SIZE * 2 and \
				abs(self.rect.centery - player.rect.centery) < TILE_SIZE * 2:
				player.health -= 50
			for enemy in enemy_group:
				if abs(self.rect.centerx - enemy.rect.centerx) < TILE_SIZE * 2 and \
					abs(self.rect.centery - enemy.rect.centery) < TILE_SIZE * 2:
					enemy.health -= 50
				
		
class Explosion(pygame.sprite.Sprite):
	def __init__(self,x,y,scale):
		pygame.sprite.Sprite.__init__(self)
		self.images = []
		for num in range(1, 6):
			img = pygame.image.load(f'img/explosion/exp{num}.png').convert_alpha()
			img = pygame.transform.scale(img,(int(img.get_width() * scale),int(img.get_height() * scale)))
			self.images.append(img)
		self.index = 0
		self.image = self.images[self.index]
		self.rect = self.image.get_rect()
		self.rect.center = (x, y)
		self.counter = 0
	def update(self):
		self.rect.x += screen_scroll
		EXPLOSION_SPEED = 4
		#update anime of explosion
		self.counter += 1
		if self.counter >= EXPLOSION_SPEED:
			self.counter = 0
			self.index += 1
			#if amime is completee then return
			if self.index >= len(self.images):
				self.kill()
			else:
				self.image = self.images[self.index]

class ScreenFade():
	def __init__(self,direction,colour,speed):
		self.direction = direction
		self.colour = colour
		self.speed = speed
		self.fade_counter = 0
	def fade(self):
		fade_complete = False
		self.fade_counter += self.speed
		if self.direction == 1:
			pygame.draw.rect(screen,self.colour,(0 - self.fade_counter,0,width // 2,height))
			pygame.draw.rect(screen,self.colour,(width // 2 + self.fade_counter,0,width,height))
			pygame.draw.rect(screen,self.colour,(0,0 - self.fade_counter,width,height // 2))
			pygame.draw.rect(screen,self.colour,(0,height // 2 + self.fade_counter ,width,height))
			
			
		
		if self.direction == 2:
			pygame.draw.rect(screen,self.colour,(0,0,width,0 + self.fade_counter))
		if self.fade_counter >= height:
			fade_complete = True
		return fade_complete
		
#create speed fades
intro_fade = ScreenFade(1,black,35)
death_fade = ScreenFade(2,PINK,20)

#create button
start_button = button.Button((width // 2) - (start_img.get_width() // 2),height // 2 -150,start_img,1)
exit_button = button.Button((width // 2) - (exit_img.get_width() // 2),height // 2 + 50,exit_img,1)
restart_button = button.Button((width // 2) - (restart_img.get_width()),height // 2 - 100,restart_img,2)



#create sprite group
enemy_group = pygame.sprite.Group()
bullet_group = pygame.sprite.Group()
grenade_group = pygame.sprite.Group()
explosion_group = pygame.sprite.Group()
item_box_group = pygame.sprite.Group()
decoration_group = pygame.sprite.Group()
water_group = pygame.sprite.Group()
exit_group = pygame.sprite.Group()


#player = Soldier('player', 200, 200, 1.65, 5, 20,5)
#health_bar = HealthBar(10,10, player.health,player.health)

#enemy = Soldier('enemy', 400, 250, 1.65, 2, 20,0)
#enemy_group.add(enemy)

#create empty tile list 
world_data = []
for row in range(ROWS):
	r = [-1] * COLS
	world_data.append(r)

#load in level data 
with open (f'level_data{level}.csv',newline='') as csvfile:
	reader = csv.reader(csvfile, delimiter=',')
	for x, row in enumerate(reader):
		for y, tile in enumerate(row):
			world_data[x][y] = int(tile)
			
world = World()
player,health_bar = world.process_data(world_data)

run = True
while run:

	clock.tick(FPS)
	if start_game == False:
		#draw menu
		screen.fill(BG)
		if start_button.draw(screen):
			start_game = True
			start_intro = True
		if exit_button.draw(screen):
			run = False
		
	else:
		
		#draw background
		draw_bg()
		#draw map
		world.draw()
		#show player health
		health_bar.draw(player.health)
		
		#show ammo and grenade
		draw_text('AMMO:', font, WHITE,10, 35)
		for x in range(player.ammo):
			screen.blit(bullet_img,(90 + (x * 10),40))
		
		draw_text('GRENADE:', font, WHITE,10, 55)
		for x in range(player.grenades):
			screen.blit(grenade_img,(135 + (x * 15),60))
		
		#update anime for player
		player.update()
		player.draw()
		
		#draw all player and enemy
		for enemy in enemy_group:
			enemy.ai()
			enemy.update()
			enemy.draw()
			
		#update and draw group
		bullet_group.update()
		grenade_group.update()
		explosion_group.update()
		item_box_group.update()
		decoration_group.update()
		water_group.update()
		exit_group.update()
		
		#draw
		bullet_group.draw(screen)
		grenade_group.draw(screen)
		explosion_group.draw(screen)
		item_box_group.draw(screen)
		decoration_group.draw(screen)
		water_group.draw(screen)
		exit_group.draw(screen)
		
		#show intro
		if start_intro == True:
			if intro_fade.fade():
				start_intro = False
				intro_fade.fade_counter = 0
		
		if player.alive:
			#shoot bullet
			if shoot:
				player.shoot()
			elif grenade and grenade_thrown == False and player.grenades > 0:
				grenade = Grenade(player.rect.centerx + (0.5 * player.rect.size[0] * player.direction),player.rect.top,player.direction)
				grenade_group.add(grenade)
				player.grenades -= 1
				grenade_thrown = True
				
			if player.in_air:
				player.update_action(2)
			#update player action
			elif moving_left or moving_right:
				player.update_action(1)# 1 is for run
			else:
				player.update_action(0)
			#move player
			screen_scroll,level_complete = player.move(moving_left, moving_right)
			bg_scroll -= screen_scroll
			#check if level complete
			if level_complete:
				start_intro = True
				level += 1
				bg_scroll = 0
				world_data = reset_level()
				if level <= MAX_LEVEL:
					#load in level data 
					with open (f'level_data{level}.csv',newline='') as csvfile:
						reader = csv.reader(csvfile, delimiter=',')
						for x, row in enumerate(reader):
							for y, tile in enumerate(row):
								world_data[x][y] = int(tile)
								
					world = World()
					player,health_bar = world.process_data(world_data)
					
				
		else:
			screen_scroll = 0
			if death_fade.fade():
				if restart_button.draw(screen):
					death_fade.fade_counter = 0
					start_intro = True
					bg_scroll = 0
					world_data = reset_level()
					#load in level data 
					with open (f'level_data{level}.csv',newline='') as csvfile:
						reader = csv.reader(csvfile, delimiter=',')
						for x, row in enumerate(reader):
							for y, tile in enumerate(row):
								world_data[x][y] = int(tile)
								
					world = World()
					player,health_bar = world.process_data(world_data)
				
				
				
		
	for event in pygame.event.get():
		#quit game
		if event.type == pygame.QUIT:
			run = False
		#keyboard presses
		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_LEFT:
				moving_left = True
				
			if event.key == pygame.K_RIGHT:
				moving_right = True
				
			if event.key == pygame.K_SPACE:
				shoot = True
			if event.key == pygame.K_q:
				grenade = True
			
			if event.key == pygame.K_UP and player.alive == True:
				player.jump = True
				jump_fx.play()
			if event.key == pygame.K_ESCAPE:
				run = False


		#keyboard button released
		if event.type == pygame.KEYUP:
			if event.key == pygame.K_LEFT:
				moving_left = False
				
			if event.key == pygame.K_RIGHT:
				moving_right = False
				
			if event.key == pygame.K_SPACE:
				shoot = False
			if event.key == pygame.K_q:
				grenade = False
				grenade_thrown = False
	
	pygame.display.update()

pygame.quit()