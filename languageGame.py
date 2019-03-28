from flask import Flask, render_template, request, redirect, url_for, jsonify
from googletrans import Translator, LANGUAGES, LANGCODES
import tweepy, re, random, nltk, spacy, json, unidecode
from spacy import displacy
from collections import Counter
from mtranslate import translate
import en_core_web_sm
import jieba
from wordfreq import top_n_list, iter_wordlist

app = Flask("myApp")

noneType = type(None)
translator = Translator()
nlp = en_core_web_sm.load()

common={"and":1,"or":1,"if":1,"the":1,"no":1,"on":1,"at":1,"it":1,"its":1,"are":1}

# Load twitter credentials from json file
with open("static/twitter_credentials.json", "r") as file:  
    creds = json.load(file)
# Load list of english words from json file
with open("static/words_dictionary.json","r") as file:
	word_list=json.load(file)
# Load list of top 10000 english words to be used to generate guesses
with open("static/modifiedTop10000asDict.txt","r") as file:
	top_word_list = json.load(file)

# Load list of languages for which word frequency is available
with open("static/langcodes_frequency.json","r") as file:
	langcodes_frequency = json.load(file)
# dictionary of language name as key and language code as value
langcodes_frequency_reverse = dict(map(reversed, langcodes_frequency.items()))
# Authenticate twitter credentials and create api object
auth = tweepy.OAuthHandler(creds['CONSUMER_KEY'],creds['CONSUMER_SECRET'])
auth.set_access_token(creds['ACCESS_TOKEN'],creds['ACCESS_SECRET'])
api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)


language_list = LANGUAGES.values()
language_frequency_list = langcodes_frequency.values()

# Function to translate given word into target language
def translated(word, dest_lang):
	translated = translate(word,dest_lang)
	if word != translated:
		return translated
	else: 
		return None

# Function to translate given word into target language
def translatedEnglish(word, dest_lang):
	translated = translate(word,dest_lang, "auto")
	if word != translated:
		return translated
	else: 
		return None
# Function to remove words that cannot be translated
def findNontranslatable(proper_tweet,dest_lang):
	translatable=[]
	for word in proper_tweet:
		translated = translate(word,dest_lang)
		if word != translated:
			translatable.append(word)
	return translatable

def langCode(dest_lang_full):
	try:
		dest_lang = LANGCODES[dest_lang_full.lower()]
	except KeyError:
		print("that language name was not recognised \n please try again")
		dest_lang_full = input("enter the language you want to practice \n")
		dest_lang = langCode(dest_lang_full)
	return (dest_lang, dest_lang_full)

# Function to remove proper nouns from tweet word list
def findName(tweet_text,proper_tweet):
	doc = nlp(tweet_text)
	for word in doc.ents:
		if word.label_ in ["PERSON","ORG","GPE"]:
			for w in word.text.split():
				if w.lower() in proper_tweet:
					proper_tweet.remove(w.lower())
	return proper_tweet

# Function to search for latest tweet
def findTweet(search_hashtag,min_words,max_id= None):
	search_number=1
	iter=0
	proper_tweet=[]
	tweet_text=""
	if type(max_id) == int:
		search_result = tweepy.Cursor(api.search, tweet_mode="extended", lang="en", max_id=max_id, q=search_hashtag+"-filter:retweets").items(search_number)
	else:
		search_result = tweepy.Cursor(api.search, tweet_mode="extended", lang="en", q=search_hashtag+"-filter:retweets").items(search_number)
	for tweet in search_result:
		tweet_text_original=""+tweet.full_text
		max_id=tweet.id
		tweetID=tweet.id
		iter+=1
	if iter==0:
		return None
	else:
		tweet_text=' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet_text_original).split())
		for word in tweet_text.split():
			if word.lower() in word_list and len(word)>2 and word.lower() not in common and word.lower() not in proper_tweet:
				proper_tweet.append(word.lower())
		proper_tweet= findName(tweet_text,proper_tweet)
		proper_tweet = findNontranslatable(proper_tweet, dest_lang)
		sorted_proper_tweet=sorted(proper_tweet, key=len, reverse=True)
		if len(sorted_proper_tweet) >= min_words:
			return (sorted_proper_tweet,tweet_text_original, tweet_text, tweetID)
		else:
			return max_id-1

# Function to find latest tweet that meets all criteria
def findTheRightTweet(search_hashtag,min_words,max_ID = None):
	#return type is tuple([list of gameWords],"tweet_original","proper_tweet_text")
	outPut = findTweet(search_hashtag,min_words,max_id = max_ID)
	while True:
		if type(outPut)==int:
			outPut = findTheRightTweet(search_hashtag,min_words, max_ID = outPut)
		elif type(outPut)==tuple:
			right_tweet = outPut
			return right_tweet
		else:
			outPut="notFound"
			return outPut

# Function to generate list of guesses
def guessGenerator(currentWord,dest_lang, number_of_guesses):
	guess = {}
	output = translated(currentWord, dest_lang)
	guess[output]=(1,currentWord)
	while len(guess)<number_of_guesses:
		randomWord = random.choice(list(top_word_list.keys()))
		if randomWord not in guess:
			output = translated(randomWord,dest_lang)
			if type(output) != noneType:
				guess[output.lower()]=(0,randomWord)
	guessList = list(guess.items())
	random.shuffle(guessList)
	guess = dict(guessList)
	return guess

