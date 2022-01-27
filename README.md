# SpellbreakLobbyScanner
Get information about your Spellbreak lobby - the region, port number, the amount of players, their names and hidden ranks! The Twitch bot prints them into your Twitch chat. Now includes an OBS overlay to display the information directly on your stream. It reads all the information from your g3 logs.

The original idea for this is by th_mrow. You can find them here:

https://www.twitch.tv/th_mrow

https://github.com/thbl088/mrow_twitch_scripts

## How to setup

### Prerequisites
1. Create a twitch account for the bot if you don't have one yet
2. Install : https://streamlabs.com/chatbot
3. Install : Python 2.7.13 (you can find it here: https://github.com/AnkhHeart/Streamlabs-Chatbot-Python-Boilerplate/wiki)
4. In Streamlabs Chatbot, under the Scripts tab, click on the settings icon in the top right, and find the Python 2.7.13 installation directory and select the Lib folder (default at C:\Python27\Lib)

![Streamlabs_Chatbot_S0JZI5dtbE](https://user-images.githubusercontent.com/6078092/151444037-42baaa01-1bde-4b75-81bc-d5225ff98907.png)

### Install the bot
1. Download the latest release as a ZIP folder from here: https://github.com/Almie/SpellbreakLobbyScanner/releases
2. In Streamlabs Chatbot, under the `Scripts` tab, click on the import icon and locate the ZIP folder you downloaded.
3. Check the `Enabled` checkbox to start the script.

![Streamlabs_Chatbot_lHYXdOq2XP](https://user-images.githubusercontent.com/6078092/151443975-494ecfba-fb37-4445-a707-19ad230c8fdd.png)

### Setup the OBS overlay
1. In Streamlabs Chatbot, under the `Scripts` tab, right-click on the SpellbreakLobbyScanner script and choose the "Insert API Key" option.
2. Then right-click it again and choose "Open Script Folder". Copy the path to this folder, you will need it later. It should be something like `C:\Users\<Your_Name>\AppData\Roaming\Streamlabs\Streamlabs Chatbot\Services\Scripts\SpellbreakLobbyScanner`.
![Streamlabs_Chatbot_UKJttXWWqX](https://user-images.githubusercontent.com/6078092/151444972-ed770de5-0418-4bd4-af11-08b38a5bcc98.png)

3. In your Streamlabs OBS/OBS Studio add a new Browser Source to your scene.
4. Turn on the `Local file` checkbox.
5. For the local file, navigate to the script folder you copied in step 2 and choose the `overlay.html` file.
6. Set the width and height to whatever you want. I recommend using maximum width (in my case 1920) and height of around 50 or 75, but you can choose any value based on preference.
7. Delete everything from the `Custom CSS` field.
8. (Optional) Check `Shutdown source when not visible` off. This means you won't see a "successfully connected" notification every time you switch scenes. However, if you need to manually refresh the overlay during your stream, you will have to open these settings again and press the `Refresh cache of current page`.
9. Press Done.

![Streamlabs_OBS_kM3QQXgnnM](https://user-images.githubusercontent.com/6078092/151447048-7030eff2-f6d6-4770-9068-ab9f59fe23a8.png)

## Troubleshooting

### My overlay says "Connection to chatbot not established."
1. Make sure Streamlabs Chatbot is running.
2. Make sure you haven't skipped the "Insert API Key" option from Step 1 of the OBS overlay set up. Check if `API_Key.js` exists in your script folder.
3. Press `Refresh the cache of current page` in the Browser source settings.
