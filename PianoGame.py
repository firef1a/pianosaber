#!/usr/bin/env python3

## pip3 install simpleaudio

import os, sys, string, time, logging, argparse

import math
import pygame
import pygame.midi
import pygame.time
import pygame_textinput
import config

import simpleaudio as sa
#sa = None

BLACK = (0,0,0)
WHITE = (255,255,255)

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


def note2midi(note):
  octave = int(note[1])
  n = "C D EF G A B".index(note[0])

  mnote = (octave+1)*12 + n
  
  if len(note) > 2:
    if note[2] == "#": mnote += 1
    elif note[2] == "f": mnote -= 1

  return mnote


class States(object):
  def __init__(self):
    self.done = False
    self.next = None
    self.quit = False
    self.previous = None

  def process_events(self, events):
    for event in events:
      self.get_event(event)

class Splash(States):
  def __init__(self, app):
      self.app = app
      States.__init__(self)
      self.next = 'start'

  def startup(self):
      logging.debug('starting Splash state')
      self.timerStarted = True
      self.endTime = time.time() + 3

  def get_event(self, event):
      if event.type == pygame.JOYBUTTONUP:
        logging.debug("Joystick button released.")
        logging.debug(event)
      elif event.type == pygame.KEYDOWN:
        if event.key == pygame.K_SPACE: self.done = True

  def update(self, screen):
    self.draw(screen)

    if self.timerStarted == True:
      if time.time() > self.endTime:
        self.done = True

  def draw(self, screen):
    textsurface = self.app.myfont.render("Piano Saber", False, (255,255,255))
    self.app.screen.blit(textsurface, ((self.app.width-textsurface.get_size()[0])//2, self.app.height//2))


class Start(States):
  def __init__(self, app):
      self.app = app
      States.__init__(self)
      self.next = 'game'

  def startup(self):
      logging.debug('starting Start state')

  def get_event(self, event):
      if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_SPACE: self.done = True

        if event.key == pygame.K_RETURN:
          self.app.score = 0 
          self.done = True
          return

        elif event.key == pygame.K_1:
                self.app.Slow = (101,255,0)
                self.app.Normal = (107,107,107)
                self.app.Imp = (107,107,107)
                self.app.speed = 1
                self.app.k1 = False
                self.app.k2 = True
                self.app.k3 = False

        elif event.key == pygame.K_2:
                self.app.Normal = (250,255,0)
                self.app.Slow = (107,107,107)
                self.app.Imp = (107,107,107)	
                self.app.speed = 2.5
                self.app.k1 = False
                self.app.k2 = True
                self.app.k3 = False

        elif event.key == pygame.K_3:
                self.app.Imp = (255,0,0)
                self.app.Slow = (107,107,107)
                self.app.Normal = (107,107,107)
                self.app.speed = 10
                self.app.k1 = False
                self.app.k2 = False
                self.app.k3 = True

        else:
                self.app.Normal = (250,255,0)
                self.app.Slow = (107,107,107)
                self.app.Imp = (107,107,107)	
                self.app.speed = 2.5
                self.app.k1 = False
                self.app.k2 = True
                self.app.k3 = False



  def update(self, screen):
    self.draw(screen)

  def draw(self, screen):
    screen.fill((0,0,0))

    textsurface = self.app.myfont.render("Score: %d" % self.app.score, False, (255,255,255))
    self.app.screen.blit(textsurface, (500, 200))

    textsurface = self.app.myfont.render("Highscores", False, (255,255,255))
    self.app.screen.blit(textsurface, ((self.app.width-textsurface.get_size()[0])//2, self.app.height//4-50))

    topten = self.app.highscores[-10:]
    topten.reverse()
    for i, (highscore, name) in enumerate(topten):
      textsurface = self.app.myfont.render("%s %s" % (name, highscore), False, (255,255,255))
      self.app.screen.blit(textsurface, ((self.app.width-textsurface.get_size()[0])//2, self.app.height//4 + i*30))


    if (int(time.time()*2) % 2) == 0:
      color = (255,255,255)
    else:
      color = (50,50,50)

    textsurface = self.app.myfont.render("Please Enter to Start", False, color)
    self.app.screen.blit(textsurface, ((self.app.width-textsurface.get_size()[0])//2, self.app.height//2+50))

    textsurface = self.app.myfont.render("Speed Options:", False, (255,255,255))
    self.app.screen.blit(textsurface, (1250, 250))

    textsurface = self.app.myfont.render("Super slow", False, (self.app.Slow))
    self.app.screen.blit(textsurface, (1250, 300))

    textsurface = self.app.myfont.render("Normal", False, (self.app.Normal))
    self.app.screen.blit(textsurface, (1250, 350))

    textsurface = self.app.myfont.render("Impossable", False, (self.app.Imp))
    self.app.screen.blit(textsurface, (1250, 400))

    textsurface = self.app.myfont.render("Press 1, 2, or 3 ", False, (255,255,255))
    self.app.screen.blit(textsurface, (1250, 600))

    textsurface = self.app.myfont.render("to change difficulty ", False, (255,255,255))
    self.app.screen.blit(textsurface, (1250, 650))

    textsurface = self.app.myfont.render("level", False, (255,255,255))
    self.app.screen.blit(textsurface, (1250, 700))




class Finish(States):
  def __init__(self, app):
      self.app = app
      States.__init__(self)
      self.next = 'start'

  def startup(self):
      logging.debug('starting Finish state')
      self.textinput = pygame_textinput.TextInput('', text_color=(255, 255, 255), cursor_color=(255, 255, 255))
      self.textinput.clear_text()

  def process_events(self, events):
      if self.textinput.update(events) == True:
        name = self.textinput.get_text()
        self.app.highscores.append((self.app.score, name))
        self.app.highscores.sort()

        self.done = True
        
  def update(self, screen):
    self.draw(screen)

  def draw(self, screen):
    screen.fill((0,0,0))

    textsurface = self.app.myfont.render("Score: %d" % self.app.score, False, (255,255,255))
    self.app.screen.blit(textsurface, (500, 200))

    textsurface = self.app.myfont.render("Highscores", False, (255,255,255))
    self.app.screen.blit(textsurface, ((self.app.width-textsurface.get_size()[0])//2, self.app.height//4-50))

    topten = self.app.highscores[-10:]
    topten.reverse()
    for i, (highscore, name) in enumerate(topten):
      textsurface = self.app.myfont.render("%s %s" % (name, highscore), False, (255,255,255))
      self.app.screen.blit(textsurface, ((self.app.width-textsurface.get_size()[0])//2, self.app.height//4 + i*30))

    textsurface = self.app.myfont.render("Please enter your name: ", False, (255,255,255))
    self.app.screen.blit(textsurface, ((self.app.width-textsurface.get_size()[0])//2, self.app.height//2+50))

    textinput_surf = self.textinput.get_surface()
    self.app.screen.blit(textinput_surf, ((self.app.width-textsurface.get_size()[0])//2, self.app.height//2 + 100))


class PianoGame(States):
  def __init__(self, app, song):
    self.app = app
    States.__init__(self)
    self.next = 'finish'

    self.song = song

  def startup(self):
    logging.debug('starting Game state')

    self.playgasd = False

    self.bottom = self.app.height - 300

    self.displayNotes = []
    y = int(self.app.height / 2)
    noteHeight = 20

    for (note, dur) in self.song.song:
      self.displayNotes.append((y, y + dur * noteHeight, note))
      y += (dur * noteHeight)
      y += noteHeight//5

    self.running = True
    self.keypressed = None
    self.playsong = False

    self.buffer = []
    self.cy1 = 0


  def update(self, screen):
    if self.keypressed:
        for (y1, y2, note) in self.displayNotes:
          if y2 > self.cy1 and y1 < self.cy1:
            noteid = self.song.Noteid.index(note)
            if noteid == self.song.Keyids.index(self.keypressed):
              if self.app.k1 == True:   self.app.score += 0.25
              elif self.app.k2 == True: self.app.score += 5
              elif self.app.k3 == True: self.app.score += 15
              elif self.playgasd == True: self.app.score += 20000
              else:
                self.app.score += 5

        if not self.playgasd:
          self.buffer = self.buffer[-6:]
          s = ''.join(self.buffer)

          if s.endswith("gasd"):
            wave_obj = sa.WaveObject.from_wave_file("Ta Da-SoundBible.com-1884170640.wav")
            play_obj = wave_obj.play()
            play_obj.wait_done()
            self.buffer = []
            self.playgasd = True
                    
    lastnote = self.displayNotes[-1]
    if self.cy1 > lastnote[1]+100:
      #song is overxs
      self.playsong = False

      ## show score
      self.done = True
      return

    if self.playsong:
      self.cy1 += self.app.speed

    self.draw(screen)

  def draw(self, screen):
    screen.fill((0,0,0))

    if 1:
      screen.fill((255,255,255), (0,self.bottom,self.app.width,4))  # draw scoring line

      cy2 = self.cy1 + self.bottom

      dx = 80
      margin = (self.app.width - dx*8) // 2

      for noteid, note in enumerate(self.song.Noteid):
        x = (noteid * dx) + margin
        screen.fill((255,255,255), (x,0,1,self.bottom))  # draw note line

        bgcolor = (255,255,255)

        if self.keypressed and self.song.Keyids.index(self.keypressed) == noteid:
          bgcolor = (255,0,0) 

        textsurface = self.app.myfont.render(note, False, bgcolor)  # draw Note
        screen.blit(textsurface,(x-textsurface.get_size()[0]//2,self.bottom+30))

        textsurface = self.app.myfont.render(self.song.Keyids[noteid], False, bgcolor) # draw key
        screen.blit(textsurface,(x-textsurface.get_size()[0]//2,self.bottom+50))

      for (y1, y2, note) in self.displayNotes:
        if y2 < self.cy1 or y1 > cy2: continue
        noteid = self.song.Noteid.index(note)
        x = (noteid * dx) + margin
        y = self.bottom - (y2-self.cy1)
        self.app.screen.fill((0, 76, 255), (x-10, y, 20, y2-y1))

    textsurface = self.app.myfont.render("Score: %d" % self.app.score, False, (255,255,255))
    screen.blit(textsurface, (500, 200))


  def get_event(self, event):
    if event.type == pygame.KEYDOWN:
      if event.key == pygame.K_RETURN:
        self.app.score = 0 
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



class App:
  def __init__(self, **settings):
    self.__dict__.update(settings)
    self.done = False
    self.state = None
    self.state_name = None
    self.state_dict = None
    self.dirty = []

    #self.screen = pygame.display.set_mode(config.screensize, pygame.FULLSCREEN|pygame.DOUBLEBUF|pygame.HWSURFACE)
    #self.screen = pygame.display.set_mode(config.screensize, pygame.FULLSCREEN|pygame.HWSURFACE)
    self.screen = pygame.display.set_mode(config.screensize, pygame.DOUBLEBUF|pygame.HWSURFACE)
    pygame.display.set_caption('Happy Birthday!... for now.')

    self.width, self.height = self.screen.get_size()


    self.highscores = [(1000, "Hayden"), (500, "Jacob"), (200, "Charlotte")]
    self.highscores.sort()
    self.score = 0
    self.speed = 3

    self.k1 = False
    self.k2 = False
    self.k3 = False

    self.Slow = (101,255,0)
    self.Normal = (250,255,0)
    self.Imp = (255,0,0)

  def setup_states(self, state_dict, start_state):
    self.state_dict = state_dict
    self.state_name = start_state
    self.state = self.state_dict[self.state_name]
    self.state.startup()

  def flip_state(self):
    self.state.done = False
    previous,self.state_name = self.state_name, self.state.next
    self.state = self.state_dict[self.state_name]
    self.state.startup()
    self.state.previous = previous

  def update(self):
    if self.state.quit:
      self.done = True
    elif self.state.done:
      self.flip_state()
    self.state.update(self.screen)

  def event_loop(self):
    events = pygame.event.get()

    for event in events:
      if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE: self.done = True
      if event.type == pygame.QUIT: self.done = True

    if not self.done:
      self.state.process_events(events)

  def main_game_loop(self):
    self.myfont = pygame.font.SysFont('Arial', 30)
    self.clock = pygame.time.Clock()

    while not self.done:
      delta_time = self.clock.tick(self.fps)/1000.0
      self.event_loop()
      self.update()

      if 0:
        fps = 1./delta_time
        textsurface = self.myfont.render("fps: %.1f" % fps, True, BLACK)
        pygame.draw.rect(self.screen, WHITE, (0, 0, textsurface.get_size()[0], textsurface.get_size()[1]), 0)
        self.screen.blit(textsurface, (0, 0))

      pygame.display.update()
      #pygame.display.flip()


def start():
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

  app = App(fps=30)

  pg = PianoGame(app, theSong)
  pg.player = player

  state_dict = {
      'splash': Splash(app),
      'start': Start(app),
      'game': pg,
      'finish':Finish(app),
  }

  app.setup_states(state_dict, 'splash')
  app.main_game_loop()

  pygame.midi.quit()
  pygame.quit()




def parse_args(argv):
  parser = argparse.ArgumentParser(
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    description=__doc__)

  parser.add_argument("-t", "--test", dest="test_flag",
                    default=False,
                    action="store_true",
                    help="Run test function")
  parser.add_argument("--log-level", type=str,
                      choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                      help="Desired console log level")
  parser.add_argument("-d", "--debug", dest="log_level", action="store_const",
                      const="DEBUG",
                      help="Activate debugging")
  parser.add_argument("-q", "--quiet", dest="log_level", action="store_const",
                      const="CRITICAL",
                      help="Quite mode")
  #parser.add_argument("files", type=str, nargs='+')

  args = parser.parse_args(argv[1:])
  if args.log_level is None: args.log_level = "INFO"

  return parser, args

def main(argv, stdout, environ):
  if sys.version_info < (3, 0): reload(sys); sys.setdefaultencoding('utf8')

  parser, args = parse_args(argv)

  numeric_loglevel = getattr(logging, args.log_level.upper(), None)
  if not isinstance(numeric_loglevel, int):
    raise ValueError('Invalid log level: %s' % args.log_level)

  logging.basicConfig(format="[%(asctime)s] %(levelname)-8s %(message)s",
                       datefmt="%m/%d %H:%M:%S", level=numeric_loglevel)

  if args.test_flag:  test();   return

  start()

if __name__ == "__main__":
  main(sys.argv, sys.stdout, os.environ)
