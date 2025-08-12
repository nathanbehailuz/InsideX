What should i use to build:
- the website (front end, backend)
- the scraping method + which sites should i scrape
- what is the algorithm to be used (I am thinking of a neural net)


What am I building:
- A program which identifies insider transactions/buys, flags them and sends it to your email. 

Flagging is made by an algorithm which is trained by previous records of insider buy and their respective returns (per give time period, 10  days, a month, a year)

- We will have a website with a landing page explaining the goal and usage of the project. And have a button for signup (users will create account to get email notifications when there is an interesting trade happening) 

- The website will provide a database of previous insider buys and their respective returns and also shows the models prediction on those data points



Order of building:
1. frontend: 
- landing page Landing /
    Goal: Explain Insidex and drive signups.
    Hero: Title “Insidex — Executive trades, indexed.”
    Sub: “Scan. Score. Signal. Deterministic alerts from SEC Form 4 filings.”
    CTA: “Sign up for alerts” → auth flow.
    Sections:

    “How it works” (ETL→Score→Signal→Track).

    “What you’ll receive” (sample alert bullets).

    “Methodology & bias controls” (short list).

    Disclaimer banner (sticky footnote).

- 

