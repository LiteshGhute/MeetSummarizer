##################################### Import section #####################################

from pathlib import Path
from tkinter import Tk, Canvas, Text, Button, PhotoImage, messagebox, filedialog
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk, ImageSequence
import pywhisper
from langchain.llms import OpenAI
import os
import soundcard as sc
import soundfile as sf
import datetime
import threading
from tkinter import Toplevel, Text
from constant import openai_key

##################################### Application Code #####################################

OUTPUT_PATH = Path(__file__).parent
ASSETS_PATH = OUTPUT_PATH / Path(r"./assets/frame0")


def relative_to_assets(path: str) -> Path:
    return ASSETS_PATH / Path(path)

filepath = ''
getText = ''
os.environ["OPENAI_API_KEY"] = openai_key
llm = OpenAI(temperature = 0.9)

window = Tk()

window.geometry("800x110")
window.configure(bg = "#FFFFFF")

# Set the title of the window
window.title("MeetSummarizer")

# Set the icon of the window (replace "icon.ico" with your icon file)
logo_path = relative_to_assets("logo-transparent-png.ico")
window.iconbitmap(logo_path)


canvas = Canvas(
    window,
    bg = "#242c34",
    height = 110,
    width = 800,
    bd = 0,
    highlightthickness = 0,
    relief = "ridge"
)

canvas.place(x = 0, y = 0)
stopStatus = False
animation_active = True

##################################### Functions Section #####################################

# For start button animation
def animate_gif(index=0):
    global animation_active
    if animation_active:
        global stopStatus
        start_button.config(image=frames[index])
        index = (index + 1) % len(frames)
        window.after(500, animate_gif, index)  # 500ms delay between frames
    else:
        animation_active = True


# To stop start button animation
def stop_animation():
    global animation_active
    animation_active = False

stopStatus = False
data = []
SAMPLE_RATE = 46100     # Change this to improve the recording sound quality


# Audio recording function 
def record_audio():
    global data
    global stopStatus
    global filepath
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    OUTPUT_FILE_NAME = f"audio_file_{timestamp}.wav"
    with sc.get_microphone(id=str(sc.default_microphone().name)).recorder(samplerate=SAMPLE_RATE) as mic:
        print("Recording... Press Stop Button to stop recording.")

        while not stopStatus:  # Check stopStatus within the loop
            chunk = mic.record(numframes=SAMPLE_RATE)
            data.extend(chunk)
        stopStatus = False
        sf.write(file=OUTPUT_FILE_NAME, data=data, samplerate=SAMPLE_RATE)
        print("Recording saved as", OUTPUT_FILE_NAME)
        filepath = OUTPUT_FILE_NAME


# Main function for start button 
def on_start_button_click():
    global stopStatus
    global data
    animate_gif()
    if not stopStatus:
        stopStatus = False
        data = []  # Reset data for a new recording
        threading.Thread(target=record_audio).start()  # Start recording in a separate thread
    else:
        messagebox.showinfo("Dialog", "Recording already in progress.")


# Main function for stop button
def on_stop_button_click():
    global stopStatus
    if not stopStatus:
        stopStatus = True
        print("Recording stopped")
        messagebox.showinfo("Dialog", "Recording stopped")
        start_button.config(image=start_button_image)
        stop_animation()
    else:
        messagebox.showinfo("Dialog", "No recording is started yet.")
    


# Function to show the selected file path or selected file name on the application
def openfile():
    global filepath
    filepath = filedialog.askopenfilename()
    print(filepath)
    canvas.itemconfig(file_label, text= filepath.split("/")[-1])


# Function to generate the transcript
def getTranscript():
    global getText
    if filepath == '':
        messagebox.showinfo("Dialog", "Please select the path")
        return False
    else:
        canvas.itemconfig(file_label, text=filepath.split("/")[-1])
        model = pywhisper.load_model("base.en")
        print("timetakes")
        result = model.transcribe(filepath)
        getText = result["text"]
        # print(getText)
        
        # Create a separate window to display the transcribed text
        text_window = Toplevel()
        text_window.title("Transcribed Text")
        text_window.iconbitmap(logo_path)
        
        # Create a Text widget to show the transcribed text
        text_widget = Text(text_window, wrap=tk.WORD)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Insert the transcribed text into the Text widget
        text_widget.insert(tk.END, getText)
        
        return True
    

# Function to summarize the audio
def summarizeIt():
    global getText
    print("getting transcript")
    status = getTranscript()
    print("got the transcript")
    print("")
    if status:
        info = 'here is the transcript, summarize it without missing any details and important highlight, give a "TITLE", "Heading", "sub-headings" and "Conclusion" and so on...'
        llm = OpenAI(temperature=0.9)
        fullText = info + '  ' + getText
        # print("let print the: " + fullText)
        summarized_text = llm(fullText)  # Get summarized text
        
        # Create a separate window to display the summarized text
        summary_window = Toplevel()
        summary_window.title("Summarized Text")
        summary_window.iconbitmap(logo_path)
        
        # Create a Text widget to show the summarized text with padding
        text_widget = Text(summary_window, wrap=tk.WORD)
        text_widget.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)  # Add padding
        
        # Insert the summarized text into the Text widget
        text_widget.insert(tk.END, summarized_text)
        
        return True
    


##################################### Buttons and Labels Section #####################################


# Load GIF frames and convert to PhotoImage
gif_path = relative_to_assets("recording_button.gif")
with Image.open(gif_path) as gif:
    frames = [ImageTk.PhotoImage(frame) for frame in ImageSequence.Iterator(gif)]


# Create a start button to record audio
start_button_image = PhotoImage(
    file=relative_to_assets("start_button.png"))
start_button = Button(
    image=start_button_image,
    borderwidth=0,
    highlightthickness=0,
    command=on_start_button_click,
    relief="flat"
)
start_button.place(
    x=60.0,
    y=46.0,
    width=30.0,
    height=30.0
)
    

# Creating a stop button to stop recording audio
stop_button_image = PhotoImage(
    file=relative_to_assets("stop_button.png"))
stop_button = Button(
    image=stop_button_image,
    borderwidth=0,
    highlightthickness=0,
    command=on_stop_button_click,
    relief="flat"
)
stop_button.place(
    x=110.0,
    y=46.0,
    width=30.0,
    height=30.0
)


# Background to show the selected file name on the screen 
file_select_background = PhotoImage(
    file=relative_to_assets("file_select_background.png"))
file_select = canvas.create_image(
    320.0,
    60.0,
    image=file_select_background
)


# Label to display the selected file name
file_label = canvas.create_text(
    200.0,
    52.0,
    anchor="nw",
    text="Please select a file...",
    fill="#000000",
    font=("Inter", 12 * -1)
)


# Create a styled browse button using ttk.Button
browse_button = ttk.Button(
    window,
    text="Browse",
    style="Browse.TButton",
    command=openfile
)
browse_button.place(x=480.0, y=48.0, width=50.0, height=27.0)


# Create a styled transcript generate button using ttk.Button
transcript_button = ttk.Button(
    window,
    text="Transcript",
    style="Transcript.TButton",
    command=getTranscript
)
transcript_button.place(x=570.0, y=25.0, width=114.0, height=27.0)


# Create a styled summarize button using ttk.Button
summarize_button = ttk.Button(
    window,
    text="Summarize",
    style="Summarize.TButton",
    command=summarizeIt
)
summarize_button.place(x=570.0, y=60.0, width=114.0, height=27.0)

###################################################################################


window.resizable(False, False)
window.mainloop()


################################# End of the code #################################