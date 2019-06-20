This allows Modmail to function throughout the month without a credit card.

# Installation
Run this command in Modmail: `plugin add fourjr/modmail-plugins/auto-restarter`

Read the [disclaimer](#disclaimer).

## Server Setup
1. Create another Heroku account
    - I used [Yandex](https://mail.yandex.com) as it was an email service without phone verification that Heroku did not block.
2. Click this big purple button [![Deploy to Heroku](https://img.shields.io/badge/deploy-to%20heroku-blueviolet.svg?style=for-the-badge)](https://heroku.com/deploy?template=https://github.com/fourjr/heroku-startup)

3. Retrieve your Heroku API token from https://dashboard.heroku.com/account (scroll down)
4. Start the web dyno
5. Add the app URL via the `setuprestarter` command

## Client Setup
1. Create 2 Heroku accounts
    - I used [Yandex](https://mail.yandex.com) as it was an email service without phone verification that Heroku did not block.
2. In each of the accounts, deploy modmail and append `-1` and `-2` respectively to both app names.
3. Create an environment variable for both apps as `HEROKU_APP_NAME` with the value of their app names with the index `-1` or `-2` respectively.
4. Start the worker on `-1` but not `-2`.

## More info
The full documentation of how this plugin works is on [fourjr/heroku-startup](https://github.com/fourjr/heroku-startup/blob/master/README.md)

## Disclaimer
I do not hold *any* responsibility if you get banned from Heroku. Choosing to add this to your Heroku experience is completely your own decision and I have no part to play in that. This is simply a tool for risk-takers who wish to risk that their account might be deleted to have fun.
