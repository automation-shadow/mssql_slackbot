from slack_sdk.web import WebClient
from slack_sdk.errors import SlackApiError
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import os
from dotenv import load_dotenv
import pymssql
from prettytable import PrettyTable
# Import all the needed modules
load_dotenv()
# Load in all the environment variables
SLACK_BOT_TOKEN = os.environ['SLACK_BOT_TOKEN']
SLACK_APP_TOKEN = os.environ['SLACK_APP_TOKEN']
DB_SERVER = os.environ['DB_SERVER']
DB_DATABASE = os.environ['DB_DATABASE']
DB_USERNAME = os.environ['DB_USERNAME']
DB_PASSWORD = os.environ['DB_PASSWORD']

app = App(token=SLACK_BOT_TOKEN)

# Define the sql driver and connection to run on the database
def query_database(say, search_str1, search_str2):
    try:
        # Create a connection to the mssql server database
        conn = pymssql.connect(server=DB_SERVER, database=DB_DATABASE, user=DB_USERNAME, password=DB_PASSWORD)
        cursor = conn.cursor()

        # Execute a stored procedure with two parameters from the Slack user 
        cursor.execute("EXEC findskills @SearchStr1 = %s, @SearchStr2 = %s", (search_str1, search_str2))
        rows = cursor.fetchall()

        # Process the result and format it so it is pretty to read
        table = PrettyTable()
        table.field_names = ["Search String 1", "Search String 2", "People with those skills"]  # Update with your actual column names

        # Set the max width for each column
        table._max_width = {"Search String 1": 50, "Search String 2": 50, "People with those skills": 100}  # Update the width as needed

        # Response if the return set is empty
        if not rows:
            say(f"No results found for: {search_str1}, {search_str2}")
            return

        #⛧ Break up the list because it is too long
        rows_per_response = 50
        total_rows = len(rows)
        start_row = 0

        while start_row < total_rows:
            end_row = min(start_row + rows_per_response, total_rows)
            for row in rows[start_row:end_row]:
                # Add each row as a new row to table
                table.add_row([search_str1, search_str2] + list(row))  # Assuming the rows are tuples

            # Send the formatted table as a single response back to Slack
            say(f"Search Results (Rows {start_row + 1}-{end_row}):\n```\n{table}\n```")

            # Clear the table for the next set of rows for the next response
            table.clear_rows()

            start_row = end_row

    except Exception as e:
        print(f"Error connecting to the database: {e}")
        say(f"Error connecting to the database: {e}")
    finally:
        # Close the database connection
        conn.close()

def query_data_age(say):
    try:
        # Create a connection to the MSSQL server database
        conn = pymssql.connect(server=DB_SERVER, database=DB_DATABASE, user=DB_USERNAME, password=DB_PASSWORD)
        cursor = conn.cursor()

        # Execute the stored procedure with no parameters
        cursor.execute("EXEC data_age")
        rows = cursor.fetchall()

        # Process the result and format it so it is pretty to read
        table = PrettyTable()
        table.field_names = ["Updated Data", "Value"]

        # Set the max width for each column
        table._max_width = {"Updated Data": 50, "Value": 50}

        # Response if the return set is empty
        if not rows:
            say("No results found for the data_age stored procedure")
            return

        # Add each row as a new row to the table
        for row in rows:
            table.add_row(list(row))

        # Send the formatted table as a single response back to Slack
        say(f"Data Age Results:\n```\n{table}\n```")

    except Exception as e:
        print(f"Error connecting to the database: {e}")
        say(f"Error connecting to the database: {e}")
    finally:
        # Close the database connection
        conn.close()

def help_command(say):
    help_text = """
    :information_source: *Bot Help* :information_source:

    To use this bot, mention the bot and provide search parameters as follows:
    ```
    @Skillbot @SearchStr1 parameter1 @SearchStr2 parameter2
    ```

    Example:
    ```
    @Skillbot @SearchStr1 java @SearchStr2 python
    ```

    This will search for skills with 'java' and 'python'.
    If you do not have two search terms, just use the same one twice.

    For help or to give feedback, Please contact Winchell :winchell_help:.
    """
    say(help_text)

