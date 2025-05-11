from flask import Flask, render_template, request, jsonify
import os, requests
import json
from dotenv import load_dotenv
import string
import nltk
from nltk.corpus import words, names
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize

load_dotenv()

app = Flask(__name__)

API_KEY = os.getenv('LASTFM_API_KEY')
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

lemmatizer = WordNetLemmatizer()
nltk.download('wordnet')
nltk.download('words')
nltk.download('names')
nltk.download('punkt')
english_vocab = set(words.words())
english_names = set(names.words())

def save_scrobbles(username, scrobbles):
	with open(f"data/{username}_all_scrobbles", 'w', encoding='utf-8') as f:
		json.dump(scrobbles, f)

def load_scrobbles(username):
	try:
		with open(f"data/{username}_all_scrobbles", 'r', encoding='utf-8') as f:
			return json.load(f)
	except FileNotFoundError:
		return None
	
def save_top1000(username, scrobbles):
	with open(f"data/{username}_top1000", 'w', encoding='utf-8') as f:
		json.dump(scrobbles, f)

def load_top1000(username):
	try:
		with open(f"data/{username}_top1000", 'r', encoding='utf-8') as f:
			return json.load(f)
	except FileNotFoundError:
		return None

def is_english_word(word):
    word_clean = word.lower().strip(string.punctuation)
    lemma = lemmatizer.lemmatize(word_clean)
    return lemma in english_vocab or word.capitalize() in english_names

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/scrobbles', methods=['POST'])
def get_all_scrobbles():	
	data = request.get_json()
	username = data.get("username")
	if not username:
		return jsonify({"error": "Username required"}), 400
	
	cached = load_scrobbles(username)
	if cached:
		return render_template("results.html", tracks = cached, username = username, content = "all scrobbles")

	seen = set()
	unique_tracks = []
	limit = 200
	page = 1

	while True:
		url = (
			"https://ws.audioscrobbler.com/2.0/"
			f"?method=user.getrecenttracks&user={username}"
			f"&api_key={API_KEY}&format=json&limit={limit}&page={page}"
		)

		try:
			r = requests.get(url)
			r.raise_for_status()
			data = r.json()

			tracks = data.get('recenttracks', {}).get('track', [])
			attr = data.get('recenttracks', {}).get('@attr', {})
			total_pages = int(attr.get('totalPages', 1))

			for track in tracks:
				name = track.get("name", "").strip().lower()
				artist = track.get("artist", {}).get("#text", "").strip().lower()

				if not name or not artist:
					continue

				key = (artist, name)
				if key not in seen:
					seen.add(key)
					unique_tracks.append(track)

			print(f"Fetched page {page}/{total_pages}")

			if page >= total_pages:
				break
			page += 1

		except requests.RequestException as e:
			return render_template("results.html", tracks=[], error=str(e))

	save_scrobbles(username, unique_tracks)
	return render_template("results.html", tracks = unique_tracks, username = username, content = "all scrobbles")

@app.route('/top1000', methods=['POST'])
def get_top1000():	
	data = request.get_json()
	username = data.get("username")
	if not username:
		return jsonify({"error": "Username required"}), 400
	
	cached = load_top1000(username)
	if cached:
		return render_template("results.html", tracks = cached, username = username, content = "top 1000 tracks")

	unique_tracks = []
	period = "overall"
	limit = 1000

	url = (
		"https://ws.audioscrobbler.com/2.0/"
		f"?method=user.gettoptracks&user={username}"
		f"&api_key={API_KEY}&format=json&limit={limit}&period={period}"
	)

	try:
		r = requests.get(url)
		r.raise_for_status()
		data = r.json()

		tracks = data.get('toptracks', {}).get('track', [])
		for track in tracks:
			unique_tracks.append(track)

	except requests.RequestException as e:
		return render_template("results.html", tracks=[], error=str(e))

	save_top1000(username, unique_tracks)
	return render_template("results.html", tracks = unique_tracks, username = username, content = "top 1000 tracks")

