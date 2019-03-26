#!/usr/bin/env python3

## pip3 install simpleaudio

import os
import time
import math
import pygame
import pygame.midi
import pygame.time
import pygame_textinput

import simpleaudio as sa
#sa = None

# define all the constant values -----------------------------------------------
volume = 127
device = 1     # device number in win10 laptop
#device = 2     # desktop


# http://www.ccarh.org/courses/253/handout/gminstruments/
instrument = 0 

whole = 16
half = 8
quarter = 4
eighth = 2
sixteenth = 1

class Song:
  def __init__(self, name):
    self.name = name

happysong = Song("Happy Birthday")
happysong.song = [('D4', eighth+sixteenth), ('D4', sixteenth), ('E4', quarter), 
             ('D4', quarter), ('G4', quarter), 
             ('F4#', eighth), ('D4', eighth+sixteenth), 
             ('D4', sixteenth), ('E4', quarter), ('D4', quarter), 
             ('A4', quarter), ('G4', half), ('D4', eighth+sixteenth), ('D4', sixteenth), 
             ('D5', quarter), ('B4', quarter), ('G4', quarter), 
             ('F4#', quarter), ('E4', quarter), ('C5', eighth+sixteenth), 
             ('C5', sixteenth), ('B4', quarter), 
             ('G4', quarter), ('A4', quarter), ('G4', half+quarter)]

happysong.Noteid = ["D4", "E4", "F4#", "G4", "A4", "B4", "C5", "D5"]
happysong.Keyids = ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k']


twinkle = Song("Twinkle Twinkle Little Star")
twinkle.Noteid = ["C4", "D4", "E4", "F4", "G4", "A4", "B4", "C5"]
twinkle.Keyids = ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k']

twinkle.song = [('C4', quarter), ('C4', quarter), ('G4', quarter), ('G4', quarter), ('A4', quarter), ('A4', quarter), ('G4', half),
                ('F4', quarter), ('F4', quarter), ('E4', quarter), ('E4', quarter), ('D4', quarter), ('D4', quarter), ('C4', half),
                ('G4', quarter), ('G4', quarter), ('F4', quarter), ('F4', quarter), ('E4', quarter), ('E4', quarter), ('D4', half),
                ('G4', quarter), ('G4', quarter), ('F4', quarter), ('F4', quarter), ('E4', quarter), ('E4', quarter), ('D4', half),
                ('C4', quarter), ('C4', quarter), ('G4', quarter), ('G4', quarter), ('A4', quarter), ('A4', quarter), ('G4', half),
                ('F4', quarter), ('F4', quarter), ('E4', quarter), ('E4', quarter), ('D4', quarter), ('D4', quarter), ('C4', half),
                ]

theSong = happysong
theSong = twinkle

wait_time = 0.5

def note2midi(note):
  octave = int(note[1])
  n = "C D EF G A B".index(note[0])

  mnote = (octave+1)*12 + n
  
  if len(note) > 2:
    if note[2] == "#": mnote += 1
    elif note[2] == "f": mnote -= 1

  return mnote

buffer = []
cy1 = 0
betpress = []


def initialize_window(width, height):
  pygame.init()
  pygame.display.set_caption('Happy Birthday!... for now.')
  #screen = pygame.display.set_mode(size)
  screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
  #screen = pygame.display.set_mode((1920,1080))
  screen.fill((0,0,0))

  return screen

