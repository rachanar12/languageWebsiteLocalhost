# languageWebsiteLocalhost
Here is the updated languageWebsite created by me for the codeFirstGirls course competition

This is the github for the languageWebsite web app created using python flask. The features of the website are:

- a welcome page that has hover brain image that tells you about benefits of being bi or multilingual
- a language statistics page where you can find out some interesting facts. 
- a form on the language statistics page that lets you find the highest frequency words in one of 27 languages. You can choose the minimum number of letters that a word should have. 
The word frequencies are being pulled from the wordfreq package that combines data from several corpus. 
- a twitter language game page where you can pick a hashtag and practice language and number of words to practice. Then you have to translate several words and at the end you can see the latest tweet related to the hashtag you selected.
This uses the tweepy module to pull the latest tweet and googletrans package to do the translation. 

This website is also hosted on heroku at: http://language-website.herokuapp.com/
however, I keep getting internal server error for the twitter language game page however the error goes away if you refresh a few times and the game carries on. I tried debugging it for hours but cant find the issue. 

The website runs on local host perfectly though. 

I am using my twitter developer credentials to use with tweepy. However, that file is in .gitignore
if you clone this repository, you will need to create a twitter_credentials.json file with your twitter consumer and access secret code. 
