# import packages
import pyaudio
import wave
import csv
import pygame
from pygame.locals import *
import random
import os
import pickle
import time

# Audio settings
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 22050
p = pyaudio.PyAudio()

# variables and parameters
WHITE = (255,255,255)
BLACK = (0,0,0)
path = os.getcwd()
dirstims = path+'/stimuli_music_snippets/'

# Functions
def wait_for_space():
    pygame.event.get()  # clear previous events
    while True:
        for ev in pygame.event.get():
            if ev.type == QUIT or (ev.type == KEYDOWN and ev.key == K_ESCAPE):
                raise Exception
            elif ev.type == KEYDOWN and ev.key == K_SPACE:
                t = pygame.time.get_ticks()
                return t

def create_empty_csv(name):
    with open(name, 'wb') as f:
        writer = csv.writer(f)
        writer.writerow(
            ('Subject', 'Experiment', 'Pilot', 'Condition', 'Experiment', 'Chunk', 'RT', 'Answer', 'TotalRT'))
    f.close()

def showInstructions(screen, instructions):
    screen.fill(WHITE)
    img = pygame.image.load(instructions)
    img_size_x, img_size_y = img.get_size()
    img_pos_x = round((SCREEN_X-img_size_x)/2)
    img_pos_y = round((SCREEN_Y-img_size_y)/2)
    screen.blit(img,(img_pos_x,img_pos_y))
    pygame.display.flip()
    t = wait_for_space()

def stim(sound):  # retrieve the file name & place
    sound = dirstims + sound + '.wav'
    return sound

def play_sound(sound):
    wf = wave.open(stim(sound), 'rb')
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)
    data = wf.readframes(CHUNK)

    while data != '':
        stream.write(data)
        data = wf.readframes(CHUNK)

def self_paced_listening(sound):
    screen.fill(WHITE)
    t0 = pygame.time.get_ticks()
    SCREEN_X, SCREEN_Y = screen.get_size()
    img = pygame.image.load('music.jpg')
    img_size_x, img_size_y = img.get_size()
    img_pos_x = round((SCREEN_X-img_size_x)/2)
    img_pos_y = round((SCREEN_Y-img_size_y)/2)
    screen.blit(img,(img_pos_x,img_pos_y))

    pygame.display.update()

    wf = wave.open(stim(sound), 'rb')
    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                    channels=wf.getnchannels(),
                    rate=wf.getframerate(),
                    output=True)
    data = wf.readframes(CHUNK)

    while data != '':

        stream.write(data)
        data = wf.readframes(CHUNK)
        ev = pygame.event.poll()
        if ev.type == QUIT or (ev.type == KEYDOWN and ev.key == K_ESCAPE):
            raise Exception
        elif ev.type == KEYDOWN and ev.key == K_SPACE:
            t = pygame.time.get_ticks() - t0
            stream.stop_stream()
            stream.close()
            screen.fill(WHITE)
            pygame.display.update()
            return t

def self_paced(m):
    screen.fill(WHITE)
    t0 = pygame.time.get_ticks()
    font = pygame.font.SysFont('Tahoma', 28)
    text = font.render(m, True, (0, 0, 0))
    textpos = text.get_rect()
    textpos.centerx = screen.get_rect().centerx
    screen.blit(text, textpos)
    t1 = play_stim(m) - t0
    pygame.display.update()
    return t1

def draw_button(label, button_pos, button_size, screen):
    posX = button_pos[0]
    posY = button_pos[1]
    sizeX = button_size[0]
    sizeY = button_size[1]

    font = pygame.font.SysFont('Tahoma', 14)
    text = font.render(label, True, (0, 0, 0))
    text_X, text_Y = font.size(label)

    pygame.draw.rect(screen, BLACK, (posX, posY, sizeX, sizeY), 2)
    screen.blit(text, (posX + round((sizeX - text_X) / 2), posY + round((sizeY - text_Y) / 2)))

def inside_button(pos, button_pos, button_size):
    if (pos[0] >= button_pos[0]) and (pos[0] <= (button_pos[0]+button_size[0])) and (pos[1] >= button_pos[1]) and (pos[1] <= (button_pos[1]+button_size[1])):
        return True
    else:
        return False

