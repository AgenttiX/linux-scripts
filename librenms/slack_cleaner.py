"""
A script for cleaning LibreNMS spam from Slack channel history
"""

import os.path

from slack_cleaner2 import SlackCleaner
from slack_cleaner2.model import SlackChannel, SlackUser


class Slack(SlackCleaner):
    def get_channel(self, name: str) -> SlackChannel:
        return next((ch for ch in self.conversations if ch.name == name))

    def get_user(self, key: str) -> SlackUser:
        return next((user for user in self.users if key in (user.id, user.name)))


def main():
    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    with open(os.path.join(repo_root, "keys", "slack-cleaner.txt")) as file:
        key = file.readline()

    print("Connecting")
    slack = Slack(key)

    print("Users:")
    print(slack.users)
    print("Channels:")
    print(slack.conversations)

    # user = slack.get_user("librenms")
    channel = slack.get_channel("server")

    deletable = [
        "Device Down! Due to no ICMP response",
        "Ping Latency",
        "recovered from Service up/down",
        "Sensor over limit - Check Device",
        "Service up/down",
        "SNMP not responding on Device",
    ]

    for msg in channel.msgs():
        if msg.bot and not msg.user and "attachments" in msg.json:
            for attachment in msg.json["attachments"]:
                if "fallback" in attachment:
                    fallback = attachment["fallback"]
                    if any(text in fallback for text in deletable):
                        print(fallback)
                        msg.delete()
                        # Delete each message only once
                        break


if __name__ == "__main__":
    main()
