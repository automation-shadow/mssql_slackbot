** Slack setup and configuration ** 
Using the Slack API page:
https://api.slack.com/apps
Create an App
Add your workspace
Add scopes for the bot:
-- app_mentions.read: This allows the bot to read the messages that mention our bot.
-- channels:join: This allows the bot to join channels.
-- chat:write: This allows the bot to send messages in a public channel.
Enable socketmode and add the follow scope:
-- connections:write
Give the token a name and generate your tokens
Enable Event subscriptions and add bot events:
-- app_mention
Grab the OAuth Access Token and the Bot User OAuth Access Tokens for your code

** PYTHON3 environment to run the bot on a linux host ** 
Create a directory
execute: python3 -m venv .venv
execute: source ./venv/bin/activate
Create a .env files for all your parameters:
-- SLACK_BOT_TOKEN=
-- SLACK_APP_TOKEN=
-- DB_SERVER=
-- DB_DATABASE=
-- DB_USERNAME=
-- DB_PASSWORD=
Install all the pre-reqs for the bot:
-- pip3 install python-dotenv slack-sdk slack-bolt pymssql prettytable
