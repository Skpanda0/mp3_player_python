import customtkinter as tk
import tkinter.filedialog as filedialog
import os
import fnmatch
import pygame.mixer as mixer
from CTkListbox import *
from PIL import Image, ImageTk
import io
from mutagen.mp3 import MP3
import time
import threading
import random
from pytube import YouTube
from youtubesearchpython import VideosSearch
import re
import eyed3
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_audio
from mutagen.id3 import APIC, ID3
import requests
import speech_recognition as sr


mixer.init()

# globa variable
playlist = []
song_playing = False
root_path=''
search_results = []
song_folder = ''
next=0
search_results=[]
box_packed = 0
chng_pos = 0
# prev_rand = None
# cur_time=0
# current_song_duration=0
# update_from_slider = False
# slider_moved = False
# slider_position = 0


#gui
#for apperance
def on_theme():
    if theme_check.get():
        tk.set_appearance_mode("light")
        list_box.configure(fg_color="gray")
    else:
        tk.set_appearance_mode("dark")
        
#for listbox showing or not
def list_show():
    global box_packed
    if box_packed == 0:    #first time always hide, so value is 0
        list_box.pack()
        box_packed = 1      #now it showing so value is 1
    else:
        list_box.pack_forget()
        box_packed = 0

#for showing or hiding volume 
def vol():
    if volume_slider.winfo_ismapped():
        volume_slider.pack_forget()
    else:
        volume_slider.pack()

#for get the file and load the song into listbox
def file():
    global root_path, song_folder
    if list_box.size() != 0:
        list_box.delete(0, 'end')
    root_path = filedialog.askdirectory()  #ask whic folder
    song_folder = root_path
    partten = "*.mp3"
    for root, dirs, files in os.walk(root_path):    #it just enter the data into listbox and playlist
        for filename in fnmatch.filter(files, partten):
            list_box.insert('end', filename)
            playlist.append(filename)

#for find the song which are in that folder
def search_song_off():
    global playlist
    song_name=search_entry_off.get()        #get the data from the search entry
    index = 0
    for file in playlist:
        name = os.path.splitext(os.path.basename(f"{root_path}\\{file}"))[0].lower()        #all the file name into small to find easy
        if song_name.lower() in name:
            i=list_box.curselection()
            list_box.deactivate(i)
            list_box.activate(index)
            lable.configure(text=list_box.get())
            play_song()
        index = index+1
    search_entry_off.delete(0 , 'end')
    search_entry_off._activate_placeholder()
    search_button_off.focus()

#display the image
def song_img():
    global root_path
    audiofile = eyed3.load(f"{root_path}\\{list_box.get()}")
    images = audiofile.tag.images 
#code for load the image
    if images:
        # Extract the first image 
        image_data = images[0].image_data
        image = Image.open(io.BytesIO(image_data))
        image = image.resize((200, 200)) 
        img = ImageTk.PhotoImage(image=image)
        image_label.configure(image=img)
        image_label.image = img  
    else:
        # If no image display a default image
        default_image = Image.open("C:\\Users\\sunil\\Downloads\\song.jpeg") 
        default_image = default_image.resize((200, 200))
        img = ImageTk.PhotoImage(image=default_image)
        image_label.configure(image=img)
        image_label.image = img

#find the song length and current time
def song_length(position=0):
    global chng_pos
    if chng_pos == 0:
        cur_s = list_box.curselection()
        if cur_s == 0:
            cur_s += 1
        if song_playing and cur_s:
            cur_time = mixer.music.get_pos()/1000  #it gives from 0 sec
            convert_curr_time = time.strftime('%M:%S', time.gmtime(cur_time))   #
            selected_item = list_box.get(list_box.curselection())
            audio_info = MP3(f"{root_path}\\{selected_item}")
            audio_length = int(audio_info.info.length)
            song_slider.configure(to=audio_length)
            song_slider.set(cur_time)
            convert_song = time.strftime('%M:%S', time.gmtime(audio_length))
            song_dur.configure(text=convert_curr_time)
            song_dur_last.configure(text=convert_song)
            root.after(1000, song_length)
    else:
        root.after_cancel(song_length) #for the function call in every second


#while chnage the slider it set the song position
def set_song_position(value):
    global chng_pos
    chng_pos = song_slider.get()
    mixer.music.set_pos(chng_pos)
    chng()