def hello_command(say):
    hello_text = """
    Hello there!
    """
    say(hello_text)

def emails_command(say, channel_id):
    try:
        client = WebClient(token=SLACK_BOT_TOKEN)
        
        # Retrieve all users, including deactivated ones
        result = client.users_list()

        # Process the result and format it as a table
        table = PrettyTable()
        table.field_names = ["User ID", "Team ID", "Display Name", "Real Name", "Phone", "Email", "Status"]

        # Set the max width for each column
        table._max_width = {"User ID": 20, "Team ID": 20, "Display Name": 20, "Real Name": 20, "Phone": 20, "Email": 40, "Status": 10}

        for user_info in result['members']:
            member_id = user_info.get('id', 'null')
            team_id = user_info.get('team_id', 'null')
            display_name = user_info.get('name', 'null')
            real_name = user_info.get('real_name', 'null')
            phone = user_info.get('profile', {}).get('phone', 'null')
            email = user_info.get('profile', {}).get('email', 'null')
            is_active = not user_info.get('deleted', True)

            table.add_row([member_id, team_id, display_name, real_name, phone, email, "Active" if is_active else "Deactivated"])

        # Send the formatted table as a single response back to Slack
        say(f"Emails in Channel (Channel ID: {channel_id}):\n```\n{table}\n```")

    except Exception as e:
        print(f"Error retrieving emails: {e}")
        say(f"Error retrieving emails: {e}")

def messages_command(say, client, channel_id, member_id):
    try:
        # Get the channel history
        history = client.conversations_history(channel=channel_id)
        
        # Filter messages by the specified member_id
        messages = [msg for msg in history['messages'] if msg.get('user') == member_id]
        
        if not messages:
            say(f"No messages found for member_id: {member_id}")
            return

        # Save messages to a text file with the name formatted as messages_{member_id}.txt
        filename = f"messages_{member_id}.txt"
        with open(filename, "w", encoding="utf-8") as file:
            for msg in messages:
                file.write(f"{msg['ts']}: {msg.get('text', 'No text')}\n")

        say(f"Messages saved to `{filename}` for member_id: {member_id}")

    except SlackApiError as e:
        print(f"Error fetching channel history: {e.response['error']}")
        say(f"Error fetching channel history: {e.response['error']}")
    except Exception as e:
        print(f"Error processing messages: {e}")
        say(f"Error processing messages: {e}")

@app.event("app_mention")
def mention_handler(ack, body, say):
    ack()

    text = body['event']['text']
    # Look at the text and execute a command
    if "!help" in text:
        help_command(say)
    elif "Hello" in text:
        hello_command(say)
    elif "!emails" in text:
        # Extract the channel_id from the message
        try:
            channel_id = text.split("!emails")[1].strip()
            emails_command(say, channel_id=channel_id)
        except ValueError:
            say("Invalid command format. Please provide the channel_id.")
    elif "!data" in text:
        say("Executing data_age stored procedure...")
        query_data_age(say)
    elif "!messages" in text:
        # Extract the channel_id and member_id from the message
        try:
            channel_id, member_id = text.split("!messages")[1].strip().split()
            messages_command(say, client, channel_id=channel_id, member_id=member_id)
        except ValueError:
            say("Invalid command format. Please provide both channel_id and member_id.")
    elif "@SearchStr1" in text:
        # Extract the search strings from the message
        search_strs = text.split("@SearchStr1")[1].strip().split("@SearchStr2")
        search_str1 = search_strs[0].strip()
        search_str2 = search_strs[1].strip()

        say(f"Searching for: {search_str1}, {search_str2}")
        # Call the function to query the database with the search strings
        query_database(say, search_str1, search_str2)
    else:
        say("Invalid command. Please use '!help' or provide search parameters.")

if __name__ == "__main__":
    client = WebClient(token=SLACK_BOT_TOKEN)
    handler = SocketModeHandler(app, SLACK_APP_TOKEN)
    handler.start()
