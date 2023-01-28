from itertools import count, cycle

import tkinter as tk
from tkinter import IntVar, Label, Frame, Button, Tk, W, ttk
from tkinter import *
from enum import Enum

from PIL import Image, ImageTk
import os
import threading
import mido
from mido import MidiFile, Message, MidiTrack,MetaMessage
from midi import MidiConnector
import datetime
import pygame
from pygame.locals import *
import sys
from functools import partial
import time
import sys
#import accuracyMeasurements
#from practiceGame import practiceGame


root = Tk() #Initializing the GUI
root.title('Digital Piano Tutor')#Setting the title of the window
root.geometry('1067x600')#Setting the size of the window
root.config(bg = 'black')#Setting bg color

#Creating some fonts
centgot50 = ('Century Gothic', 50, 'bold')
centgot32 = ('Century Gothic', 32, 'bold')
centgot42 = ('Century Gothic', 42, 'bold')
centgot12 = ('Century Gothic', 12, 'bold') 
centgot20 = ('Century Gothic', 20, 'bold') 

title_lbl = Label(root, text = 'Digital Piano tutor', fg = 'white', bg = 'black', font = centgot50)
title_lbl.grid(row=0,column=0)
root.columnconfigure(0, weight=1)
root.rowconfigure(0, weight=1)

parent = os.getcwd() #Getting the working directory path
resources_folder = os.path.join(parent, "resources")
resources_path = os.path.join(os.path.abspath("resources"))
midi_path = os.path.join(resources_folder, "midi-files") #Specifying the path of the MIDI files
png_path = os.path.join(resources_folder, "sheet-pngs")  #Specifying the path of the PNGs for the music sheet
piano_keys_path = os.path.join(resources_path, "piano-keys")
#practice_path = os.path.join(os.path.join(parent,"examples"),"created")

pygame.mixer.pre_init(44100, -16, 2, 512) #Set up the mixer that will generate our sounds, 512 buffer size for minimal delay
pygame.init() #Initialize the pygame module to be able to use the mixer

note_filenames = ['f3.ogg', 'gb3.ogg', 'g3.ogg', 'ab3.ogg', 'a3.ogg', 'bb3.ogg', 'b3.ogg', 'c4.ogg', 'db4.ogg', 'd4.ogg', 'eb4.ogg', 'e4.ogg', 'f4.ogg', 'gb4.ogg', 'g4.ogg', 'ab4.ogg', 'a4.ogg', 'bb4.ogg', 'b4.ogg', 'c5.ogg', 'db5.ogg', 'd5.ogg', 'eb5.ogg', 'e5.ogg']

NOTE_SOUNDS = []
for filename in note_filenames:
    NOTE_SOUNDS.append(pygame.mixer.Sound(os.path.join(piano_keys_path, filename)))
    NOTE_SOUNDS.append(pygame.mixer.Sound(os.path.join('resources','piano-keys', filename)))
MIDI_NOTES = [i for i in range(53, 77)]

class RecordingStatus(Enum):
    STOPPED = 0
    RECORDING = 1

class PlayingStatus(Enum):
    STOPPED = 0
    PLAYING = 1

class Mode(Enum):
    STOPPED = 0
    RECORDING = 1
    PLAYING = 2
    LISTENING = 3

AM_PLAYING = PlayingStatus.STOPPED
IS_PLAYING = PlayingStatus.STOPPED
IS_RECORDING = RecordingStatus.STOPPED
RUN = Mode.STOPPED

#Start Playing Frame
def start_game():
    mainmenu_fr.grid_forget()
    start_game_fr = Frame(root, bg='black')
    start_game_fr.grid(row=0, column=0)
    Label(start_game_fr, text='Start Game', font=centgot42,
          fg='black', bg='white', bd=0, width=18, height=2).grid(row=0, pady=20)

    Button(start_game_fr, text='Play Mode', bd=0, font=centgot32,
           fg='black', bg='white', width=15, command = lambda: list_of_songs(1)).grid(row=1, pady=5)
    Button(start_game_fr, text='Practice Mode', bd=0, font=centgot32,
           fg='black', bg='white', width=15, command = lambda: list_of_songs(2)).grid(row=2, pady=5)

    Button(start_game_fr, text='Listen Mode', bd=0, font=centgot32,
           fg='black', bg='white', width=15, command = lambda: list_of_songs(3)).grid(row=3, pady=5)
    Button(start_game_fr, text='Back', font=centgot32, bd=0,
           fg='black', bg='white', width=15, command = go_home).grid(row=4, pady=5)

           
def list_of_songs(mode):
    for w in root.winfo_children():
        w.destroy()
    song_list_fr = Frame(root, bg = 'black')
    song_list_fr.grid(row = 0, column = 0)
    Label(song_list_fr, text='Pick a Song', font=centgot42,
    fg='black', bg='white', bd=0, width=18, height=2).grid(row=0, pady=10)
    files = os.listdir(midi_path)
    if mode == 1:
        for name in files:
            Button(song_list_fr, text = os.path.join(os.path.splitext(name)[0]), bd=0, font=centgot20,fg='black', bg='white', width=25, command = partial(play_mode, name)).grid(row= files.index(name)+1, pady=5) 
    elif mode == 2:
        for name in files:
            Button(song_list_fr, text = os.path.join(os.path.splitext(name)[0]), bd=0, font=centgot20,fg='black', bg='white', width=25, command =  partial(practice_mode, name)).grid(row= files.index(name)+1, pady=5)  
    else:
        for name in files:
            Button(song_list_fr, text = os.path.join(os.path.splitext(name)[0]), bd=0, font=centgot20,fg='black', bg='white', width=25, command =  partial(listen_mode, name)).grid(row= files.index(name)+1, pady=5)  
    Button(song_list_fr, text='Back', font=centgot32, bd=0,
        fg='black', bg='white', width=15, command = go_home).grid(row=len(files) + 1, pady=5) 


