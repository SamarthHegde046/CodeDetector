import pyttsx3  

# Initialize text-to-speech engine
engine = pyttsx3.init()

# Set voice
voices = engine.getProperty("voices")
engine.setProperty("voice", voices[0].id)  # Change index if you want another voice

# Set speaking rate
rate = engine.getProperty("rate")
engine.setProperty("rate", rate - 60)

# Welcome message
print("Welcome to ROBO SPEAKER 2.0 Created by Muhammad Navas")
engine.say("Welcome to ROBO SPEAKER 2.0 Created by Muhammad Navas")
engine.runAndWait()

# Loop for user input
while True:
    x = input("Enter what you want me to speak (or 'q' to quit): ")
    if x.lower() == "q":
        print("Goodbye!")
        engine.say("Goodbye! Have a great day.")
        engine.runAndWait()
        break
    engine.say(x)
    engine.runAndWait()
