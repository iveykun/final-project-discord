# final-project-discord
final project

you will need to make a discord bot and get its token on the official discord development page. You also need to create a file named "birthdayFile.txt" 

Optional: enable dotenv and put the token inside that .env file

dependencies: too many 

How to use:

It is complicated to set up, i can provide a video of me explaining all the different functions if you want.

First you need to go to discord developer portal and make an account, after which you will have to make a new "app" as well as a new "bot" user. Name it however you wish; mine is called Leafeon. The most important part is to obtain a "token" which is a type of license for the bot to be able to connect to discord servers. 

Then you have to replace the token in the code (bot.run(token)) with the token you obtained. Token is like a ID for a bot. 

On your PC, make sure to download discord.py[voice] as well as asyncio, FFmpeg, youtube-dl, as well as any dependencies. I can't keep track of everything I need, so you will unfortunaltely have to read the errors and install any missing libraries.

If everything works, create a file named birthdayFile.txt and put it in the same folder as the bot file.

To run the bot, in your command prompt after doing cd (path/to/file/bot.py) you should run python3 bot.py (i named my file main.py but choose whatever you like)

A common problem with this program is indentations (especially if you planned on using raspberry pi to run it like me) because nano is so strict with indents. As of may 24 2020 this bot is only confirmed to be working on windows, I have written another basic version (that only does birthday announcing) that runs on linux and raspi and I will provide if you ask for it.

The basic version is confirmed to be working on linux, windows, as well as a web server such as AWS and heroku.

Commands:

ping: returns pong! in the chat. Used to test if the bot is online
help: returns a list of everything the bot does as well as the time it announces birthdays.
date: returns the date in UTC
time: returns the time in UTC
happy: sends Happy Birthday! in the chat
praise: sends the number of times the bot has been congratulated in the chat
good: thanks the user
setbday MMDD: set the bday for the user in the format MMDD
join: joins the same voice channel as the user
play (url): plays the song to a url. Works with youtube and certain other websites.
loop: loop current queue
queue: shows the current queue of songs to be played
stop: stops the song and clears the queue
pause: pause the music
resume: resumes the music
volume (0-100): sets volume between 0 and 100


I have disabled skipping songs as it was causing some problems.

BOT USAGE
You can change the prefix of the bot in one of the last lines of the code. Default is ;
Make sure the bot is online with [prefix]ping

After that, make sure you are connected to a voice channel and run ;join
and after that you can run ;play (any youtube url)
if you do not join before hand it will join automatically.

setbday works by taking the username (like mine is ivey-kun#2275) which is unique for every discord user, and then saves it into a file with their birthday like january 2nd would be 0102. The bot checks the first 4 characters of each line in the file and then compares it with today's date. If there is a match, the function birthday() will send a birthday wish in the chat. You have to change the chat ID for every different server, in this code it is set to my personal test server. 

if the person has already set his birthday, the bot will simply recall the bday and will not set another instance. Howevwre, if they made a mistake, you will have to go in the birthdayFile.txt and remove it manually because using w+ in my program erases all the birthdays. I have resorted to using a+ to avoid that.

The bot creates a list off that file and reads them one by one to check if there is a birthday today. I am not sure why I implemented this method but I think it's because at first raspberry pi didn't let me open 2 files at the same time, or something, so I resorted to an internal list