class PianoGame:
  def __init__(self, song):
    self.song = song
    self.playgasd = False

  def update_screen(self):
        self.screen.fill((0,0,0))

        if self.gamemode == "playing":
                self.screen.fill((255,255,255), (0,self.bottom,self.width,4))  # draw scoring line

                cy2 = self.cy1 + self.bottom

                dx = 80
                margin = (self.width - dx*8) // 2

                for noteid, note in enumerate(self.song.Noteid):
                        x = (noteid * dx) + margin
                        self.screen.fill((255,255,255), (x,0,1,self.bottom))  # draw note line

                        bgcolor = (255,255,255)

                        if self.keypressed and self.song.Keyids.index(self.keypressed) == noteid:
                          bgcolor = (255,0,0) 

                        textsurface = self.myfont.render(note, False, bgcolor)  # draw Note
                        self.screen.blit(textsurface,(x-textsurface.get_size()[0]//2,self.bottom+30))

                        textsurface = self.myfont.render(self.song.Keyids[noteid], False, bgcolor) # draw key
                        self.screen.blit(textsurface,(x-textsurface.get_size()[0]//2,self.bottom+50))

                for (y1, y2, note) in self.displayNotes:
                        if y2 < self.cy1 or y1 > cy2: continue
                        noteid = self.song.Noteid.index(note)
                        x = (noteid * dx) + margin
                        y = self.bottom - (y2-self.cy1)
                        self.screen.fill((0, 76, 255), (x-10, y, 20, y2-y1))

        textsurface = self.myfont.render("Score: %d" % self.score, False, (255,255,255))
        self.screen.blit(textsurface, (500, 200))


        if self.gamemode in ("ready", "score"):
                textsurface = self.myfont.render("Highscores", False, (255,255,255))
                self.screen.blit(textsurface, ((self.width-textsurface.get_size()[0])//2, self.height//4-50))

                topten = self.highscores[-10:]
                topten.reverse()
                for i, (highscore, name) in enumerate(topten):
                  textsurface = self.myfont.render("%s %s" % (name, highscore), False, (255,255,255))
                  self.screen.blit(textsurface, ((self.width-textsurface.get_size()[0])//2, self.height//4 + i*30))

        if self.gamemode == "ready":
                if (int(time.time()*2) % 2) == 0:
                        color = (255,255,255)
                else:
                        color = (50,50,50)
                textsurface = self.myfont.render("Please Enter to Start", False, color)
                self.screen.blit(textsurface, ((self.width-textsurface.get_size()[0])//2, self.height//2+50))

                textsurface = self.myfont.render("Speed Options:", False, (255,255,255))
                self.screen.blit(textsurface, (1250, 250))

                textsurface = self.myfont.render("Super slow", False, (self.Slow))
                self.screen.blit(textsurface, (1250, 300))

                textsurface = self.myfont.render("Normal", False, (self.Normal))
                self.screen.blit(textsurface, (1250, 350))

                textsurface = self.myfont.render("Impossable", False, (self.Imp))
                self.screen.blit(textsurface, (1250, 400))

                textsurface = self.myfont.render("Press 1, 2, or 3 ", False, (255,255,255))
                self.screen.blit(textsurface, (1250, 600))

                textsurface = self.myfont.render("to change difficulty ", False, (255,255,255))
                self.screen.blit(textsurface, (1250, 650))

                textsurface = self.myfont.render("level", False, (255,255,255))
                self.screen.blit(textsurface, (1250, 700))

        if self.gamemode == "score":
                textsurface = self.myfont.render("Please enter your name: ", False, (255,255,255))
                self.screen.blit(textsurface, ((self.width-textsurface.get_size()[0])//2, self.height//2+50))

                textinput_surf = self.textinput.get_surface()
                self.screen.blit(textinput_surf, ((self.width-textsurface.get_size()[0])//2, self.height//2 + 100))

        # Blit its surface onto the screen
        pygame.display.flip()


  def run(self):
    self.width = 640
    self.height = 480
    self.screen = initialize_window(self.width, self.height)
    self.width, self.height = pygame.display.get_surface().get_size()

    self.bottom = self.height - 300
    self.score = 0

    self.highscores = [(1000, "Hayden"), (500, "Jacob"), (200, "Charlotte")]
    self.highscores.sort()

    self.speed = 3

    pygame.font.init() 
    self.myfont = pygame.font.SysFont('Arial', 30)

    self.displayNotes = []
    y = int(self.height / 2)
    noteHeight = 20

    for (note, dur) in self.song.song:
      self.displayNotes.append((y, y + dur * noteHeight, note))
      y += (dur * noteHeight)
      y += noteHeight//5

    # Everything that changes, lives in your game loop!
    # while the game is running, it updates!
    self.clock = pygame.time.Clock()

    self.running = True
    self.keypressed = None
    self.playsong = False

    self.buffer = []
    self.cy1 = 0

    self.k1 = False
    self.k2 = False
    self.k3 = False

    self.Slow = (101,255,0)
    self.Normal = (250,255,0)
    self.Imp = (255,0,0)

    self.gamemode = "ready"

    while self.running:
      events = pygame.event.get()
      for event in events:
        # This will exit game loop
        if event.type == pygame.QUIT:
          self.running = False

        if self.gamemode == "playing":
          if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                  self.score = 0 
                  self.playsong = True
                elif event.key == pygame.K_q:
                  return
                else:
                  c = chr(event.key)
                  if not self.keypressed:
                    if c in self.song.Keyids:
                      i = self.song.Keyids.index(c)
                      note = self.song.Noteid[i]
                      if note:
                        self.buffer.append(c)
                        if self.player:
                          self.player.note_on(note2midi(note), volume)
                        self.keypressed = c

          if event.type == pygame.KEYUP:
                c = chr(event.key)
                if self.keypressed:
                  if c == self.keypressed:
                    if c in self.song.Keyids:
                      i = self.song.Keyids.index(c)
                      note = self.song.Noteid[i]

                      if self.player:
                        self.player.note_off(note2midi(note), volume)
                      self.keypressed = None


        if self.gamemode == "ready":
          if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
              self.score = 0 
              self.playsong = True
              self.gamemode = "playing"

            elif event.key == pygame.K_1:
                    self.Slow = (101,255,0)
                    self.Normal = (107,107,107)
                    self.Imp = (107,107,107)
                    self.speed = 1
                    self.k1 = False
                    self.k2 = True
                    self.k3 = False

            elif event.key == pygame.K_2:
                    self.Normal = (250,255,0)
                    self.Slow = (107,107,107)
                    self.Imp = (107,107,107)	
                    self.speed = 2.5
                    self.k1 = False
                    self.k2 = True
                    self.k3 = False

            elif event.key == pygame.K_3:
                    self.Imp = (255,0,0)
                    self.Slow = (107,107,107)
                    self.Normal = (107,107,107)
                    self.speed = 10
                    self.k1 = False
                    self.k2 = False
                    self.k3 = True

            else:
                    self.Normal = (250,255,0)
                    self.Slow = (107,107,107)
                    self.Imp = (107,107,107)	
                    self.speed = 2.5
                    self.k1 = False
                    self.k2 = True
                    self.k3 = False

        if self.gamemode == "score":
                if self.textinput.update(events) == True:
                        name = self.textinput.get_text()
                        self.highscores.append((self.score, name))
                        self.highscores.sort()
                        self.gamemode = "ready"
                        self.cy1 = 0

      self.update_screen()

      if self.gamemode == "playing":
        if self.keypressed:
            for (y1, y2, note) in self.displayNotes:
              if y2 > self.cy1 and y1 < self.cy1:
                noteid = self.song.Noteid.index(note)
                if noteid == self.song.Keyids.index(self.keypressed):
                  if self.k1 == True:   self.score += 0.25
                  elif self.k2 == True: self.score += 5
                  elif self.k3 == True: self.score += 15
                  elif self.playgasd == False: self.score += 20000
                  elif self.playgasd == True: pass
                  else:
                    self.score += 5

        if not self.playgasd:

                  self.buffer = self.buffer[-6:]
                  s = ''.join(self.buffer)

                  if s.endswith("gasd"):
                    wave_obj = sa.WaveObject.from_wave_file("Ta Da-SoundBible.com-1884170640.wav")
                    play_obj = wave_obj.play()
                    play_obj.wait_done()
                    self.buffer = []
                    self.playgasd = True
                    

                    n = time.time()
      if self.gamemode == "playing":
              lastnote = self.displayNotes[-1]
              if self.cy1 > lastnote[1]+100:
                      #song is overxs
                      self.playsong = False

                      ## show score

                      self.textinput = pygame_textinput.TextInput('', text_color=(255, 255, 255), cursor_color=(255, 255, 255))
                      self.textinput.clear_text()
                      self.gamemode = "score"

              if self.playsong:
                      self.cy1 += self.speed

      self.clock.tick(60)


def main():
  if 1:
    global device

    pygame.midi.init()
    #device = pygame.midi.get_default_output_id()
    while device < 255:
      try:
        player = pygame.midi.Output(device, 0)
        break
      except pygame.midi.MidiException:
        pass
      device += 1

    player.set_instrument(instrument)

  pg = PianoGame(theSong)
  pg.player = player
  pg.run()
  #pygame.midi.quit()

main()
