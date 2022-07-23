# Sophie
A project to build a next generation home robot

This will be where I store the code base for my robot project. The robot is a next generation home robot with a omni directional drive unit and 6 axis collaborative robot arm. The robot is heavly centered around being soley on-board based processing, this is because, I believe we should stray away from paid models, subscriptions and IOT things as they loose much of their abilitys if the power or internet go out. That is not to say it wont have some things linked to the internet, just more that if the internet goes out it is not a rather expensive paper weight. 

The software will be caotic at first as I'm still in the process of learning python well. 

Initial software/programs:
1. voice_assistant - This will be a voice assistant based on the vosk voice recognition project, It uses a offline text to speech system to report back anwsers to questions you have. 
2. memory_system - based on a database (will need to look into this, as it will play a important role to the robot. Think like the ability to recall the last time you seen someone if asked) 
3. reading_module - This is a work in progress of a pipeline program to read pysical books and writing, This will unlock many use cases for the robot. 

Hardware specs:
1. Nividia Jetson TX2
2. Ufactory Lite 6 (6 axis robot arm, able to lift ~1kg)
3. ZED stereo vision camera
4. Respeaker v2.0 (Microphone)
5. 3x stepper motor drives
6. 1x Pi Pico, (controls the stepper drives, and other low level sensors)
7. 2x 30ah life batteries 

I suggest going over to the following website for more info on build and progress. https://hackaday.io/project/182694-sophie-robot