#after change the positon it start the slider movement
def chng():
    global chng_pos
    if chng_pos == 0:
        root.after_cancel(chng)
    else:
        cur_time = mixer.music.get_pos()/1000  
        cur_time += chng_pos
        convert_curr_time = time.strftime('%M:%S', time.gmtime(cur_time))
        song_dur.configure(text=convert_curr_time)
        song_slider.set(cur_time)
        root.after(1000, chng)

#it use for play the song
def play_song(value=0):
    global song_playing,chng_pos
    chng_pos = 0
    if value == 0:
        song_playing = True
        if list_box.curselection() == None:
            list_box.activate(0)
        mixer.music.load(f"{root_path}\\{list_box.get()}")
        mixer.music.play()
        song_length()
        song_img()

#if we select the song and press the button it play that song
def select():
    global song_playing
    lable.configure(text=list_box.get())
    play_song()
    
#stop the song
def stop():
    index = list_box.curselection()
    mixer.music.stop()
    list_box.deactivate(index)

#it play the next song according to current selecting song
def next():
    global song_playing
    next = list_box.curselection()
    if next < list_box.size()-1:
        list_box.deactivate(next)
        list_box.activate(next+1)
        lable.configure(text=list_box.get())
        play_song()
    else:
        list_box.deactivate(list_box.size()-1)
        list_box.activate(0)
        lable.configure(text=list_box.get())
        play_song()
    
#it play the previous song according to current selecting song
def prev():
    global song_playing
    next = list_box.curselection()
    list_box.deactivate(next)
    list_box.activate(next-1)
    lable.configure(text=list_box.get())
    play_song()

#if we not press next song it automatically play the song
def play_auto_thread():
    global song_playing
    while True:
        if song_playing and not mixer.music.get_busy():
            song_playing = False
            next()  # Play the next song after the current one finishes
        time.sleep(1)

#pause the song
def pause():
    global song_playing
    if song_playing == True:
        mixer.music.pause()
        song_playing = False
    else:
        mixer.music.unpause()
        song_playing = True

#set the volume
def set_volume(value):
    mixer.music.set_volume(float(value) / 100)

#using random module we shuffle the song
def shuffle():
    global playlist
    list_box.delete(0, 'end')
    random.shuffle(playlist)
    for i in playlist:
        list_box.insert('end', i)
    list_box.activate(0)
    lable.configure(text=list_box.get())
    play_song()

#tab 2 logics
#show waring if anything not working
def show_custom_warning(message):
    warning_window = tk.CTk()
    warning_window.title("Warning")

    warning_label = tk.CTkLabel(warning_window, text=message, font=("Helvetica", 14))
    warning_label.pack(padx=20, pady=20)

    ok_button = tk.CTkButton(warning_window, text="OK", command=warning_window.destroy)
    ok_button.pack(pady=10)

    warning_window.mainloop()

#clear the whole tab
def clear():
    result_text.delete(0 , 'end')
    search_entry.delete(0 , 'end')
    prg_label.pack_forget()
    prg_bar.pack_forget()
    frame8.pack_forget()

#search the song in youtube and give 10 links
def search_song():
    global search_results
    prg_label.pack_configure()
    prg_bar.pack_configure(pady=10)
    frame8.pack_configure(padx=5,pady=5, anchor = 'n')
    status_label.pack_configure(anchor="s",padx=10,pady=15)
    query = search_entry.get()
    videos_search = VideosSearch(query, limit=10)
    search_results = videos_search.result()['result']
    for index, result in enumerate(search_results):
        result_text.insert('end', f"{index + 1}. {result['title']}\n")

#it shows how download %
def on_progress(stream, chunk, bytes_remaining):
    total_size = stream.filesize
    bytes_downloaded = total_size - bytes_remaining
    percentage = bytes_downloaded / total_size * 100
    prg_label.configure(text=str(int(percentage))+ "%")
    prg_label.update()
    prg_bar.set(float(percentage / 100))

