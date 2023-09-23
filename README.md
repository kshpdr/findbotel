# findbotel - find a journey of your dream

Bot is currently disabled due to the privacy concerns since the challenge is already over.

![](https://raw.githubusercontent.com/kshpdr/findbotel/main/media/findbotel_word.png "Logo findbotel")

This is a coding project made for a [Check24 coding challenge](https://github.com/check24-scholarships/holiday-challenge) that I've been writting for the last two week
of August in some gaps between my exams at the university. This bot is written in python, database is hosted on AWS RDS service (hopefully, they won't 
charge me too much) and a bot itself is deployed on a Heroku platform. For the libraries, I have used psycopg for the databse connection, flask for the server 
implementation and pyTelegramBotAPI to make use of Telegram Bot API.

You can try it out online at https://t.me/findbotelbot

## What was implemented

- A basic search of a journey for given dates, places and amount of people
- A hotel view that is available after a basic search under each found hotel
- A pagination to navigate through list of airports and all available offers (that was harsh)
- Payment option is included (unfortunately can't charge money from you but it makes you believe you pay)
- An option to check a location of each hotel
- Fast search engine: After deployment of dataset (I haven't even enough space on my computer to download it first) I've started to experiment with the
queries and found out that their execution is extremely slow - 104.24 seconds. After some optimization steps, such as correct data formating, indexing the table with a btree index and proper use of SQL operators I've managed to decrease
the execution time to 0.0025 seconds, which was fast enough for my purposes. As an idea, I want to implement asynchronous queries to start the search even 
before receiving all of data but til now I hadn't much time to that.

![](https://media.giphy.com/media/Baj94CdIEzwUXSYqsC/giphy.gif)
![](https://media.giphy.com/media/KCLaSBsgqNZ95EFMoW/giphy.gif)
