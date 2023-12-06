from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
import os
from dotenv import load_dotenv
import pymssql
from prettytable import PrettyTable

load_dotenv()

SLACK_BOT_TOKEN = os.environ['SLACK_BOT_TOKEN']
SLACK_APP_TOKEN = os.environ['SLACK_APP_TOKEN']
DB_SERVER = os.environ['DB_SERVER']
DB_DATABASE = os.environ['DB_DATABASE']
DB_USERNAME = os.environ['DB_USERNAME']
DB_PASSWORD = os.environ['DB_PASSWORD']

app = App(token=SLACK_BOT_TOKEN)

def query_database(say, search_str1, search_str2):
    try:
        # Establish a connection to the database
        conn = pymssql.connect(server=DB_SERVER, database=DB_DATABASE, user=DB_USERNAME, password=DB_PASSWORD)
        cursor = conn.cursor()

        # Example query with two parameters from Slack
        cursor.execute("EXEC findskills @SearchStr1 = %s, @SearchStr2 = %s", (search_str1, search_str2))
        rows = cursor.fetchall()

        # Process the result and format it as a table
        table = PrettyTable()
        table.field_names = ["Search String 1", "Search String 2", "People with those skills"]  # Replace with your actual column names

        # Set the max width for each column
        table._max_width = {"Search String 1": 50, "Search String 2": 50, "People with those skills": 100}  # Adjust the width as needed

        if not rows:
            say(f"No results found for: {search_str1}, {search_str2}")
            return

        rows_per_response = 50
        total_rows = len(rows)
        start_row = 0

        while start_row < total_rows:
            end_row = min(start_row + rows_per_response, total_rows)
            for row in rows[start_row:end_row]:
                # Add each row as a new row in the table
                table.add_row([search_str1, search_str2] + list(row))  # Assuming the rows are tuples

            # Send the formatted table as a single response
            say(f"Search Results (Rows {start_row + 1}-{end_row}):\n```\n{table}\n```")

            # Clear the table for the next set of rows
            table.clear_rows()

            start_row = end_row

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

    For help, contact Winchell :winchell_help: .
    """
    say(help_text)

def hello_command(say):
    hello_text = """
    Hello there!
    """
    say(hello_text)

@app.event("app_mention")
def mention_handler(ack, body, say):
    ack()

    text = body['event']['text']

    if "!help" in text:
        help_command(say)
    elif "Hello" in text:
        hello_command(say)
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
    handler = SocketModeHandler(app, SLACK_APP_TOKEN)
    handler.start()

