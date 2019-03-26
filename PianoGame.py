import pygame
import pygame.midi
import pygame.time
import time
import keyboard
import math
import simpleaudio as sa
import pygame_textinput
import pyautogui as gui

# define all the constant values -----------------------------------------------
n = int(127)
device = 1     # device number in win10 laptop
instrument = 0 # http://www.ccarh.org/courses/253/handout/gminstruments/
note_D3 = 62
note_E3 = 64
note_Fsharp3 = 66   # http://www.electronics.dit.ie/staff/tscarff/Music_technology/midi/midi_note_numbers_for_octaves.htm
note_G3 = 67
note_A3 = 69
note_B3 = 71
note_C4 = 72
note_D4 = 74

happysong = [('D3', 3), ('D3', 1), ('E3', 4), ('D3', 4), ('G3', 4), ('F#3', 8), ('D3', 3), ('D3', 1), ('E3', 4), ('D3', 4), 
	('A3', 4), ('G3', 8), ('D3', 3), ('D3', 1), ('D4', 4), ('B3', 4), ('G3', 4), ('F#3', 4), ('E3', 4), ('C4', 3), ('C4', 1), ('B3', 4), 
	('G3', 4), ('A3', 4), ('G3', 12)]



#48
volume = (n)	
wait_time = 0.5

# initize Pygame MIDI ----------------------------------------------------------
pygame.midi.init()

# set the output device --------------------------------------------------------
player = pygame.midi.Output(device)

# set the instrument -----------------------------------------------------------
player.set_instrument(instrument)
#text input

# play the notes ---------------------------------------------------------------

notes = { 'g':note_D3, 'a':note_E3, 's':note_Fsharp3, 'd':note_G3,
		  'w':note_A3, 'right': note_B3, 'f':note_C4, 'space':note_D4 }
Noteid = ["D3", "E3", "F#3", "G3", "A3", "B3", "C4", "D4"]
Keyids = ['g', 'a', 's', 'd', 'w', 'h', 'f', 'space']

afbet = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 
	'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']

buffer = []
cy1 = 0
betpress = []


def initialize_window(width, height):
	pygame.init()
	pygame.display.set_caption('Happy Birthday!... for now.')
	#screen = pygame.display.set_mode(size)
	screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
	screen.fill((0,0,0))

	return screen