def closure_task(screen,text):

    screen.fill(WHITE)
    SCREEN_X, SCREEN_Y = screen.get_size()
    BUTTON_SIZE = (round(SCREEN_X/7), round(SCREEN_Y/10))

    t0 = pygame.time.get_ticks()
    font = pygame.font.SysFont('Tahoma', 28)
    text = font.render(text, True, (0, 0, 0))
    img_size_x, img_size_y = text.get_size()
    screen.blit(text, (round((SCREEN_X - img_size_x) / 2), round((SCREEN_Y - img_size_y) / 3)))
    pygame.display.update()

    # DRAW BUTTONS
    draw_button("Totally complete",[SCREEN_X/6, SCREEN_Y/2],BUTTON_SIZE,screen)
    draw_button("Somewhat complete", [SCREEN_X*2/6, SCREEN_Y / 2], BUTTON_SIZE, screen)
    draw_button("Somewhat incomplete", [SCREEN_X*3/6, SCREEN_Y / 2], BUTTON_SIZE, screen)
    draw_button("Totally incomplete", [SCREEN_X*4/6, SCREEN_Y/2], BUTTON_SIZE, screen)
    pygame.display.update()

    response = 'null'

    while True:
        event = pygame.event.poll()
        (x, y) = pygame.mouse.get_pos()

        # print str(t)+": pos x: "+str(x)+", pos y: "+str(y)+" "
        if event.type == pygame.MOUSEBUTTONUP:
            if inside_button((x, y), [SCREEN_X/6, SCREEN_Y/2], BUTTON_SIZE):
                # print "fin: false (" + str(sample)+ " samples)"
                response = 'Totally complete'
                t = pygame.time.get_ticks() - t0
                return response, t
            if inside_button((x, y), [SCREEN_X*4/6, SCREEN_Y/2], BUTTON_SIZE):
                # print "fin: true (" + str(sample)+ " samples)"
                response = 'Totally incomplete'
                t = pygame.time.get_ticks() - t0
                return response,t

            if inside_button((x, y), [SCREEN_X*3/6, SCREEN_Y/2], BUTTON_SIZE):
                # print "fin: true (" + str(sample)+ " samples)"
                response = 'Somewhat incomplete'
                t = pygame.time.get_ticks() - t0
                return response,t

            if inside_button((x, y), [SCREEN_X*2/6, SCREEN_Y/2], BUTTON_SIZE):
                # print "fin: true (" + str(sample)+ " samples)"
                response = 'Somewhat complete'
                t = pygame.time.get_ticks() - t0
                return response,t

            else:
                print "outside"




    return t1

def selection_task(screen, sound1, sound2):
    screen.fill(WHITE)
    SCREEN_X, SCREEN_Y = screen.get_size()
    BUTTON_SIZE = (round(SCREEN_X/8), round(SCREEN_Y/10))

    # write in the screen (1)
    font = pygame.font.SysFont('Tahoma', 28)
    text = font.render('Listen to these two possible continuations', True, (0, 0, 0))
    img_size_x, img_size_y = text.get_size()
    screen.blit(text, (round((SCREEN_X - img_size_x) / 2), round((SCREEN_Y - img_size_y) / 3)))
    pygame.display.update()

    # play sound 1 (2)
    draw_button("Option A", [SCREEN_X/3 - BUTTON_SIZE[0], SCREEN_Y/2], BUTTON_SIZE, screen)
    time.sleep(2)
    pygame.display.update()
    play_sound(sound1)

    # play sound 2 (3)
    draw_button("Option B", [SCREEN_X*3/4 - BUTTON_SIZE[0], SCREEN_Y/2], BUTTON_SIZE, screen)
    pygame.display.update()
    play_sound(sound2)

    # write in the screen (4)
    t0 = pygame.time.get_ticks()
    screen.fill(WHITE)
    pygame.display.update()
    font = pygame.font.SysFont('Tahoma', 28)
    text = font.render('Which one completes bettter the sequence?', True, (0, 0, 0))
    img_size_x, img_size_y = text.get_size()
    screen.blit(text, (round((SCREEN_X - img_size_x) / 2), round((SCREEN_Y - img_size_y) / 3)))
    # display buttons
    draw_button("Option A", [SCREEN_X/3 - BUTTON_SIZE[0], SCREEN_Y/2], BUTTON_SIZE, screen)
    draw_button("Option B", [SCREEN_X*3/4 - BUTTON_SIZE[0], SCREEN_Y/2], BUTTON_SIZE, screen)
    pygame.display.update()

    # wait for the answer (5)
    response = 'null'

    while True:
        event = pygame.event.poll()
        (x, y) = pygame.mouse.get_pos()

        # print str(t)+": pos x: "+str(x)+", pos y: "+str(y)+" "
        if event.type == pygame.MOUSEBUTTONUP:
            if inside_button((x, y), [SCREEN_X/3 - BUTTON_SIZE[0], SCREEN_Y/2], BUTTON_SIZE):
                # print "fin: false (" + str(sample)+ " samples)"
                response = 'A'
                t = pygame.time.get_ticks() - t0
                return response, t
            if inside_button((x, y), [SCREEN_X*3/4 - BUTTON_SIZE[0], SCREEN_Y/2], BUTTON_SIZE):
                # print "fin: true (" + str(sample)+ " samples)"
                response = 'B'
                t = pygame.time.get_ticks() - t0
                return response, t

            else:
                print "outside"

