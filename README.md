# Sophie
A project to build a next generation home robot

This will be where I store the code base for my robot project. The robot is a next generation home robot with a omni directional drive unit and 6 axis collaborative robot arm. The robot is heavly centered around being soley on-board based processing, this is because, I believe we should stray away from paid models, subscriptions and IOT things as they loose much of their abilitys if the power or internet go out. That is not to say it wont have some things linked to the internet, just more that if the internet goes out it is not a rather expensive paper weight. 

The software will be caotic at first as I'm still in the process of learning python well. I welcome all input from all walks of life on coding as long as it is constructive in nature.

Initial software/programs:
1. voice_assist - This will be a voice assistant based on the vosk voice recognition project, It uses a offline text to speech system to report back anwsers to questions you have. Recently I swapped it to a smaller neural network model and it has been preforming quite well on the TX2.
2. memory_sys - based on a database (will need to look into this, as it will play a important role to the robot. Think like the ability to recall the last time you seen someone if asked) 
3. reading_module - This is a work in progress of a pipeline program to read pysical books and writing, This will unlock many use cases for the robot. It currently is in a working state, but also sloooow. 
4. Face_recog

Current tasks for the robot to preform:
1. Read a physical book (with my now 7 year old flipping the pages) 
2. *Play hide and seek (requested by my daughter, she is going places)
3. Wipe down a table (any old table top, more so, see if the table is in a state to be cleaned, then find a rag, fdkjghaskdfh well maybe have a rag with cleaning solution on-board?)
4. Pick up items on the floor and place them in a basket. (requested by the wife...) 
5. Bring a drink from one location to another (it's a beer right?)
6. Serve wine/champagne for a party environment (more alcohol!)
7. Greet people at the door (I suppose it could try to say hi and then learn thier names while also linking it to the face_recognition module)

Hardware specs:
1. Nividia Jetson TX2
2. Ufactory Lite 6 (6 axis robot arm, able to lift ~1kg)
3. ZED stereo vision camera
4. Respeaker v2.0 (Microphone)
5. 3x stepper motor drives
6. 1x Pi Pico, (controls the stepper drives, and other low level sensors)
7. 2x 30ah life batteries 

I suggest going over to the following website for more info on build and progress. https://hackaday.io/project/182694-sophie-robot
