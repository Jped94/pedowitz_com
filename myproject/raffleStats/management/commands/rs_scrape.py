#!/usr/bin/env python3
import praw
import pandas as pd
import datetime as dt
import pprint
import re
import sys
from . import rs_config
from datetime import datetime
from django.core.management.base import BaseCommand, CommandError
from django.db.models import F
from raffleStats.models import (Raffle, SpotCount)


class Command(BaseCommand):
    help = "Scrapes info from watchuraffle"


    def scrape_wur(self):

        self.write_to_status_log("Starting scrape ")

        #GRAB DATA FROM REDDIT
        #
        #
        #

        reddit = praw.Reddit(client_id=rs_config.c_client_id, \
                             client_secret=rs_config.c_client_secret, \
                             user_agent=rs_config.c_user_agent, \
                             username=rs_config.c_username, \
                             password=rs_config.c_password)

        subreddit = reddit.subreddit('watchuraffle')
        newest = subreddit.new(limit=50)

        # ITERATE THROUGH POSTS
        #
        #
        #

        num_records_added = 0

        for post in newest:
            if (post.link_flair_text == "Complete"):

                #initialize variables
                vpost_id = None
                vtitle = None
                vnum_spots = None
                vprice_per_spot = None
                vwinning_spot = None
                vnum_spots_for_winner = None
                vdatetime_posted = None
                vdatetime_completed = None
                vduration_hours = None
                vtier = None

                vspot_histogram = None

                vpost_id = post.id
                vtier = self.get_raffle_tier(post)
                vtitle = post.title
                vprice_per_spot = -1 #unknown how to do this yet

                win_comment = self.get_win_comment(post)
                if not win_comment:
                    continue
                vwinning_spot = self.get_win_number(post, win_comment)

                if vwinning_spot == -1:
                    continue
                else:
                    spot_results = self.build_histogram(post.selftext, vwinning_spot, post)
                    if spot_results["winner_num_spots"] == None:
                        continue
                    else:
                        vnum_spots_for_winner = spot_results["winner_num_spots"]
                        vnum_spots = spot_results["num_spots"]
                        vspot_histogram = spot_results["spot_counts"]

                vdatetime_posted = self.get_raffle_start_time(post)
                vdatetime_completed = self.get_raffle_end_time(post, win_comment)
                timediff = vdatetime_completed - vdatetime_posted
                vduration_hours = round(timediff.seconds/3600, 2)


                # INSERT RAFFLE INTO DB
                #
                #
                #

                if(Raffle.objects.filter(post_id = vpost_id).exists() == False):
                    newRaffle = Raffle(post_id = vpost_id, \
                                        title = vtitle, \
                                        num_spots = vnum_spots, \
                                        price_per_spot = vprice_per_spot, \
                                        winning_spot = vwinning_spot, \
                                        num_spots_for_winner = vnum_spots_for_winner, \
                                        datetime_posted = vdatetime_posted, \
                                        datetime_completed = vdatetime_completed, \
                                        duration_hours = vduration_hours, \
                                        tier = vtier)
                    newRaffle.save()
                    num_records_added += 1
                    self.insert_spot_count(vspot_histogram, newRaffle)
                #pprint.pprint(vars(post))
        self.write_to_status_log("Ending scrape. Added " + str(num_records_added) + " records.")

    def build_histogram(self, description, win_number, post):
        win_user = None
        spot_counts_by_user = {}
        spot_counts = {}
        results = {}
        num_spots = 0
        spot_regex = r"(([0-9]+)\s(/u/\S+))"

        spots = re.findall(spot_regex, description)

        for spot in spots:
            num_spots += 1
            if int(spot[1]) == win_number:
                win_user = spot[2]
                print(win_user)
            if spot[2] in spot_counts_by_user.keys():
                spot_counts_by_user[spot[2]] += 1
            else:
                spot_counts_by_user[spot[2]] = 1

        results["num_spots"] = num_spots

        if (win_user):
            results["winner_num_spots"] = spot_counts_by_user[win_user]
        else:
            results["winner_num_spots"] = None
            self.write_to_log("No winner found", post)

        for user in spot_counts_by_user.keys():
            num_spots = spot_counts_by_user[user]
            if num_spots in spot_counts.keys():
                spot_counts[num_spots] += 1
            else:
                spot_counts[num_spots] = 1

        results["spot_counts"] = spot_counts

        return results

    def get_win_comment(self, post):
        bot_call_regex = r"/u/boyandhisbot\s[0-9]+$"
        bot_call_regex_ci = re.compile(bot_call_regex, re.IGNORECASE)
        winner_regex = r"The\swinner\sis:\s\[([0-9]+)\]"
        winner_regex_c = re.compile(winner_regex)
        winComment = None

        botCallComment = None
        for comment in post.comments:
            if re.match(bot_call_regex_ci, comment.body) != None:
                botCallComment = comment
        if not botCallComment:
            self.write_to_log("No bot call comment found", post)
            return winComment

        for reply in botCallComment._replies:
            result = re.search(winner_regex_c, reply.body)
            if result:
                winComment = reply
                break;

        if not winComment:
            self.write_to_log("No win comment found", post)

        return winComment


    def get_win_number(self, post, winComment):
        winner_regex = r"The\swinner\sis:\s\[([0-9]+)\]"
        result = re.search(winner_regex, winComment.body)
        win_number = int(result.group(1))

        if (win_number == None):
            win_number = -1
            self.write_to_log("No win number found", post)
        return win_number


    def get_raffle_start_time(self, post):
        created_utc = int(post.created_utc)
        datetime_object = datetime.utcfromtimestamp(created_utc)
        return datetime_object


    def get_raffle_end_time(self, post, win_comment):
        created_utc = int(win_comment.created_utc)
        datetime_object = datetime.utcfromtimestamp(created_utc)
        return datetime_object


    def get_raffle_tier(self, post):
        title = post.title
        title_tag_regex = r"\[(.+)\]"
        nm_regex_c = re.compile(r"NM", re.IGNORECASE)
        blue_nm_regex_c = re.compile(r"Blue NM", re.IGNORECASE)

        tag = re.search(title_tag_regex, post.title)

        #If we got to this function, there is a "complete" flair so this is certianly
        #a raffle. NM and Blue NM are forced to use the tags. If there is something
        #other than NM or Blue NM, lets assume that it is a main raffle.
        if tag == None:
            print("MAIN")
            return 2
        else:
            tag = tag.group(1)

            if re.match(nm_regex_c, tag):
                print("NM")
                return 0 #NM
            elif re.match(blue_nm_regex_c, tag):
                print("Blue")
                return 1 #Blue NM
            else:
                print("MAIN")
                return 2 #Main

    def insert_spot_count(self, spot_counts, raffle):
        for num_spots in spot_counts.keys():
            num_users = spot_counts[num_spots]
            spot_entry = SpotCount(post_id = raffle, num_spots = num_spots, count = num_users)
            spot_entry.save()

    def write_to_log(self, error_message, post):
        log_file = open("error_log.txt", "a+")
        log_file.write("Title: " + post.title + ", " + error_message + "\n")
        log_file.close()

    def write_to_status_log(self, message):
        log_file = open("status_log.txt", "a+")
        log_file.write(message + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n")
        log_file.close()


    def handle(self, **options):
        self.scrape_wur()