class ImageLabel(Label):

    def load(self, im):
        if isinstance(im, str):
            im = Image.open(im)
        frames = []

        try:
            for i in count(1):
                frames.append(ImageTk.PhotoImage(im.copy()))
                im.seek(i)
        except EOFError:
            pass
        self.frames = cycle(frames)
 
        try:
            self.delay = im.info['duration']
        except:
            self.delay = 100
 
        if len(frames) == 1:
            self.configure(image=next(self.frames))
        else:
            self.next_frame()
 
    def unload(self):
        self.cronfigure(image=None)
        self.frames = None
 
    def next_frame(self):
        if self.frames:
            self.configure(image=next(self.frames))
            self.after(self.delay, self.next_frame)

#Running the gif file as a background  GUI using ImageLabel class
gif_lbl = ImageLabel(root, bd=0, width=1280, height=720, bg='black')
gif_lbl.grid(row=0,column=0)
gif_lbl.load('resources/gui-background/musical_notes.gif')

#Main Menu Frame
def start_mainmenu():
    for w in root.winfo_children():
        if w not in (mainmenu_fr, gif_lbl):
            w.grid_forget()
    mainmenu_fr.grid(row = 0, column = 0)

#Go home
def go_home():
    start_mainmenu()

#Quit game method
def quit_game():
    sys.exit()


def show_perf():
    perf = [('Date Time', 'Song Name', 'Click Accuracy', 'Duration Accuracy', 'Overall Accuracy'),
    ('13/4/2021 16:07', 'Happy Birthday', 'Clicks: 96%', 'Duration: 75%', 'Overall: 89%'), 
    ('18/4/2021 11:12', 'Summertime Sadness', 'Clicks: 76%', 'Duration: 83%', 'Overall: 80%')]
    mainmenu_fr.grid_forget()
    trackperf_fr = Frame(root, bg='black')
    Label(trackperf_fr, text='Performance History', font=centgot32).grid(row=0, column=0,sticky=W, pady=10)
    trackperf_fr.grid(row=0, column=0)
    for dt, song, clc, dur, ov in perf:
        row(Label(trackperf_fr, bg='black'),dt, song, clc, dur, ov).grid(columnspan=5, pady=4)
    Button(trackperf_fr, text='Back', font=centgot32, bd=0,
    fg='black', bg='white', width=15, command=go_home).grid(row=4, pady=5) 

def row( label,datetime, songname, click_acc, dur_acc, overall_acc):
    Label(label, text=datetime, bg='white', fg='black', font=centgot12, width=15).grid(row=0, column=0)
    Label(label, text=songname, bg='white', fg='black', font=centgot12, width=40).grid(row=0, column=1)
    Label(label, text=click_acc, bg='white', fg='black', font=centgot12, width=15).grid(row=0, column=2)
    Label(label, text=dur_acc, bg='white', fg='black', font=centgot12, width=18).grid(row=0, column=3)
    Label(label, text=overall_acc, bg='white', fg='black', font=centgot12, width=15).grid(row=0, column=4)
    return label


mainmenu_fr = Frame(root, bg = 'black') #creating the main menu frame
trackperf_fr = Frame(root, bg = 'black')#creating the track performance frame
start_game_fr = Frame(root, bg = 'black')

#Creating the main title label
Label(mainmenu_fr, text='Digital Piano Tutor', font=centgot42,
                  fg='black', bg='white',bd=0, width=18, height=2).grid(row=0, pady=20)

#Creating the necessary buttons in main menu
Button(mainmenu_fr, text='Start Playing',bd=0, font=centgot32,
                  fg='black', bg='white', width=15, command = start_game).grid(row=1, pady=5)
Button(mainmenu_fr, text='Enter a Piece',bd=0, font=centgot32,
                  fg='black', bg='white',  width=15 ).grid(row=2, pady=5)

Button(mainmenu_fr, text='Track Performance', bd=0,font=centgot32,
                  fg='black', bg='white',  width=15, command=show_perf).grid(row=3, pady=5)
Button(mainmenu_fr, text='Quit', font=centgot32,bd=0,
                  fg='black', bg='white', width=15, command=quit_game).grid(row=4, pady=5)

root.bind_all('<Escape>', lambda e: start_mainmenu()) #Whenever Escape is pressed, go back to main menu
root.bind('<BackSpace>', lambda event: go_home())


#Recoder
class MusicPlayer:
    def __init__(self):
        self.MIDI_NOTES = list(range(53, 77))
        self.NOTE_SOUNDS = []
        self.KEY_SOUND = {}
        self.AM_PLAYING = PlayingStatus.STOPPED
        self.IS_PLAYING = PlayingStatus.STOPPED
        self.IS_RECORDING = RecordingStatus.STOPPED
        self.RUN = Mode.STOPPED

    def load_sounds(self):
        # code to load sound files
        pass

    def play_note(self, note):
        # code to play the sound of a specific note
        pass

    def record(self):
        # code to record audio
        pass













































































def waithere():
    t = IntVar()
    root.after(1000, t.set, 1)
    root.wait_variable(t)
waithere()

if title_lbl in root.winfo_children():    
    start_mainmenu()


root.mainloop()