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
from functions import *

### DO THIS ONLY ONCE #####
#create_empty_csv('Results_Experiment2')

# Audio settings
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 22050
p = pyaudio.PyAudio()

# variables and parameters
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
path = os.getcwd()
dirstims = path + '/stimuli_music_snippets/'
conditions = ['A', 'B', 'C']  # conditions: 1=A=Prefered, 2=B=Disprefered, 3=C=Globally Ambiguous
conditions_fillers = ['1', '2', '3']

# RUNNING THE EXPERIMENT
try:
    # ASK DATA IN CONSOLE (1)

    # get subject (and experiment)
    subj = raw_input('subject initials (no spaces or accents): ')
    subj = subj.lower()

    # get pilot data (which pilot are we passing)
    pilot = raw_input('pilot (1 is closure task; 2 is selection task): ')
    TRIALS = trial_generation(conditions, conditions_fillers)

    for t in range(len(TRIALS)):
        TRIALS[t]['subject'] = subj
        TRIALS[t]['experiment'] = '2'
        TRIALS[t]['pilot'] = pilot

    # initialize pygame and fonts
    pygame.init()
    pygame.font.init()

    # randomize TRIALS per participant
    random.shuffle(TRIALS)

    # OPEN SCREEN  (2)

    # full screen for actual experiment
    #screen = pygame.display.set_mode([0, 0], FULLSCREEN | DOUBLEBUF | HWSURFACE)

    # smaller screen size for debug
    screen = pygame.display.set_mode([1000, 600])
    SCREEN_X, SCREEN_Y = screen.get_size()

    # SHOW INSTRUCTIONS (3)
    if pilot == '1':
        showInstructions(screen, 'instructions_1.jpeg')

        # EXAMPLES(3')

        # EX1. CLOSED SEQUENCE
        example1= 'examples/Example_Sequences_closed'
        example2= 'examples/Example_Sequences_open'

        play_stim(example1)

        img = pygame.image.load('pilot1_example1.jpeg')
        img_size_x, img_size_y = img.get_size()
        img_pos_x = round((SCREEN_X - img_size_x) / 2)
        img_pos_y = round((SCREEN_Y - img_size_y) / 2)
        screen.blit(img, (img_pos_x, img_pos_y))
        pygame.display.flip()
        wait_for_space()

        play_stim(example2)

        # EX2. OPEN SEQUENCE
        img = pygame.image.load('pilot1_example2.jpeg')
        img_size_x, img_size_y = img.get_size()
        img_pos_x = round((SCREEN_X - img_size_x) / 2)
        img_pos_y = round((SCREEN_Y - img_size_y) / 2)
        screen.blit(img, (img_pos_x, img_pos_y))
        pygame.display.flip()
        wait_for_space()


    elif pilot == '2':
        showInstructions(screen, 'instructions_2.jpeg')



    # PRACTICE (4)
    #
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

        # fixation point(A)
        screen.fill(WHITE)
        font = pygame.font.SysFont('Tahoma', 36)
        text = font.render('+', True, (0, 0, 0))
        img_size_x, img_size_y = text.get_size()
        screen.blit(text, (round((SCREEN_X - img_size_x) / 2), round((SCREEN_Y - img_size_y) / 2)))
        pygame.display.update()
        wait_for_space()

        # self-paced-listening(B) : 5 chunks
        for i in range(len(TRIALS[t]['chunks'])):
            tiempo = self_paced_listening(screen, TRIALS[t]['chunks'][i][0])
            TRIALS[t]['chunks'][i][1] = tiempo  # saving the listening time
            pygame.display.flip()
            TRIALS[t]['total.listening.time'] = int(TRIALS[t]['total.listening.time']) + int(TRIALS[t]['chunks'][i][1])
            print TRIALS[t]['chunks'][i]


        # offline task(C)
        if pilot == '1':
            response, response_time = closure_task(screen, 'How complete did this chord sequence sound to you?')
            print(response, response_time)
            TRIALS[t]['response'] = response
            TRIALS[t]['response_time'] = response_time
            pygame.display.update()
        elif pilot == '2':
            response, response_time = selection_task(screen, '01A', '01A')
            TRIALS[t]['response'] = response
            TRIALS[t]['response_time'] = response_time
            pygame.display.update()

    # QUESTIONS (6)


    # FINAL SCREEN (7)

    screen.fill(WHITE)
    font = pygame.font.SysFont('Tahoma', 36)
    text = font.render('Thanks!', True, (0, 0, 0))
    img_size_x, img_size_y = text.get_size()
    screen.blit(text, (round((SCREEN_X - img_size_x) / 2), round((SCREEN_Y - img_size_y) / 2)))
    pygame.display.update()
    time.sleep(5)

    # SAVE RESULTS (8)
    os.chdir(path + '/subject_results/')
    name = subj + '_' + pilot + '_python'
    with open(name, 'wb') as f:
        pickle.dump(TRIALS, f)

    # include results of the subject in bigger csv
    include_csv_data('Results_Experiment2', TRIALS, path)


except:
    os.chdir(path + '/subject_results/')
    name = subj + '_' + pilot + '_python'
    with open(name, 'wb') as f:
        pickle.dump(TRIALS, f)

    include_csv_data('Results_Experiment2', TRIALS, path)



finally:
    pygame.quit()
    p.terminate()
