import pyttsx3                                                       # Voice to  text conversion module for OS                                                 
engine=pyttsx3.init()                                                # Module initialization
voices = engine.getProperty('voices')                                # Getting voice properties available in pyttsx3
engine.setProperty('voice', voices[0].id)                            # Setting voice 
rate=engine.getProperty('rate')                                      # Getting rate property available in pyttsx3
engine.setProperty('rate', rate-60)                                  # Setting rate
print("Welcome to ROBO SPEAKER 2.O Created by Muhammad Navas")       # Welcome message
engine.say("Welcome to ROBO SPEAKER 2.O Created by Muhammad Navas")  # Speak welcome message
engine.runAndWait()                                                  # Run Call                            
x=""                                                                 # Text initilization                        
while True:                                                          # Condition
    if(x.upper() =="Q" or x.lower()=="q"):                           # Condition
        break                                                        # Break condition
    x=input("Enter what you want to me to speak :")                  # Input 
    engine.say(x)                                                    # Call
    engine.runAndWait()                                              # Run Call