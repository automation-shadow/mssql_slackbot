### Slack setup and configuration

1. Using the Slack API page:
```sh
https://api.slack.com/apps
```
2. Create an App
3. Add your workspace
4. Add scopes for the bot:
```sh
app_mentions.read: This allows the bot to read the messages that mention our bot.
channels:join: This allows the bot to join channels.
chat:write: This allows the bot to send messages in a public channel.
```
5. Enable socketmode and add the follow scope:
```sh
connections:write
```
6. Give the token a name and generate your tokens
7. Enable Event subscriptions and add bot events:
```sh
app_mention
```
8. Grab the OAuth Access Token and the Bot User OAuth Access Tokens for your code

### PYTHON environment to run the bot on a linux host

1. Create a directory
2. execute: `python -m venv .venv`
3. execute: `source ./venv/bin/activate`
4. Create a .env files for all your parameters:
```sh
SLACK_BOT_TOKEN=
SLACK_APP_TOKEN=
DB_SERVER=
DB_DATABASE=
DB_USERNAME=
DB_PASSWORD=
```
5. Install all the pre-reqs for the bot:
```sh
pip3 install python-dotenv slack-sdk slack-bolt pymssql prettytable
```
