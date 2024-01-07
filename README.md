# Sophie
A project to build a next generation home robot

The envisioned tasks for the Sophie Robot project are multifaceted, aiming to blend practical utility with advanced technological features. Key tasks include reading physical books (interacting with children), wiping down tables, picking up items from the floor, serving drinks, and greeting people at the door. The design also considers aiding the elderly and disabled, such as fetching items and assisting with feeding. Additional functionalities include using OpenCV for facial recognition, and providing weather updates. Overall I'm attempting to create a versatile, interactive, and helpful home robot.

This will be where I store the code base for my robot project. The robot is a next generation home robot with a omni directional drive unit and 6 axis collaborative robot arm. The robot is heavly centered around being soley on-board based processing, this is because, I believe we should stray away from paid models, subscriptions and IOT things as they loose much of their abilitys if the power or internet go out. That is not to say it wont have some things linked to the internet, just more that if the internet goes teh robot does not become a rather expensive paper weight. That being said it now features Chat GPT passoff, when a phrase is not understood... lol

The software will be caotic at first as I'm still in the process of learning python well. I welcome all input from all walks of life on coding as long as it is constructive in nature.

Initial software/programs:
1. voice_assist.py - This is a voice assistant based on the vosk voice recognition project, It uses a offline text to speech system to report back anwsers to questions you have. It falls back to chat GPT 4 if a offline phrase is not detected. Recently I swapped it to a smaller neural network model and it has been preforming quite well on the TX2.
2. reading_module.py - This is a work in progress of a working pipeline program to read physical books and writing, This will unlock many use cases for the robot. It currently is in a working state, but also sloooow. (Takes a image from the camera now)
3. chat_gpt4.py - This is a pass off module that pings the Chat GPT 4 servers for a response then speaks it out.
4. zed_snap.py - Initilizes the ZED camera, takes a high resolution photo, date/time stamps it and saves to a folder. (has a rough implementation of image stabilization)
5. weather_service.py - This class retrieves the current weather report for a specified city using the OpenWeather API. It constructs
and sends a request to the API with the city name, desired units (imperial or metric), and the API key. After
receiving the response, the function parses the JSON data to extract key weather details such as temperature,
humidity, and weather description.
6. security_module.py - This security class module focuses on providing an automated security system. It integrates a ZED stereo camera and various sensors to monitor an environment for potential security breaches. The system is capable of detecting motion and is planned to be equipped with AI audio analysis for detecting sounds like breaking glass, enhancing its security capabilities.

Not yet implemented (WIP)
7. memory_sys - based on a database (will need to look into this, as it will play a important role to the robot. Think like the ability to recall the last time you seen someone if asked) 
8. Face_recog - 

Current tasks for the robot to preform:
1. General voice assitance for around the house (now supercharged with Chat GPT!) (check, needs some work but working none the less, It's hearing itself and answering itself and also it should turn to face the direction of the sound if able)
2. Read a physical book (with my now 7 year old flipping the pages) The reading module is done, need to fine tune it to speed up and preprocess the image more.
3. Play hide and seek (requested by my daughter, she is going places) (person asks to play hide and seek the robot says "it would love too play hide and seek", (movment stuff is not implemented yet) It rotates 360 scanning the room, it then heads to the wall all while counting down from 10, states (ready or not here I come) It then goes into a complicated and methodical search pattern looking for small human like figures and or faces. (Never to find anything of course as children will for sure out smart it or lose attention, lol)
4. Wipe down a table (any old table top, more so, see if the table is in a state to be cleaned, then find a rag, fdkjghaskdfh well maybe have a rag with cleaning solution on-board?)
5. Pick up items on the floor and place them in a basket. (requested by the wife...) (Use vision based AI to scan the floor and anything it thinks it can grab try 3 times, if sucessful take to a bin and drop it in)
6. Bring a drink from one location to another (it's a beer right?) (map based off the ladar, then vision based AI to find drink, attempt to grasp three times then take to user if successful. (go hide in corner if not successful) 
7. Serve wine/champagne for a party environment (more alcohol!) Custom serving tray, advanced people/croud navigation... stop once and a while do a large pattern while generally avoiding walls, furniture, fall hazards, robot traps and people. 
8. Greet people at the door (I suppose it could try to say hi and then learn thier names while also linking it to the face_recognition module?)

Hardware specs:
1. 1x Nvidia Jetson TX2
2. 1x Ufactory Lite 6 (6 axis robot arm, able to lift ~1kg)
3. 1x ZED stereo vision camera
4. 1x Respeaker v2.0 (Microphone)
5. 3x stepper motor drive units
6. 1x Pi Pico, (controls the stepper drives, and other low level sensors)
7. 2x 12v 30ah LiFePO4 Deep Cycle batteries 

I suggest going over to the following website for more info on build and progress. https://hackaday.io/project/182694-sophie-robot