def update_screen():
	screen.fill((0,0,0))

	if gamemode == "playing":
		screen.fill((255,255,255), (0,bottom,width,4))  # draw scoring line

		cy2 = cy1 + bottom

		dx = 80
		margin = (width - dx*8) // 2

		for noteid, note in enumerate(Noteid):
			x = (noteid * dx) + margin
			screen.fill((255,255,255), (x,0,1,bottom))  # draw note line

			bgcolor = (255,255,255)

			if keypressed and Keyids.index(keypressed) == noteid:
				bgcolor = (255,0,0) 

			textsurface = myfont.render(note, False, bgcolor)  # draw Note
			screen.blit(textsurface,(x-textsurface.get_size()[0]//2,bottom+30))

			textsurface = myfont.render(Keyids[noteid], False, bgcolor) # draw key
			screen.blit(textsurface,(x-textsurface.get_size()[0]//2,bottom+50))


		for (y1, y2, note) in displayNotes:
			if y2 < cy1 or y1 > cy2: continue
			noteid = Noteid.index(note)
			x = (noteid * dx) + margin
			y = bottom - (y2-cy1)
			screen.fill((0, 76, 255), (x-10, y, 20, y2-y1))

	textsurface = myfont.render("Score: %d" % score, False, (255,255,255))
	screen.blit(textsurface, (500, 200))

	textsurface = myfont.render("High Score: %d" % highscores[-1][0], False, (255,255,255))
	screen.blit(textsurface, (1250, 200))

	if gamemode in ("ready", "score"):

		textsurface = myfont.render("Highscores", False, (255,255,255))
		screen.blit(textsurface, ((width-textsurface.get_size()[0])//2, height//4-50))

		topten = highscores[-10:]
		topten.reverse()
		for i, (highscore, name) in enumerate(topten):
			textsurface = myfont.render("%s %s" % (name, highscore), False, (255,255,255))
			screen.blit(textsurface, ((width-textsurface.get_size()[0])//2, height//4 + i*30))

	if gamemode == "ready":
		if (int(time.time()*2) % 2) == 0:
			color = (255,255,255)
		else:
			color = (50,50,50)
		textsurface = myfont.render("Please Enter to Start", False, color)
		screen.blit(textsurface, ((width-textsurface.get_size()[0])//2, height//2+50))

		textsurface = myfont.render("Speed Options:", False, (255,255,255))
		screen.blit(textsurface, (1250, 250))

		

		textsurface = myfont.render("Super slow", False, (Slow))
		screen.blit(textsurface, (1250, 300))

		textsurface = myfont.render("Normal", False, (Normal))
		screen.blit(textsurface, (1250, 350))

		textsurface = myfont.render("Impossable", False, (Imp))
		screen.blit(textsurface, (1250, 400))

		textsurface = myfont.render("Press 1, 2, or 3 ", False, (255,255,255))
		screen.blit(textsurface, (1250, 600))

		textsurface = myfont.render("to change difficulty ", False, (255,255,255))
		screen.blit(textsurface, (1250, 650))

		textsurface = myfont.render("level", False, (255,255,255))
		screen.blit(textsurface, (1250, 700))

		


	if gamemode == "score":
		textsurface = myfont.render("Please enter your name: ", False, (255,255,255))
		screen.blit(textsurface, ((width-textsurface.get_size()[0])//2, height//2+50))

		textinput_surf = textinput.get_surface()
		screen.blit(textinput_surf, ((width-textsurface.get_size()[0])//2, height//2 + 100))


	# Blit its surface onto the screen
	pygame.display.flip()

def list_of_keys_pressed():
	return pygame.key.get_pressed()

# DON'T TOUCH THE CODE ABOVE ----------
width = 640
height = 480
screen = initialize_window(width, height)
width, height = pygame.display.get_surface().get_size()

bottom = height - 300
score = 0

highscores = [(1000, "Hayden"), (500, "Jacob"), (200, "Charlotte")]
highscores.sort()

speed = 3

pygame.font.init() 
myfont = pygame.font.SysFont('Arial', 30)

displayNotes = []
y = int(height / 2)
noteHeight = 20

for (note, dur) in happysong:
	displayNotes.append((y, y + dur * noteHeight, note))
	y += (dur * noteHeight)
	y += noteHeight//5

# Everything that changes, lives in your game loop!
# while the game is running, it updates!
clock = pygame.time.Clock()

running = True
keypressed = None
playsong = False

Slow = (101,255,0)
Normal = (250,255,0)
Imp = (255,0,0)

k1 = False
k2 = False
k3 = False

n = 0

gamemode = "ready"

while running:
	if gamemode == "playing":
		if keypressed:
			if not keyboard.is_pressed(keypressed):
				note = notes[key]
				player.note_off(note, volume)
				keypressed = None
		else:
			for key, note in notes.items():
				if keyboard.is_pressed(key):
					buffer.append(key)
					player.note_on(note, volume)
					keypressed = key
					break

		if keypressed:
			for (y1, y2, note) in displayNotes:
				if y2 > cy1 and y1 < cy1:
					noteid = Noteid.index(note)
					if noteid == Keyids.index(keypressed):
						if k1 == True:
							score += 0.25

						elif k2 == True:
							score += 5

						elif k3 == True:
							score += 15

						else:
							score += 5

		buffer = buffer[-6:]
		s = ''.join(buffer)
		
		if s.endswith("gasd"):
			wave_obj = sa.WaveObject.from_wave_file("Ta Da-SoundBible.com-1884170640.wav")
			play_obj = wave_obj.play()
			play_obj.wait_done()
			buffer = []
			if  n == 1000 and score < 1000:
				score += 1000

			elif score > 1000:
				pass

			n = time.time
	events = pygame.event.get()

	for event in events:
		# This will exit game loop

		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_ESCAPE:
				running = False
				break
			if gamemode == "ready":
				if event.key == pygame.K_RETURN:
					score = 0 
					playsong = True
					gamemode = "playing"

				elif event.key == pygame.K_1:
					Slow = (101,255,0)
					Normal = (107,107,107)
					Imp = (107,107,107)
					speed = 1
					k1 = False
					k2 = True
					k3 = False

				elif event.key == pygame.K_2:
					Normal = (250,255,0)
					Slow = (107,107,107)
					Imp = (107,107,107)	
					speed = 2.5
					k1 = False
					k2 = True
					k3 = False

				elif event.key == pygame.K_3:
					Imp = (255,0,0)
					Slow = (107,107,107)
					Normal = (107,107,107)
					speed = 10
					k1 = False
					k2 = False
					k3 = True

				else:
					Normal = (250,255,0)
					Slow = (107,107,107)
					Imp = (107,107,107)	
					speed = 2.5
					k1 = False
					k2 = True
					k3 = False

	if gamemode == "score":
		if textinput.update(events) == True:
			name = textinput.get_text()
			highscores.append((score, name))
			highscores.sort()
			gamemode = "ready"
			cy1 = 0
    
	#screen.fill((0,0,0))
	# Always leave this! It adds your updates.
	update_screen()
	
	if gamemode == "playing":
		lastnote = displayNotes[-1]
		if cy1 > lastnote[1]+100:
			#song is overxs
			playsong = False

			## show score

			textinput = pygame_textinput.TextInput('', text_color=(255, 255, 255), cursor_color=(255, 255, 255))
			textinput.clear_text()
			gamemode = "score"

		if playsong:
			cy1 += speed

	clock.tick(60)