#download teh song and convert into .mp3
def download():
    global search_results, root_path

    video_link = search_results[result_text.curselection()]['link']
    yt = YouTube(video_link, on_progress_callback=on_progress)
    audio_stream = yt.streams.filter(only_audio=True).first()
    thumbnail_url = yt.thumbnail_url
    response = requests.get(thumbnail_url)
    
    try:
        title = sanitize_filename(yt.title)
        audio_filename = f"{title}.mp4"

        # Download the audio stream
        audio_stream.download(output_path=root_path, filename=audio_filename)

        if response.status_code == 200:
            thumbnail_filename = f"{root_path}\\{title}.jpg"
            with open(thumbnail_filename, 'wb') as f:
                f.write(response.content)
        
        output_file_path = f"{root_path}\\{title}.mp3"
        input_file_path = f"{root_path}\\{audio_filename}"

        try:
            ffmpeg_extract_audio(input_file_path, output_file_path)
            curr = list_box.curselection()
            list_box.deactivate(curr)
            list_box.delete(0, 'end')
            pattern = "*.mp3"
            for root, dirs, files in os.walk(root_path):
                for filename in fnmatch.filter(files, pattern):
                    list_box.insert('end', filename)
                    playlist.append(filename)
        except:
            show_custom_warning("Conversion is not successful")
        
        os.remove(input_file_path)

    except:
        show_custom_warning("Can't Download That song")

    add_album_art(output_file_path, thumbnail_filename)

#save the thumbnail of that song place into the audio file
def add_album_art(audio_filename, thumbnail_filename):
    audio = ID3(audio_filename)
    with open(thumbnail_filename, "rb") as albumart:
        audio.add(APIC(3, 'image/jpeg', 3, 'Front cover', albumart.read()))
        audio.save()
        os.remove(thumbnail_filename)

#it uses to avoid all the special words to _
def sanitize_filename(filename):
    sanitized_filename = re.sub(r'[\/:*?"<>|]', '_', filename)
    return sanitized_filename

#use mic to seach the song
def mic_use():
    search_entry.delete(0 , 'end')
    r = sr.Recognizer()
    with sr.Microphone() as source:
        mic_label.configure(text="Listening...")
        r.pause_threshold = 0.5
        audio = r.listen(source)
    try:
        mic_label.configure(text="Recognizing...")
        quary = r.recognize_google(audio , language = 'en-in')
        time.sleep(1)
    except Exception as e:
        mic_label.configure(text="Say That Again please... ")
    search_entry.insert(0, quary)
    mic_label.configure(text="")

# gui part
root = tk.CTk()
root.title("mp3 Player")
root.geometry("600x600")
root.maxsize(600,600)

root._set_appearance_mode("dark")

tabview = tk.CTkTabview(master=root)
tabview.pack(fill='both', expand=True)
tabview.add("Home")
#leftside frame
frame1 = tk.CTkFrame(tabview.tab("Home"))
frame1.pack(padx=5, pady=5, expand=True, side = 'left',anchor='nw')
# file
file_button = tk.CTkButton(frame1, text="choose folder",command=file, width=40, height=10)
file_button.pack(pady=10)
#listbox
list_button = tk.CTkButton(frame1, text="Song list" , command=list_show ,width=40, height=10)
list_button.pack(pady=5)

list_box = CTkListbox(tabview.tab("Home"), width=1000)
list_box.pack(padx=10, pady=10, expand=True, fill="both")
list_box.pack_forget()
#theme
lable1 = tk.CTkLabel(frame1 , text="Apperance : ",width=100)
lable1.pack(pady=10)

theme_check = tk.CTkCheckBox(frame1, text="light" , border_width=1 , checkbox_height=15, checkbox_width=15)
theme_check.pack(padx=25)
theme_check.configure(command=on_theme)

#volume
volume_button= tk.CTkButton(frame1, text="volume" , command=vol ,width=40, height=10)
volume_button.pack(pady=10)
volume_slider = tk.CTkSlider(frame1, from_=0, to=100, command=set_volume, height=10, width=140)
volume_slider.set(50)  # Set the initial volume to 50%
volume_slider.pack(pady=15 )
volume_slider.pack_forget()


#frame2
frame2 = tk.CTkFrame(tabview.tab("Home"), width=900)
frame2.pack(padx=5,pady=5, anchor = 'n', expand=True, fill="both")

#frame3(serch , button)
frame3 = tk.CTkFrame(frame2,width=900)
frame3.pack(padx=5,pady=5)

search_entry_off = tk.CTkEntry(frame3, width=200, placeholder_text="Song name")
search_entry_off.pack(side=tk.LEFT,pady=10, padx=30 )

search_button_off = tk.CTkButton(frame3, text="Search", command=search_song_off)
search_button_off.pack(side=tk.LEFT,pady=10, padx=10 )

#frame4(song iamge, name , time)
frame4=tk.CTkFrame(frame2,width=900)
frame4.pack(padx=5,pady=5)

image_label = tk.CTkLabel(frame4 ,text='')
image_label.pack(pady=10)
default_image = Image.open("C:\\Users\\sunil\\Downloads\\song.jpeg") 
default_image = default_image.resize((200, 200))
img = ImageTk.PhotoImage(image=default_image)
image_label.configure(image=img)