@app.route('/shortnsweet', methods=['POST'])
def get_shorter_than():
	data = request.get_json()
	username = data.get("username")
	durationMax = data.get("duration")
	dataset = data.get("dataset")

	if dataset == "all scrobbles" or dataset == "all scrobbles shorter than 2 minutes" or dataset == "all scrobbles not in English" or dataset == "all scrobbles with maximum 5 characters":
		unfiltered = load_scrobbles(username)
		filtered = []
		durations = []
		playcounts = []

		index = 0
		for track in unfiltered:
			print("checking track " + str(index) + " of " + str(len(unfiltered)))

			mbid = track.get("mbid", "")
			artist = track.get("artist", {}).get("#text", "")
			title = track.get("name", "")

			if id != '':
				url = (
					"https://ws.audioscrobbler.com/2.0/"
					f"?method=track.getInfo&api_key={API_KEY}"
					f"&mbid={mbid}&username={username}&format=json"
				)
			else:
				url = (
					"https://ws.audioscrobbler.com/2.0/"
					f"?method=track.getInfo&api_key={API_KEY}"
					f"&artist={artist}&track={title}&username={username}&format=json"
				)
			
			try:
				r = requests.get(url)
				r.raise_for_status()
				data = r.json()

				duration = int(data.get('track', {}).get('duration', '0')) // 1000
				print(title)
				print(duration)

				if duration < durationMax and duration > 0:
					durations.append(duration)
					filtered.append(track)

					playcount = data.get('track', {}).get('playcount', '0')
					playcounts.append(playcount)

			except requests.RequestException as e:
				return render_template("results.html", tracks=[], error=str(e))
			
			index += 1
		
		return render_template("results.html", tracks = filtered, username = username, content = "all scrobbles shorter than 2 minutes", durations = durations, playcounts = playcounts)
	
	if dataset == "top 1000 tracks" or dataset == "top tracks shorter than 2 minutes" or dataset == "top tracks not in English" or dataset == "top tracks with maximum 5 characters":
		unfiltered = load_top1000(username)
		filtered = []

		for track in unfiltered:
			duration = int(track.get("duration", "0"))

			if duration < durationMax and duration > 0:
				filtered.append(track)
		
		return render_template("results.html", tracks = filtered, username = username, content = "top tracks shorter than 2 minutes")
	
	else:
		return None
	
@app.route('/nonparliamo', methods=['POST'])
def get_songs_not_in():
	data = request.get_json()
	username = data.get("username")
	dataset = data.get("dataset")

	filtered = []

	if dataset == "all scrobbles" or dataset == "all scrobbles shorter than 2 minutes" or dataset == "all scrobbles not in English" or dataset == "all scrobbles with maximum 5 characters":
		unfiltered = load_scrobbles(username)

		for track in unfiltered:
			title = track.get("name", "")
			words_in_title = word_tokenize(title)
			print(words_in_title)

			if words_in_title and (sum(is_english_word(word) for word in words_in_title) / len(words_in_title) < 0.2):
				filtered.append(track)
			
		return render_template("results.html", tracks = filtered, username = username, content = "all scrobbles not in English")
	
	if dataset == "top 1000 tracks" or dataset == "top tracks shorter than 2 minutes" or dataset == "top tracks not in English" or dataset == "top tracks with maximum 5 characters":
		unfiltered = load_top1000(username)

		for track in unfiltered:
			title = track.get("name", "")
			words_in_title = word_tokenize(title)
			print(words_in_title)

			if words_in_title and (sum(is_english_word(word) for word in words_in_title) / len(words_in_title) < 0.2):
				filtered.append(track)
		
		return render_template("results.html", tracks = filtered, username = username, content = "top tracks not in English")
	
	else:
		return None

@app.route('/dontspeak', methods=['POST'])
def get_titles_under():
	data = request.get_json()
	maxChars = data.get("chars")
	username = data.get("username")
	dataset = data.get("dataset")

	filtered = []

	if dataset == "all scrobbles" or dataset == "all scrobbles shorter than 2 minutes" or dataset == "all scrobbles not in English" or dataset == "all scrobbles with maximum 5 characters":
		unfiltered = load_scrobbles(username)

		for track in unfiltered:
			title = track.get("name", "")

			if len(title.replace(" ", "")) <= maxChars:
				filtered.append(track)
			
		return render_template("results.html", tracks = filtered, username = username, content = "all scrobbles with maximum 5 characters")
	
	if dataset == "top 1000 tracks" or dataset == "top tracks shorter than 2 minutes" or dataset == "top tracks not in English" or dataset == "top tracks with maximum 5 characters":
		unfiltered = load_top1000(username)

		for track in unfiltered:
			title = track.get("name", "")
			
			if len(title.replace(" ", "")) <= maxChars:
				filtered.append(track)
		
		return render_template("results.html", tracks = filtered, username = username, content = "top tracks with maximum 5 characters")
	
	else:
		return None

if __name__ == '__main__':
	app.run(debug=True)