dest_lang = 0
search_hashtag = 0
min_words = 0
dest_lang_full = 0
number_of_guesses = 0
points = 0
list_game_words = 0
words_played = 0
right_tweet = 0
guess = 0

@app.route("/welcome", methods=["GET","POST"])
def welcome():
	return render_template("indexExt.html")

@app.route("/about", methods=["GET", "POST"])
def about():
	return render_template("about.html")

@app.route("/contact", methods=["GET", "POST"])
def contact():
	return render_template("contact.html")

@app.route("/languagestatistics", methods=["GET","POST"])
def languagestatistics():
	return render_template("languagestatistics.html", language_frequency_list=language_frequency_list)

def englishChecker(word_translated):
	listTranslated = word_translated.split(" ")
	for word in listTranslated:
		if word.lower() not in word_list:
			return None
	return "ok"

def frequencyFunction(language, min_word_length, number_frequency):
	lang = langcodes_frequency_reverse[language]
	iterFrequency = iter_wordlist(lang, wordlist = "best")
	frequency_output = []
	frequency_output_english = []
	i = 0
	for word in iterFrequency:
		if len(word)>= int(min_word_length) and "0" not in word and word not in word_list:
			frequency_output.append(word)
			word_translated = translatedEnglish(word, "en")
			if type(word_translated) != noneType:
				word_translated_checked = englishChecker(word_translated)
				if type(word_translated_checked) != noneType:
					frequency_output_english.append(word_translated)
					i += 1
		if i == int(number_frequency):
			return (frequency_output, frequency_output_english)

@app.route("/frequency", methods=["GET","POST"])
def frequency():
	language = request.form.get("language")
	min_word_length = request.form.get("min_word_length")
	number_frequency = request.form.get("number_frequency")
	output = frequencyFunction(language, min_word_length, number_frequency)
	frequency_output = output[0]
	frequency_output_english = output[1]
	return render_template("languagestatistics.html", language_frequency_list=language_frequency_list, frequency_output=frequency_output, frequency_output_english=frequency_output_english, language=language, min_word_length=min_word_length, number_frequency=number_frequency)

@app.route("/twitterlanguagegame", methods=["GET","POST"])
def twitterlanguagegame():
	if right_tweet=="notFound":
		hashtagError=True
		return render_template("twitterlanguagegame.html",language_list=language_list, hashtagError=hashtagError)
	else:
		return render_template("twitterlanguagegame.html",language_list=language_list)

@app.route("/languageGame", methods=["POST"])
def twitterGet():
	global dest_lang
	global search_hashtag
	global min_words
	global dest_lang_full
	global number_of_guesses
	global points
	global list_game_words
	global words_played
	global right_tweet
	global guess
	search_hashtag = "#"+request.form.get("hashtag")
	dest_lang_full = request.form.get("language")
	min_words = int(request.form.get("min_words"))
	langCodeOutput = langCode(dest_lang_full)
	dest_lang = langCodeOutput[0]
	dest_lang_full = langCodeOutput[1]
	number_of_guesses = 4
	right_tweet = findTheRightTweet(search_hashtag, min_words)
	if right_tweet=="notFound":
		return redirect(url_for('twitterlanguagegame'))
	list_game_words = right_tweet[0]
	points = 0
	words_played = 0
	return redirect(url_for('trial'))

#@app.route("/")
@app.route("/langGame", methods=["GET","POST"])
def trial():
	global guess
	global word
	global guess_reverse
	if words_played > len(list_game_words)-1 or words_played == min_words:
		score = points/words_played
		urlTweet="https://publish.twitter.com/oembed?url=https://twitter.com/twitter/status/"+str(right_tweet[3])
		tweetID=right_tweet[3]
		return render_template("twitterlanguagegame.html", language_list=language_list, score=score, tweet_text_original=right_tweet[1], urlTweet=urlTweet, tweetID=tweetID)
	word = list_game_words[words_played]
	guess = guessGenerator(word,dest_lang, number_of_guesses)
	guess_reverse = dict(map(reversed,guess.items()))
	guess_list = [*guess.keys()]
	return render_template("twitterlanguagegame.html", search_hashtag=search_hashtag, dest_lang_full=dest_lang_full, language_list=language_list, word=word, guess=guess, guess_reverse=guess_reverse, points=points, words_played=words_played)
	
@app.route("/langGameAnswer", methods=["GET","POST"])
def answerThing():
	global words_played
	global points
	answer = request.form["answer"]
	words_played += 1
	if guess[answer][0]==1:
		points+=1
	return render_template("twitterlanguagegame.html", answer=answer, search_hashtag=search_hashtag, dest_lang_full=dest_lang_full, language_list=language_list, word=word, guess=guess, guess_reverse=guess_reverse, points=points, words_played=words_played)
	
@app.route("/tweet", methods=["GET","POST"])
def tweet():
	tweetID=1103446762688339969
	urlTweet="https://publish.twitter.com/oembed?url=https://twitter.com/twitter/status/"+str(tweetID)
	return render_template("tweetTrial.html", urlTweet=urlTweet, tweetID=tweetID)
		
app.run(debug=True)