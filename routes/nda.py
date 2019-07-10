#!/usr/bin/env python3

# Author: Samuel Guebo
# Description: Utility for generating a list of
# users in wikicode text. It is used to populate
# m:Access to nonpublic personal data policy/Noticeboard
# License: MIT

import itertools
from flask import render_template
from flask import request
import json
import mw_api_client as mw
import re
import requests
from flask import Blueprint

nda = Blueprint('nda', __name__)


@nda.route('/nda',  methods=['GET', 'POST'])
def index(title=None):
    """
    Default/Home page of the application/tool.

    Keyword arguments:
    month -- the default title of the homepage
    """

    title = "Flax"
    description = "A minimalist application layout in Python/Flask."
    content = None
    user_groups = diffs = []
    summary = remote_wiki_text = ""
    namespace = 'Access to nonpublic personal data policy/Noticeboard'

    if request.method == 'POST':

        old_content = request.form['previous_content']
        new_users = request.form['new_users']
        diff = request.form['diff']

        # format news users
        if new_users != "":
            if len(new_users.split("\r\n")) > 1:
                summary = "+" + ", ".join(unique_list(new_users.split("\r\n")))
            else:
                summary = "+" + new_users

            new_users = text_to_users(new_users)

        if len(new_users) > 0 or diff != "":

            if old_content != "":

                # append new_users to old_users
                old_users = get_users(old_content)

                # update new_users with diff
                if diff != "":
                    summary = []
                    for user in old_users:
                        if user['status'] == 'new':
                            user['status'] = 'old'
                            user['diff'] = diff

                            summary.append(user["username"])

                    summary = "+diff for " + ", ".join(summary)

                if len(new_users) > 0:
                    user_groups = get_user_groups(old_users + new_users)
                else:
                    user_groups = get_user_groups(old_users)

                header_template = re.search('\\{\\{\\:.*?\\}\\}',
                                            old_content).group(0)
                content = get_wikicode(header_template, user_groups)
                content += "\n"
                content += summary
    else:
        remote_wiki_text = get_content_from_wiki('https://meta.wikimedia.org',
                                                 namespace)
        diffs = get_diff('https://meta.wikimedia.org/w/api.php', namespace)
        page_id = list(diffs['query']['pages'])[0]
        diffs = diffs['query']['pages'][page_id]['revisions']

    return render_template(
        'nda.html', title=title, content=content,
        description=description, remote_wiki_text=remote_wiki_text,
        summary=summary, diffs=diffs, namespace=namespace
    )


def get_group(username):
    """
    Check first character of a username and identify its group

    Keyword arguments:
    username -- a string containing the username
    """

    group = ""

    alphabet = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L",
                "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X",
                "Y", "Z"]

    regexcharacters = '[\\!\\@\\#\\$\\%\\^\\&\\*\\(\\)\\,\\.\\?\\"\\:\\{\\}\\|'
    regexcharacters += '\\<\\>\\-]'

    chars = list(username)
    first_char = ""

    if len(chars) > 0:
        first_char = chars[0]
    else:
        print(username+" could not be split")

    # check whether it's a Number
    if re.search("\\d", first_char) is not None:
        group = "Numbers"

    # check whether it's a Symbol
    elif re.search(regexcharacters, first_char) is not None:
        group = "Symbols"

    # check whether character is in Alphabet
    elif first_char.capitalize() in alphabet:
        if first_char in ["X", "Y", "Z"]:
            group = "XYZ"
        else:
            group = first_char.capitalize()

    # if not in the above, then it's 215
    else:
        group = "NonLatin"

    return group


def get_file_text(filename):
    """
    Extract text from a file

    Keyword arguments:
    filename -- the file from which the text is extracted
    """
    text = ""
    try:
        f = open(filename)

        # append characters
        for x in f:
            # chars += x
            text += x

    except Exception as e:
        print(e)
        pass

    return text


'''
def get_noticeboard_array(text):
    """
    Collect specific data from the wikicode
    and convert it into an array

    Keyword arguments:
    text -- a raw text in wikicode format
    """

    header_template = re.search("\{\{\:.*?\}\}", text).group(0)
    users = get_users(text)
    user_groups = get_user_groups(users)
    content = get_wikicode(header_template, user_groups)

    return content
'''


def get_user_groups(users):
    """
    Generate an array, grouping them by key

    Keyword arguments:
    users -- a list object containing users
    """

    # sort users so that the gouping can work
    usernames = sorted(users, key=lambda x: x['username'])
    users = []  # empty it
    user_groups = {}

    # remove duplicates
    for k, g in itertools.groupby(usernames, key=lambda x: x['username']):
        username = list(g)
        users.append(username[0])

    # group users by keyword, requires previous sorting with same key
    users = sorted(users, key=lambda x: x['group'])

    for k, g in itertools.groupby(users, key=lambda x: x['group']):

        user_groups[k] = list(g)

        # sort again by username
        user_groups[k] = sorted(user_groups[k],
                                key=lambda x: x['username'])

    # odering user_groups
    ordered_user_groups = {}
    keys = sorted(user_groups.keys())

    for key in keys:
            ordered_user_groups[key] = user_groups[key]

    return ordered_user_groups


