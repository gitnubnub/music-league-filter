# 🎵 Music League Filter

A simple Flask web app for filtering songs from your Last.fm profile data, tailored specifically for upcoming rounds in Elliot Roberts Discord Music League. You need python installed on your computer to run this.


## 🚀 Current features

- 🎧 Supports **top 1000 tracks** and **all scrobbles (without multiples)** from your Last.fm profile.
- ⏱️ **Songs shorter than 2 minutes (ROUND 2)**: Checks durations, unfortunately a lot of tracks don't have data for this on Last.fm (especially when coming from all scrobbles, where it must be retrieved per individual song).
- 🌍 **Songs not in English (ROUND 3)**: Checks titles for English words and eliminates them from the list, but it typically doesn't recognize geographic or non-typical names. As such, in this case, songs that don't count for this category can still show up. Use with common sense and/or a lyrics website.
- 🔠 **Songs with 5 or less characters (ROUND 5)**: The least complicated, defined as in the round description and works well.


## 🔧 Setup Instructions

### 1. Clone the repository and navigate into it
In command line, go to the location where you want to save this project and run:
```bash
git clone https://github.com/yourusername/music-league-filter.git
cd music-league-filter
```
### 2. Set up your .env file
You will need a Last.fm API key (you can request it [here](https://www.last.fm/api/account/create)). Since this is intended for running locally, you can use http://localhost for the homepage and callback URLs. When you get your API key, create a `.env` file in the root folder and copy and paste it in there like this:
```ini
API_KEY=your_api_key_here
```
### 3. Install the required packages
In the root folder of the project run:
```bash
pip install -r requirements.txt
```
### 4. Run the server
In the root folder of the project run:
```bash
python app.py
```
### 5. Open the app in your browser
Navigate to the localhost address that your app is running on. If you're not sure what port it's using, you can check it in the terminal where you started the server.


## 💡 Disclaimers and practical tips

This is my first time sharing something I coded outside of university and it's far from perfect. I've decided to focus on Last.fm for a start, because it doesn't require logging in for access to this type of data. I've also put aesthetics on the side, the css is very basic but might get upgraded in the future.

Also planned are filters for other upcoming rounds (watch this space!) and *maybe* integration of streaming platforms (I guess Spotify would be handy, since Music League uses it), but that depends on the amount of my free time and ability to figure out the hows of their APIs.

The most important thing to keep in mind if you'll be using this is that it is ***slow***. As a rule of thumb the top 1000 tracks list and filtering works relatively quick, whereas the all scrobbles side can test your patience, especially when it comes to the duration filter.

For reference I had 177 pages of scrobbles (7784 songs) and it took about 4 minutes to retrieve them and a whopping 25 minutes to check their durations. If your numbers are similar or higher, you might wanna occupy yourself during that time XD. Things like internet speed will also affect the time it will take.

To avoid waiting every time you want to check something both lists get **saved locally on your device** after you first request them. They can be found in the `data` folder. If you'd like those lists to update with more recent data, you should first delete them manually, so that they can re-generate.

Also note that the list of songs under 2 minutes **doesn't get saved locally**. When checking all scrobbles that is the longest process (although based on testing seemingly yields the least results due to lacking data), so you might want to take a screenshot before exiting (as mentioned, it's not a long list anyway 😉).

For the longer processes, there's also print outs in the terminal so you can follow the progress and estimate how long it might take.

If anyone decides to try this, I just hope you won't hate me, the developer, by the end. Finally, if you have any questions, problems or suggestions, feel free to contact me via Discord (@urskaisnotrunning). :)
