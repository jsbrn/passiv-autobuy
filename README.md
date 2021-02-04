# passiv-autobuy

[Passiv](https://passiv.com) is a tool that connects to your brokerage and calculates portfolio rebalancing automatically based on targets you select. It then provides a one click BUY button to make the process easier. However, due to strict regulations, they do not expose an API for the executing of orders.

For me, that meant I could not set up my Raspberry Pi to automatically place my preconfigured orders every week. But since I am still able to log in to the website and click the button myself, I decided to write a Python script that will simulate such a thing.

Running this script will connect to your account and execute the orders.

## Setup

It's written for Python 3 but is probably backwards compatible. You'll need to `pip install` the following:
* `requests`
* `pyotp`
* `python-dotenv`

## Running

When you run the script, it will walk you through the process step by step. It will NOT perform any order executions without asking you first, unless you pass `-y` in the arguments.

## Environment Variables

You can supply the required information in a `.env` file to make automation easier:

```
    EMAIL = "example@example.com"
    PASSWORD = "examplePassword123"
    TFA_SECRET = "exAmplESeCr3t"
```

If you want to enable 2FA on your Passiv account and still run it via a cron job, set up an authenticator app and paste the 2FA secret into the `.env` file. Your authenticator app should have some kind of export function.