def get_users(text):
    """
    Collect users from the wikicode
    and convert it into an array

    Keyword arguments:
    text -- a raw text in wikicode format
    """

    users = []

    users_with_diff = re.findall("\\{\\{\\/user.*", text)
    users_without_diff = re.findall("\\* \\[\\[User:.*\\]\\]", text)

    for user_line in users_with_diff:
        description = re.sub("\\{\\{.*\\}", "", user_line)  # only description
        user_line = user_line.replace(description, "")  # all but description
        diff = re.search("\\b/|\\d+", user_line).group(0)  # diff number
        username = re.sub("\\{\\{.*\\|", "",
                          user_line).replace("}", "")  # username
        group = get_group(username)

        if len(str(description)) < 2:
            description = None

        row = {
            "diff": diff,
            "username": username,
            "description": description,
            "group": group,
            "status": "old",
        }

        users.append(row)

    for user_line in users_without_diff:
        username = re.search("User\\:.*?\\]", user_line)
        if username is not None:
            username = username[0].replace("]", "").replace("User:", "")

        group = get_group(username)
        row = {
            "diff": "",
            "username": username,
            "description": "",
            "group": group,
            "status": "new",
        }

        users.append(row)

    return users


def get_wikicode(header_template, user_groups):
    """
    Generate a wikicode text by concatenating
    and formatting header_template and items
    of user_groups list

    Keyword arguments:
    header_template -- a transclusion in wikicode
    user_groups -- a list object containing grouped users
    """

    wikicode = ""

    # header_template, linebreak
    wikicode += header_template
    wikicode += "\n\n"

    # Number, Symbols
    for x in ["Numbers", "Symbols"]:
        if x in user_groups:
            wikicode += get_wikicode_item(x, user_groups[x])

    # A-Z
    for x in user_groups:
        if x not in ["Numbers", "Symbols", "NonLatin"]:
            wikicode += get_wikicode_item(x, user_groups[x])

    # Non-Latin
    y = "NonLatin"
    if y in user_groups:
        wikicode += get_wikicode_item(y, user_groups[y])

    return wikicode


def get_wikicode_item(header, users):
    """
    Generate a wikicode that will be used in loop
    for user_groups list

    Keyword arguments:
    header -- section header
    user_groups -- a list object containing grouped users
    """

    wikicode = ""

    # edge case
    if header == "NonLatin":
        wikicode += '<span id="Nonlatin"></span>'  # Id for navigation
        wikicode += "\n"
        header = "Non-Latin"

    if header == "XYZ":
        wikicode += '<span id="X"></span><span id="Y">'
        wikicode += '</span><span id="Z"></span>'
        wikicode += "\n"

    wikicode += "=== " + header + " ==="
    wikicode += "\n"

    for user in users:
        if(user['status'] == 'new'):
            wikicode += "* [[User:" + user['username'] + "]]"
        else:
            wikicode += "{{/user|" + user['diff'] + "|"
            wikicode += user['username'] + "}}"
        if user['description']:
            wikicode += user['description']
        wikicode += "\n"

    wikicode += "\n"

    return wikicode


def text_to_users(text):
    """
    Generate a list of users from text

    Keyword arguments:
    text -- raw text
    """

    users = []
    for user in text.split("\r\n"):
        group = get_group(user)

        row = {
            "diff": "",
            "username": user,
            "description": None,
            "group": group,
            "status": "new",
        }

        users.append(row)

    return users


def get_diff(api_url, namespace):
    """
    Fetch last diff of a wiki page

    Keyword arguments:
    api_url -- absolute link to the Rest API
    namespace -- page where to fetch diffs

    Link: https://www.mediawiki.org/wiki/API:Revisions
    """

    parameters = {
        "action": "query",
        "prop": "revisions",
        "titles": namespace,
        "rvprop": "ids|user|comment",
        "rvlimit": "1",
        "format": "json"
    }

    query = ""
    i = 0
    for k in parameters:
        query += k + "=" + parameters[k]
        if i < len(parameters)-1:
            query += "&"
        i += 1

    url = api_url + "?" + query
    r = requests.get(url)
    jsonArray = r.text

    return json.loads(jsonArray)


def get_content_from_wiki(url, namespace):
    """
    Fetch raw text from a wiki page

    Keyword arguments:
    wiki -- wiki website
    namespace -- page where to fetch text

    Link: https://mwclient.readthedocs.io/en/latest/user/page-ops.html
    """

    wp = mw.Wiki(url+"/w/api.php")
    text = wp.page(namespace).read()

    return text


def unique_list(l):
    """
    Remove duplicates from text
    """
    ulist = []
    [ulist.append(x) for x in l if x not in ulist]
    return ulist
