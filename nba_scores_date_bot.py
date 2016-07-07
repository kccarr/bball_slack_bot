from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd
import html5lib
import os
import time
from slackclient import SlackClient


# starterbot's ID as an environment variable
BOT_ID = os.environ.get("BOT_ID")

# constants
AT_BOT = "<@" + BOT_ID + ">:"
EXAMPLE_COMMAND = "score"

# instantiate Slack & Twilio clients
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))


def handle_command(command, channel):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """
    response = "Not sure what you mean. Use the *" + EXAMPLE_COMMAND + \
               "* command with a space a date in the MM/DD/YYYY format for Basketball Scores you want."
    if command.startswith(EXAMPLE_COMMAND):
    	str_date = str(command)
    	# simple testing then add regex function
	    date = str_date[:-10]
	    url = "http://stats.nba.com/scores/#!/{0}".format(date)

		# this is the html from the given url
		html = urlopen(url)
		soup = BeautifulSoup(html, 'html5lib')
		# recieving error saying None Type is not callable
		column_headings = [th.get_text() for th in soup.findall('tr').findall('th')]
		data_rows = soup.findall('tr')[2:]
		score_data = [[td.get_text() for td in data_rows[i].findall('td')] 
			for i in range(len(data_rows))]
        response = pd.DataFrame(score_data, columns=column_headings)
    slack_client.api_call("chat.postMessage", channel=channel,
                          text=response, as_user=True)


def parse_slack_output(slack_rtm_output):
    """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.
    """
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                # return text after the @ mention, whitespace removed
                return output['text'].split(AT_BOT)[1].strip().lower(), \
                       output['channel']
    return None, None


if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
    if slack_client.rtm_connect():
        print("StarterBot connected and running!")
        while True:
            command, channel = parse_slack_output(slack_client.rtm_read())
            if command and channel:
                handle_command(command, channel)
            time.sleep(READ_WEBSOCKET_DELAY)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")

