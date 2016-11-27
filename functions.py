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


############################################################
###################### FUNCTIONS ###########################
############################################################

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
            ('Subject', 'Experiment', 'Pilot', 'Item', 'Condition', 'Experiment', 'Chunk', 'Trans', 'List.time', 'Response.Time', 'Answer', 'Total.List.Time'))
    f.close()

def showInstructions(screen, instructions):
    screen.fill(WHITE)
    SCREEN_X, SCREEN_Y = screen.get_size()
    img = pygame.image.load(instructions)
    img_size_x, img_size_y = img.get_size()
    img_pos_x = round((SCREEN_X-img_size_x)/2)
    img_pos_y = round((SCREEN_Y-img_size_y)/2)
    screen.blit(img,(img_pos_x,img_pos_y))
    pygame.display.flip()
    wait_for_space()

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

def self_paced_listening(screen, sound):
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

#General funciton
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
    text = font.render('Which one completes better the sequence?', True, (0, 0, 0))
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
    #('Subject', 'Experiment', 'Pilot', 'Type', 'Condition', 'Experiment', 'Chunk', 'Transposition', 'List.time', 'Response.Time', 'Answer', 'Total.List.Time'))
    os.chdir(path)
    with open(name, 'a') as f:
        writer = csv.writer(f)
        for t in range(len(trials)):
            for i in range(len(trials[t]['chunks'])):
                writer.writerow((trials[t]['subject'], trials[t]['experiment'], trials[t]['pilot'], trials[t]['type'],
                                 trials[t]['condition'], str(i),
                                 trials[t]['chunks'][i][1], trials[t]['response_time'], trials[t]['response'], trials[t]['total.listening.time']))

    f.close()

# CREATING STIMULI #TOTAL: 18 EXPERIMENTAL ITEMS + 9 FILLERS = 27 trials
def trial_generation(conditions, conditions_filler):
    TRIALS = []
    # experimental items(1) 6 repetitions * 3 conditions = 18 items


    for c in range(len(conditions)):
        for i in range(6):  # Repetitions/Transpositions (same 6 transpositions for all participants, differences within subjecst)
            trial = {}
            trial['subject'] ='NA'
            trial['experiment'] ='NA'
            trial['pilot'] = 'NA'
            trial['response'] = 'NA'
            trial['response_time'] ='NA'
            trial['total.listening.time'] = 0

            trial['type'] = 'experimental_trial'
            trial['condition'] = conditions[c]
            trial['dir'] = 'chords/'
            # files: transposition-chunk-
            # trials['chunks'] = [[chunk1: chord, time=0], [chunk2: chord, time=0]...]
            t = 0  # time
            trial['transposition']= str(i)
            trial['chunks'] = [[trial['dir'] + str(i) + '-' + '1', t], [trial['dir'] + str(i) + '-' + '2', t],
                               [trial['dir'] + str(i) + '-' + '3', t],
                               [trial['dir'] + str(i) + '-' + '4' + '-' + str(c + 1), t],
                               [trial['dir'] + str(i) + '-' + '5', t]]

            TRIALS.append(trial)

    # include fillers(2) (conditions are FOR FILLERS, different conditions)
    ## now: 3 repetitions, 9 fillers

    for c in range(len(conditions_filler)):
        for i in range(3):  # Repetitions/Transpositions
            trial = {}
            trial['subject'] ='NA'
            trial['experiment'] ='NA'
            trial['pilot'] = 'NA'
            trial['response'] = 'NA'
            trial['response_time'] ='NA'
            trial['total.listening.time'] = 0

            trial['type'] = 'filler'
            trial['condition'] = conditions_filler[c]
            trial['dir'] = 'fillers/'
            trial['transposition'] = str(i)
            trial['chunks'] = [[trial['dir'] + str(i) + '-' + '1', t],
                               [trial['dir'] + str(i) + '-' + '2' + '-' + trial['condition'], t],
                               [trial['dir'] + str(i) + '-' + '3', t], [trial['dir'] + str(i) + '-' + '4', t],
                               [trial['dir'] + str(i) + '-' + '5', t]]
            TRIALS.append(trial)

    return TRIALS

