This program is meant to take in public RBY replays from Pokemon Showdown and determine an aggregate "Luck Score" for each pokemon (and by extension, player) in the match.

To use this program: 
1) Save all files locally to a single folder
2) Open main.py in your preferred IDE
  - (if you don't have a Python IDE, you can download the Anaconda launcher here (https://www.anaconda.com/download), which prepares several IDEs for your machine.
  - My go-to IDE of the ones available through Anaconda is PyCharm Community Edition
3) At the bottom of main.py, inside an "if __name__ == '__main__':" block, replace the URL inside the "parse_log()" line with the URL of the replay you want to analyze
4) Run main.py and the results will be printed to the console. If you want to dig deeper into what contributed to the luck scores, the full luck calculation logs are saved at the bottom of the results.json file

Things the calculator already takes into account
  - Confusion luck
  - Paralysis luck
  - Crit luck (correctly based on speed stat)
  - Miss luck (includes 1/256 miss chance)
  - Secondary effect chance
  - Wrap partial trapping only counting as one move use
  - Secondary effect immunity by type (no body slam para for normals, no burn chance for fire types, etc)
  - Sleep Clause & Freeze Clause

Things the calculator doesn't take into account (yet)
  - Damage ranges
  - Still considers a crit lucky even if it would have killed without the crit
  - Checking if crits actually decrease damage done (due to stat boosts/drops)
  - Wrap turn luck (2-5 turns)
  - Sleep turn luck (1-7 turns)
  - Confusion turn luck (1-3 turns)
  - Multi-hit move luck (Pin Missile 2-5 hits, etc)
  - Still considers an attempted stat drop unlucky even if the stat is already at -6

 If you have any questions/advice/bugs, feel free to reach out to ButtGallon on Pokemon Showdown & Smogon Forums (https://www.smogon.com/forums/members/buttgallon.682693/), or kevo411@verizon.net
