import praw
import re
import json
from datetime import datetime


class LinuxHelperBot:
    def __init__(self, bot_name):
        # Bot name MUST be specified and set up in praw.ini
        self._bot = praw.Reddit(bot_name)
        self._json_filename = "config.json"

        try:
            with open(self._json_filename, "r") as posts_file:
                self._json_data = json.load(posts_file)
                self._previous_posts = self._json_data["Post_IDs"]
        except FileNotFoundError:
            self._json_data = {}
            self._previous_posts = []

        with open("text_values.json", "r") as values:
            self._text_values_json = json.load(values)
            self._text_values = self._text_values_json["text_values"]

    def write_to_json(self):
        """
        Writes current value of previous posts to json file
        """
        self._json_data["Post_IDs"] = self._previous_posts
        with open(self._json_filename, "w") as config:
            json.dump(self._json_data, config)

    def read_subreddit(self, subreddit, mode="hot", search_limit=5):
        """
        Prints up to the search limit of posts in a subreddit, sorted by hot or new (mode)
        """
        sub = self._bot.subreddit(subreddit)
        if mode == "hot":
            post_list = sub.hot(limit=search_limit)
        elif mode == "new":
            post_list = sub.new(limit=search_limit)
        else:
            return False
        for post in post_list:
            print("========================================")
            print("Title: ", post.title)
            print("Text:  ", post.selftext)
            print("Score: ", post.score)
            print("========================================\n")

    def kali_post_cleanse(self, mode="new", search_limit=5):
        """
        This uses a dictionary [stored in text_values.json] to rate a post between 1-10 on
        the likelihood that it is a generic Linux question. It then gives a helpful reply directing
        the poster to better resources.
        """
        sub = self._bot.subreddit("Kalilinux")
        if mode == "hot":
            post_list = sub.hot(limit=search_limit)
        elif mode == "new":
            post_list = sub.new(limit=search_limit)
        else:
            return False

        for post in post_list:
            if post.id not in self._previous_posts:
                value = 0
                for word in self._text_values:
                    if word.lower() in (post.title.lower() + post.selftext.lower()):
                        value += self._text_values[word]
                    if value >= 10:
                        print(f"{post.title} has a score of {value}")
                        try:
                            the_reply = f"""
Hello {post.author},

If you are having a generic Linux or networking issue (configuring adapters, booting, VMs, using various tools, etc.)
you'll have better luck asking a question in one of the following subreddits:

- r/linuxquestions
- r/linux4noobs
- r/techsupport

Check the sidebar for more information. Before posting a question in these subreddits, see if you can make any progress
by Googling the *precise* issues and/or errors you are having. Please consider removing your submission if you believe
it better belongs in another subreddit.

Kali Linux isn't the best choice for learning the basics of GNU/Linux. Other distros are far more beginner friendly
like Pop!_OS (r/pop_os), Linux Mint (r/linuxmint), and Ubuntu (r/Ubuntu).

[ This message was sent automatically, if sent in error, please disregard. PM for feedback :) ]                 
"""
                            post.reply(the_reply)
                            print("Bot replying to: ", post.title)

                            self._previous_posts.append(post.id)
                            print("Script Successful")

                            with open("log.txt", "a") as log:
                                now = datetime.now()
                                time = now.strftime("%d/%m/%Y %H:%M:%S")
                                log.write("=========================\n")
                                log.write("Bot Action Successful!\n")
                                log.write(time + "\n")
                                log.write(f"Script wrote to post: {post.title}\n")
                                log.write("=========================\n\n")
                                print("See log for details.")

                            self.write_to_json()
                            return "Function Successful."

                        except Exception as error:
                            print("Bot Failed!")
                            print(error)
                            with open("log.txt", "a") as log:
                                now = datetime.now()
                                time = now.strftime("%d/%m/%Y %H:%M:%S")
                                log.write("=========================\n")
                                log.write("Bot Action Failed!\n")
                                log.write(time + "\n")
                                log.write("Error Message: " + str(error) + "\n")
                                log.write("=========================\n\n")
                                print("See log for details.")
                            self.write_to_json()
                            return False
        print("No results found.")
        with open("log.txt", "a") as log:
            now = datetime.now()
            time = now.strftime("%d/%m/%Y %H:%M:%S")
            log.write("=========================\n")
            log.write("Bot Didn't Find a Match\n")
            log.write(time + "\n")
            log.write(f"No posts reached the 10 point threshold found.\n")
            log.write("=========================\n\n")
            print("See log for details.")
        self.write_to_json()

    def find_and_reply(self, subreddit, search_text, reply_text, mode="hot", search_limit=5):
        """
        This finds a post in a subreddit, and replies.
        This will search a post title and post text for matches.
        "subreddit": The subreddit we are searching
        "search_text": what we will pass into "re.search()"
        "reply_text": what the bot will reply to the found post
        "mode": sort by new or hot
        "search_limit": number of posts to load at a time
        """
        sub = self._bot.subreddit(subreddit)
        if mode == "hot":
            post_list = sub.hot(limit=search_limit)
        elif mode == "new":
            post_list = sub.new(limit=search_limit)
        else:
            return False
        for post in post_list:
            if post.id not in self._previous_posts:
                if re.search(search_text, post.title + post.selftext, re.IGNORECASE):
                    try:
                        post.reply(reply_text)
                        print("Bot replying to: ", post.title)

                        self._previous_posts.append(post.id)
                        print("Script Successful")

                        with open("log.txt", "a") as log:
                            now = datetime.now()
                            time = now.strftime("%d/%m/%Y %H:%M:%S")
                            log.write("=========================\n")
                            log.write("Bot Action Successful!\n")
                            log.write(time + "\n")
                            log.write(f"Script wrote to post: {post.title}\n")
                            log.write("=========================\n\n")
                            print("See log for details.")

                        self.write_to_json()
                        return "Function Successful."

                    except Exception as error:
                        print("Bot Failed!")
                        print(error)
                        with open("log.txt", "a") as log:
                            now = datetime.now()
                            time = now.strftime("%d/%m/%Y %H:%M:%S")
                            log.write("=========================\n")
                            log.write("Bot Action Failed!\n")
                            log.write(time + "\n")
                            log.write("Error Message: " + str(error) + "\n")
                            log.write("=========================\n\n")
                            print("See log for details.")
                        self.write_to_json()
                        return False
        print("No results found.")
        with open("log.txt", "a") as log:
            now = datetime.now()
            time = now.strftime("%d/%m/%Y %H:%M:%S")
            log.write("=========================\n")
            log.write("Bot Didn't Find a Match\n")
            log.write(time + "\n")
            log.write(f"No posts matching \"{search_text}\" found.\n")
            log.write("=========================\n\n")
            print("See log for details.")
        self.write_to_json()


def main():
    bot = LinuxHelperBot("communityKaliBot")
    bot.kali_post_cleanse("new", 10)


if __name__ == "__main__":
    main()