def include_csv_data(name, trials, path):
    os.chdir(path)
    with open(name, 'a') as f:
        writer = csv.writer(f)
        for t in range(len(trials)):
            for i in range(len(trials[t]['chunks'])):
                writer.writerow((trials[t]['subject'], trials[t]['experiment'], trials[t]['pilot'],
                                 trials[t]['condition'], 'Experiment2', trials[t]['chunks'][i][0],
                                 trials[t]['chunks'][i][1], 'Answer', 'TotalRT'))

    f.close()


### DO THIS ONLY ONCE #####
# create_empty_csv('Results_Experiment2')


# CREATING STIMULI (II)
#conditions: 1=A=Prefered, 2=B=Disprefered, 3=C=Globally Ambiguous

conditions = ['1','2','3']
TRIALS = []
# experimental items(1)
for c in range(len(conditions)):
    for i in range(4): # Repetitions/Transpositions
        trial = {}
        trial['type'] = 'experimental_trial'
        trial['condition'] = conditions[c]
        trial['dir'] = 'chords/'
        # files: transposition-chunk
        # trials['chunks'] = [[chunk1: chord, time=0], [chunk2: chord, time=0]...]
        trial['chunks'] = [[trial['dir']+str(i)+'-'+'1', 0],[trial['dir']+str(i)+'-'+'2', 0], [trial['dir']+str(i)+'-'+'3', 0], [trial['dir']+str(i)+'-'+'4'+'-'+trial['condition'], 0], [trial['dir']+str(i)+'-'+'5', 0]]
        TRIALS.append(trial)

# include fillers(2) (conditions are FOR FILLERS, different conditions)
conditions_filler = ['1','2','3']
for c in range(len(conditions_filler)):
    for i in range(4): # Repetitions/Transpositions
        trial = {}
        trial['type'] = 'filler'
        trial['condition'] = conditions[c]
        trial['dir'] = 'fillers/'
        trial['chunks'] = [[trial['dir']+str(i)+'-'+'1', 0],[trial['dir']+str(i)+'-'+'2'+'-'+trial['condition'], 0], [trial['dir']+str(i)+'-'+'3', 0], [trial['dir']+str(i)+'-'+'4', 0], [trial['dir']+str(i)+'-'+'5', 0]]
        TRIALS.append(trial)



# 1. increase the number of repetitions to 6 (6*3=18 experimental items)
# 2. pick first 6 random transpositions
# 3. each participants hears these (6 between participants)
# 4. (2*3 = fillers), pick 2 transpositions
# 24 items now.



