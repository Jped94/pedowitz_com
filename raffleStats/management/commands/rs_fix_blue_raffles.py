#!/usr/bin/env python3
import praw
import pandas as pd
import re
import sys
from . import rs_config
from django.core.management.base import BaseCommand, CommandError
from django.db.models import F
from raffleStats.models import Raffle


class Command(BaseCommand):
    help = "[blue nm] tag turned into [blue]. Now all blues are being classified as main"

    def retier_blue_raffles(self):
        raffles = Raffle.objects.order_by('-datetime_completed')

        for raffle in raffles:
            #if it is considered main, lets reevaluate
            if (raffle.tier == 2):
                new_tier = self.get_raffle_tier(raffle)
                if (new_tier != raffle.tier):
                    raffle.tier = new_tier
                    raffle.save()


    def get_raffle_tier(self, post):
        title = post.title
        title_tag_regex = r"\[(.+)\]"
        nm_regex_c = re.compile(r"NM", re.IGNORECASE)
        blue_nm_regex_c = re.compile(r"Blue", re.IGNORECASE)

        tag = re.search(title_tag_regex, post.title)

        #If we got to this function, there is a "complete" flair so this is certianly
        #a raffle. NM and Blue NM are forced to use the tags. If there is something
        #other than NM or Blue NM, lets assume that it is a main raffle.
        if tag == None:
            print("MAIN")
            return 2
        else:
            tag = tag.group(1)

            #match must find the regex at the beginning
            if re.match(nm_regex_c, tag):
                print("NM")
                return 0 #NM
            #search for blue so we can have "Blue NM" or "Blue"
            elif re.search(blue_nm_regex_c, tag):
                print("Blue")
                return 1 #Blue NM
            else:
                print("MAIN")
                return 2 #Main



    def handle(self, **options):
        self.retier_blue_raffles()
