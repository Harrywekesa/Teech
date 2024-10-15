import pyttsx3
import tkinter as tk
from tkinter import filedialog, messagebox
import re
import os

# Initialize the speech engine
engine = pyttsx3.init()

# Default settings for voice customization
default_rate = 150
default_pitch = 100
character_voice_map = {}
current_file_name = None  # To store the uploaded file name

# Function to set the voice and adjust speed, pitch, and other properties
def set_voice_for_character(character, rate, selected_voice, pitch):
    voices = engine.getProperty('voices')

    # Filter for male or female voices based on the selected voice type
    if selected_voice == "Male":
        for voice in voices:
            if 'male' in voice.name.lower():
                engine.setProperty('voice', voice.id)
                break
    elif selected_voice == "Female":
        for voice in voices:
            if 'female' in voice.name.lower():
                engine.setProperty('voice', voice.id)
                break
    else:
        if character not in character_voice_map:
            voice_id = len(character_voice_map) % len(voices)
            character_voice_map[character] = voices[voice_id].id
        engine.setProperty('voice', character_voice_map[character])

    # Adjust the speech rate (speed) based on pitch
    adjusted_rate = rate + (pitch - default_pitch) * 2  # Simulate pitch with speed variation
    engine.setProperty('rate', adjusted_rate)

# Function to convert text to speech
def text_to_speech(text, character, rate, selected_voice, pitch):
    set_voice_for_character(character, rate, selected_voice, pitch)
    engine.say(text)
    engine.runAndWait()

# Function to read text from a file
def read_file():
    global current_file_name
    file_path = filedialog.askopenfilename(title="Select a text file",
                                           filetypes=(("Text files", "*.txt"),))
    if file_path:
        current_file_name = os.path.basename(file_path).split('.')[0]  # Extract file name without extension
        with open(file_path, 'r') as file:
            return file.readlines()
    return []

# Function to parse dialogue from the script file
def parse_script_lines(lines):
    script = []
    character_dialogue_pattern = re.compile(r"^(\w+):\s*(.+)")  # Pattern: CharacterName: Dialogue

    for line in lines:
        line = line.strip()  # Remove any leading/trailing whitespace
        if not line:
            continue  # Skip empty lines

        match = character_dialogue_pattern.match(line)
        if match:
            character, dialogue = match.groups()
            script.append((character, dialogue))
        else:
            # If no character is detected, treat it as narration
            script.append(("Narrator", line))

    return script

# GUI Application
class TextToSpeechApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Text-to-Speech Converter")
        self.root.geometry("500x550")

        # Welcome message
        self.welcome_label = tk.Label(root, text="Welcome to Text-to-Speech App", font=("Arial", 16))
        self.welcome_label.pack(pady=10)

        # Text box for raw text input
        self.text_entry = tk.Text(root, height=5, width=50)
        self.text_entry.pack(pady=10)

        # Button to select a text file
        self.file_button = tk.Button(root, text="Upload Text File", command=self.upload_file)
        self.file_button.pack(pady=5)

        # Speed control
        self.rate_label = tk.Label(root, text="Adjust Voice Speed:")
        self.rate_label.pack()
        self.rate_slider = tk.Scale(root, from_=100, to_=250, orient=tk.HORIZONTAL)
        self.rate_slider.set(default_rate)
        self.rate_slider.pack()

        # Pitch control
        self.pitch_label = tk.Label(root, text="Adjust Voice Pitch:")
        self.pitch_label.pack()
        self.pitch_slider = tk.Scale(root, from_=50, to_=150, orient=tk.HORIZONTAL)
        self.pitch_slider.set(default_pitch)
        self.pitch_slider.pack()

        # Voice selection (Male, Female)
        self.voice_label = tk.Label(root, text="Select Voice Type (Male/Female):")
        self.voice_label.pack()
        self.voice_var = tk.StringVar(value="Male")
        self.voice_dropdown = tk.OptionMenu(root, self.voice_var, "Male", "Female", "Dynamic (Characters)")
        self.voice_dropdown.pack(pady=5)

        # Output format selection (MP3, WAV)
        self.format_label = tk.Label(root, text="Select Output Format:")
        self.format_label.pack()
        self.format_var = tk.StringVar(value="MP3")
        self.format_dropdown = tk.OptionMenu(root, self.format_var, "MP3", "WAV")
        self.format_dropdown.pack(pady=5)

        # Convert button
        self.convert_button = tk.Button(root, text="Convert to Speech", command=self.convert_text_to_speech)
        self.convert_button.pack(pady=10)

    # Function to upload and read text file
    def upload_file(self):
        lines = read_file()
        if lines:
            self.text_entry.delete('1.0', tk.END)  # Clear existing text
            self.text_entry.insert(tk.END, ''.join(lines))

    # Function to convert text to speech
    def convert_text_to_speech(self):
        global current_file_name
        text = self.text_entry.get("1.0", tk.END).strip()
        if not text:
            messagebox.showerror("Error", "Please enter text or upload a file.")
            return

        # Get the selected rate (speed), pitch, voice, and format
        selected_rate = self.rate_slider.get()
        selected_pitch = self.pitch_slider.get()
        selected_voice = self.voice_var.get()
        selected_format = self.format_var.get().lower()  # Convert to lowercase for file extension

        # Parse the script from the text input
        script_lines = parse_script_lines(text.splitlines())

        # Loop through each dialogue and convert to speech
        for character, dialogue in script_lines:
            print(f"Converting {character}'s line to speech: {dialogue}")
            text_to_speech(dialogue, character, selected_rate, selected_voice, selected_pitch)

        # Determine output file name
        if current_file_name:
            output_file_name = f"{current_file_name}.{selected_format}"
        else:
            first_word = text.split()[0] if text else "output"
            output_file_name = f"{first_word}.{selected_format}"

        # Save output audio as file
        engine.save_to_file(text, output_file_name)
        engine.runAndWait()
        messagebox.showinfo("Success", f"Audio saved as '{output_file_name}'.")

if __name__ == "__main__":
    root = tk.Tk()
    app = TextToSpeechApp(root)
    root.mainloop()