# RUNNING THE EXPERIMENT(II)
try:
    # ASK DATA IN CONSOLE (1)
    # get subject (and experiment)
    subj = raw_input('subject initials (no spaces or accents): ')
    subj = subj.lower()
    # get pilot data (which pilot are we passing)
    pilot = raw_input('pilot (1 is closure task; 2 is selection task): ')

    pygame.init()  # initialize pygame
    pygame.font.init()

    random.shuffle(TRIALS)  # randomize TRIALS per participant
    print (TRIALS) #debug

    # OPEN SCREEN  (2)
    # full screen for actual experiment
    # screen = pygame.display.set_mode([0, 0], FULLSCREEN | DOUBLEBUF | HWSURFACE)

    # smaller screen size for debug
    screen = pygame.display.set_mode([1000, 600])
    SCREEN_X, SCREEN_Y = screen.get_size()

    # SHOW INSTRUCTIONS (3)
    if pilot=='1':
        showInstructions(screen, 'instructions_1.jpeg')
    elif pilot=='2':
        showInstructions(screen, 'instructions_2.jpeg')

    #PRACTICE (4)
    # screen.fill(WHITE)
    # font = pygame.font.SysFont('Tahoma', 36)
    # text1 = font.render('Remember to press SPACE to start', True, (0, 0, 0))
    # text = font.render('+', True, (0, 0, 0))
    # img_size_x, img_size_y = text.get_size()
    # img_size_x1, img_size_y1 = text1.get_size()
    # screen.blit(text, (round((SCREEN_X - img_size_x) / 2), round((SCREEN_Y - img_size_y) / 2)))
    # screen.blit(text1, (round((SCREEN_X - img_size_x1) / 3), round((SCREEN_Y - img_size_y1) / 2)))
    # pygame.display.update()
    # wait_for_space()
    #
    # # self-paced-listening(B) : 5 chunks
    # for i in range(len(TRIALS[1]['chunks'])):
    #     self_paced_listening(TRIALS[t]['chunks'][i][0])
    #     pygame.display.flip()
    # # offline task(C)
    # if pilot == '1':
    #     response, t = closure_task(screen, 'How complete did this chord sequence sound to you?')
    #     pygame.display.update()
    # elif pilot == '2':
    #     response, t = selection_task(screen, '01A', '01A')
    #     pygame.display.update()

    # BEGIN TRIALS (5)
    for t in range(len(TRIALS)):
        TRIALS[t]['subject'] = subj
        TRIALS[t]['experiment'] = '2'
        TRIALS[t]['pilot'] = pilot

        # fixation point(A)
        screen.fill(WHITE)
        font = pygame.font.SysFont('Tahoma', 36)
        text = font.render('+', True, (0, 0, 0))
        img_size_x, img_size_y = text.get_size()
        screen.blit(text, (round((SCREEN_X-img_size_x)/2), round((SCREEN_Y-img_size_y)/2)))
        pygame.display.update()
        wait_for_space()

        # self-paced-listening(B) : 5 chunks
        for i in range(len(TRIALS[t]['chunks'])):
            tiempo = self_paced_listening(TRIALS[t]['chunks'][i][0])
            TRIALS[t]['chunks'][i][1] = tiempo  # saving the listening time
            pygame.display.flip()
            print TRIALS[t]['chunks'][i]

        # offline task(C)
        if pilot == '1':
            response,t =closure_task(screen,'How complete did this chord sequence sound to you?')
            pygame.display.update()
        elif pilot=='2':
            response, t =selection_task(screen,'01A','01A')
            pygame.display.update()

    #QUESTIONS? (6)

    #FINAL SCREEN (7)

    screen.fill(WHITE)
    font = pygame.font.SysFont('Tahoma', 36)
    text = font.render('Thanks!', True, (0, 0, 0))
    img_size_x, img_size_y = text.get_size()
    screen.blit(text, (round((SCREEN_X - img_size_x) / 2), round((SCREEN_Y - img_size_y) / 2)))
    pygame.display.update()
    time.sleep(5)

    #SAVE RESULTS (8)
    os.chdir(path+'/subject_results/')
    name = subj +'_' + pilot + '_python'
    with open(name, 'wb') as f:
        pickle.dump(TRIALS, f)
    #include results of the subject in bigger csv
    include_csv_data('Results', TRIALS, path)

finally:
        pygame.quit()
        p.terminate()


