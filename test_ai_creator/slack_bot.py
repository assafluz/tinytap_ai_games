import os
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import subprocess

import os, datetime
import requests
import json


# Set your Slack API token
slack_token = 'xoxb-2652831235-1561320230754-azo4XGopaUQzmo4rE5WWngi1'
channel_id = 'C05MRKCQPPF'  # Replace with your channel ID

client = WebClient(token=slack_token)


def send_message(text):
    try:
        response = client.chat_postMessage(channel=channel_id, text=text)
        return response['ts']  # Return the timestamp of the sent message
    except SlackApiError as e:
        print(f"Error sending message: {e.response['error']}")


def handle_command(command):
    if command == "run_test":
        subprocess.run(["python", "create_ai_game.py"], cwd=os.path.dirname(os.path.abspath(__file__)))
        send_message("Test script has been triggered and executed.")


if __name__ == "__main__":
    send_message("Slack integration script is online.")

    while True:
        try:
            events = client.conversations_history(channel=channel_id, limit=1)
            if events["ok"]:
                message_text = events["messages"][0]["text"]
                if "run test" in message_text.lower():
                    handle_command("run_test")
        except SlackApiError as e:
            print(f"Error getting messages: {e.response['error']}")

        # Sleep for a few seconds before checking for new messages
        time.sleep(5)
