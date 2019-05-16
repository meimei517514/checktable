# -*- coding: utf-8 -*-

import re,os,json
from flask import Flask
from flask import request
from basecode.check_table import *

app = Flask(__name__, static_url_path='')


@app.route("/checktable", methods=['GET', 'POST'])
def access_payload():

    payload = json.loads(request.values.get("payload"))

    #post_redmine_issues(payload)
    parse_commits(payload)

    return "sweat"


def main():
    app.run(host='100.84.74.126', port=9542, debug=True)

if __name__ == '__main__':
    main()