lable = tk.CTkLabel(frame4, text='',width=250)
lable.pack(pady=5)

song_dur = tk.CTkLabel(frame4 , text='00:00')
song_dur.pack(side = tk.LEFT,padx=5,pady=5)

song_slider = tk.CTkSlider(frame4, from_=0, to=100 , command=set_song_position , width=170)
song_slider.set(0)
song_slider.pack(side = tk.LEFT,padx=5,pady=5)


song_dur_last=tk.CTkLabel(frame4 , text='00:00')
song_dur_last.pack(side = tk.LEFT,padx=5,pady=5)

#frame5(prev,play,pause,next,shuffle button)
frame5 = tk.CTkFrame(frame2,width=900)
frame5.pack(padx=5,pady=5)

prev_img = tk.CTkImage(dark_image=Image.open(r'D:\vscode\projects\mp3\prev.png') , size=(25,25))
next_img = tk.CTkImage(dark_image=Image.open(r'D:\vscode\projects\mp3\next.png'), size=(25,25))
play_img = tk.CTkImage(dark_image=Image.open(r'D:\vscode\projects\mp3\play.png'), size=(25,25))
pause_img = tk.CTkImage(dark_image=Image.open(r'D:\vscode\projects\mp3\pause.png'), size=(25,25))
shuffle_img = tk.CTkImage(dark_image=Image.open('D:\\vscode\\projects\\mp3\\shuffle.png'), size=(25,25))

prev_button = tk.CTkButton(frame5, text="", image=prev_img, command=prev, width=5, height=5 , fg_color="black", bg_color='black')
prev_button.pack(side = tk.LEFT,padx=7,pady=5)

play_button = tk.CTkButton(frame5, text="", command=select, image=play_img, width=5, height=5, fg_color="black", bg_color='black')
play_button.pack(side = tk.LEFT,padx=7,pady=5)

pause_button = tk.CTkButton(frame5, text="", image=pause_img, command=pause, width=5, height=5, fg_color="black", bg_color='black')
pause_button.pack(side = tk.LEFT,padx=7,pady=5)

next_button = tk.CTkButton(frame5, text="", image=next_img, command=next, width=5, height=5, fg_color="black", bg_color='black')
next_button.pack(side = tk.LEFT,padx=7,pady=5)

shuffle_button = tk.CTkButton(frame5, text="", image=shuffle_img, command=shuffle, width=5, height=5, fg_color="black", bg_color='black')
shuffle_button.pack(side = tk.LEFT,padx=7,pady=5)


#search
tabview.add("Search")

frame6 = tk.CTkFrame(tabview.tab("Search"))
frame6.pack(padx=5,pady=5, anchor = 'n')

search_entry = tk.CTkEntry(frame6, width=200, placeholder_text="Song name")
search_entry.pack(side=tk.LEFT,pady=10, padx=30 )

mic = tk.CTkButton(frame6, text='mic',width=5 , command=mic_use)
mic.pack(side=tk.LEFT,pady=10, padx=10 )

search_button = tk.CTkButton(frame6, text="Search", command=search_song)
search_button.pack(side=tk.LEFT,pady=10, padx=10 )

mic_label = tk.CTkLabel(tabview.tab("Search"), text='')
mic_label.pack(padx=5,pady=10,anchor = 'n')

result_text = CTkListbox(tabview.tab("Search"),fg_color="gray", width=1000)
result_text.pack(padx=5,pady=10,anchor = 'n')

frame7 = tk.CTkFrame(tabview.tab("Search"))
frame7.pack(padx=5,pady=5, anchor = 'n')

download_button = tk.CTkButton(frame7, text="Download" ,command=download)
download_button.pack(side=tk.LEFT,pady=10, padx=10 )

clear_button = tk.CTkButton(frame7, text="clear" ,command=clear)
clear_button.pack(side=tk.LEFT,pady=10, padx=10 )

frame8 = tk.CTkFrame(tabview.tab("Search"))


prg_label = tk.CTkLabel(frame8, text="0%")

prg_bar = tk.CTkProgressBar(frame8, width=400)
prg_bar.set(0.0)

status_label = tk.CTkLabel(tabview.tab("Search"),text="Status: Idle")


#threading
music_thread = threading.Thread(target=play_auto_thread)
music_thread.daemon = True
music_thread.start()
root.mainloop()


