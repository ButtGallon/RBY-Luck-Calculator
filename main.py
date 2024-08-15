import requests
from luckfunctions import *
from functionslist import *
import json

def parse_log(replayURL):
    logfile = requests.get(replayURL+'.log').text.splitlines()
    results, parsedlogfile = prepare_parsedlogfile(logfile, replayURL)
    for line in parsedlogfile:
        line, parsedlogfile, results = replay_parse_switch(line, parsedlogfile, results)
        # sort significant events
    results['significantevents'] = sorted(results['significantevents'], key=lambda tup: tup[0])
    # sort luckcatalog
    results['luckcatalog'] = sorted(results['luckcatalog'], key=lambda tup: tup[1])
    # update result totals
    teams = ['team1', 'team2']
    categories = ['kills', 'deaths', 'luck', 'support', 'hphealed', 'damagedone', 'remaininghealth']
    for team in teams:
        for mon in results[team]['roster']:
            results[team]['score'] += 1 - mon['deaths']
            for category in categories:
                results[team][category] += mon[category]
                results[team][category] = round(results[team][category], 2)
            mon['luck'] = mon['luck'] / 100
            results[team]['totalhealth'] += 100
        results[team]['luck'] = results[team]['luck'] / 100
    # output results to json file
    with open('results.json', 'w+') as f:
        json.dump(results, f, indent=2)
    # team1
    damagedone = results['team1']['damagedone']
    damagedonetest = results['team2']['totalhealth'] - results['team2']['remaininghealth'] + results['team2'][
        'hphealed']
    score = results['team1']['score']
    scoretest = len(results['team1']['roster']) - results['team2']['kills'] - results['team1']['selfdeaths']
    if damagedonetest != damagedone: results['errormessage'].append(
        "This replay's Team 1 damage numbers do not add up. Please contact claduva and do not submit the replay.")
    if scoretest != score: results['errormessage'].append(
        "This replay's Team 1 score numbers do not add up. Please contact claduva and do not submit the replay.")
    if score != 0 and results['team2']['wins'] == 1: results['errormessage'].append(
        "The losing team's score should be 0. Please contact claduva and do not submit the replay.")
    # team2
    damagedone = results['team2']['damagedone']
    damagedonetest = results['team1']['totalhealth'] - results['team1']['remaininghealth'] + results['team1'][
        'hphealed']
    score = results['team2']['score']
    scoretest = len(results['team2']['roster']) - results['team1']['kills'] - results['team2']['selfdeaths']
    if damagedonetest != damagedone: results['errormessage'].append(
        "This replay's Team 2 damage numbers do not add up. Please contact claduva and do not submit the replay.")
    if scoretest != score: results['errormessage'].append(
        "This replay's Team 2 score numbers do not add up. Please contact claduva and do not submit the replay.")
    if score != 0 and results['team1']['wins'] == 1: results['errormessage'].append(
        "The losing team's score should be 0. Please contact claduva and do not submit the replay.")
    return results

def prepare_parsedlogfile(logfile,replayURL):
    parsedlogfile=[]
    line_number=0
    turn_number=0
    results=initializeoutput()
    results['replay']=replayURL
    for line in logfile:
        if line.find("|")>-1:
            #remove unneeded lines
            line=line.replace(", M","").replace(", F","").replace("-*","").replace(", shiny","").replace(", L50","").replace(", L5","").replace("-Striped","").replace("-Trash","").replace("-Sandy","").replace("Indeedee-F","Indeedee").replace("-Super","").replace("-Large","").replace("-Small","").replace("-Blue","").replace("-Orange","").replace("Florges-White","Florges").replace("-Pokeball","").replace("-Elegant","").replace("-Indigo","").replace("-Yellow","").replace("-Bug","").replace("-Dark","").replace("-Dragon","").replace("Arceus-Electric","Silvally").replace("Silvally-Electric","Silvally").replace("-Fairy","").replace("-Fighting","").replace("-Fire","").replace("-Flying","").replace("-Ghost","").replace("-Grass","").replace("-Ground","").replace("-Ice","").replace("-Normal","").replace("-Poison","").replace("Arceus-Psychic","Arceus").replace("Silvally-Psychic","Silvally").replace("-Rock","").replace("-Steel","").replace("-Water","").replace("-Douse","").replace("-Burn","").replace("-Chill","").replace("-Shock","").replace("Type: ","Type:").replace("Mr. ","Mr.").replace("-Sensu","").replace("-Pom-Pom","").replace("-Pa'u","").replace("Farfetch'd","Farfetchd").replace("-Totem","").replace("-Resolute","").replace("-Meteor","").replace("Meowstic-F","Meowstic").replace("-East","").replace("fetch’d","fetchd").replace("fetch'd","fetchd").replace("-Ruby-Cream","").replace("-Matcha-Cream","").replace("-Mint-Cream","").replace("-Lemon-Cream","").replace("-Salted-Cream","").replace("-Ruby-Swirl","").replace("-Caramel-Swirl","").replace("-Rainbow-Swirl","")
            linestoremove=["|","|teampreview","|clearpoke","|upkeep"]
            badlines=["","|start","|player|p1","|player|p2","|player|p1|","|player|p2|","|-notarget","|-clearallboost","|-nothing","|-ohko","|rated"]
            linepurposestoremove=["j","c","l","html","raw","teamsize","gen","gametype","tier","rule","-mega","seed","teampreview","anim"]
            linepurpose=line.split("|",2)[1].replace("-","")
            #Clean up |start
            if line == '|start':
                line = '|start|'
            #iterate turn number
            if linepurpose=="turn":
                turn_number+=1
                results['numberofturns']=turn_number
            #add turn data
            elif line not in linestoremove and linepurpose not in linepurposestoremove and line not in badlines:
                lineremainder=line.split("|",2)[2]
                if lineremainder.find("/")>-1:
                    lineremainder_=""
                    for segment in lineremainder.split("|"):
                        if segment.find("/")>-1:
                            try:
                                numerator=segment.split("/")[0]
                                denomenator=segment.split("/")[1].split("|")[0].split(" ")[0]
                                newnumerator=int(int(numerator)/int(denomenator)*100)
                                if newnumerator==0: newnumerator=1
                                segment=segment.replace(f"/{denomenator}","/100").replace(f"{numerator}/",f"{newnumerator}/")
                            except:
                                pass
                        lineremainder_=lineremainder_+"|"+segment
                    lineremainder=lineremainder_[1:]
                parsedlogfile.append([line_number,turn_number,linepurpose,lineremainder])
                line_number+=1
    return results,parsedlogfile

def initializeoutput():
    #initialize output json
    results={}
    results['team1']={}
    results['team2']={}
    results['team1']['coach']=""
    results['team2']['coach']=""
    results['team1']['roster']=[]
    results['team2']['roster']=[]
    results['team1']['wins']=0
    results['team2']['wins']=0
    results['team1']['forfeit']=0
    results['team2']['forfeit']=0
    results['team1']['score']=0
    results['team2']['score']=0
    results['team1']['timesswitched']=-1
    results['team2']['timesswitched']=-1
    results['team1']['selfdeaths']=0
    results['team2']['selfdeaths']=0
    results['team1']['remaininghealth']=0
    results['team2']['remaininghealth']=0
    results['team1']['totalhealth']=0
    results['team2']['totalhealth']=0
    results['team1']['kills']=0
    results['team2']['kills']=0
    results['team1']['deaths']=0
    results['team2']['deaths']=0
    results['team1']['luck']=0
    results['team2']['luck']=0
    results['team1']['damagedone']=0
    results['team2']['damagedone']=0
    results['team1']['hphealed']=0
    results['team2']['hphealed']=0
    results['team1']['support']=0
    results['team2']['support']=0
    results['team1']['activemon']=None
    results['team2']['activemon']=None
    results['team1']['Leech Seed']=None
    results['team2']['Leech Seed']=None
    results['numberofturns']=0
    results['turns']=[]
    results['replay']=""
    results['significantevents']=[]
    results['luckcatalog']=[]
    results['errormessage']=[]
    return results

def replay_parse_switch(argument, parsedlogfile, results):
    switcher = {
        'activate': activate_function,
        'boost': boost_function,
        'cant': cant_function,
        #'crit': crit_function,
        'curestatus': curestatus_function,
        'damage': damage_function,
        'detailschange': detailschange_function,
        'drag': switch_drag_function,
        'fieldstart': fieldstart_function,
        'fieldend': fieldend_function,
        'heal': heal_function,
        'message': message_function,
        'move': move_function,
        'player': player_function,
        'poke': poke_function,
        'replace': replace_function,
        'sethp': sethp_function,
        'start': start_function,
        'status': status_function,
        'switch': switch_drag_function,
        'unboost': unboost_function,
        'weather': weather_function,
        'win': win_function,
        'zpower': zpower_function,
    }
    # Get the function from switcher dictionary
    func = switcher.get(argument[2], lambda argument, parsedlogfile, results: (argument, parsedlogfile, results))
    # Execute the function
    return func(argument, parsedlogfile, results)

def print_results(url):
    parse_log(url)
    print(str(json.load(open('results.json'))['team1']['coach']) + " vs " + str(
        json.load(open('results.json'))['team2']['coach']))
    if json.load(open('results.json'))['team1']['luck'] >= 0:
        luckyteam = 'team1'
    else:
        luckyteam = 'team2'
    print("Overall Luck Score: " + str(json.load(open('results.json'))[luckyteam]['luck']) + " in favor of " +
          json.load(open('results.json'))[luckyteam]['coach'])
    print('')
    results = json.load(open('results.json'))
    for mon in results['team1']['roster']:
        print(json.load(open('results.json'))['team1']['coach'] + '\'s ' + mon['pokemon'] + ' luck value is: ' + str(
            mon['luck']))
    print('')
    for mon in results['team2']['roster']:
        print(json.load(open('results.json'))['team2']['coach'] + '\'s ' + mon['pokemon'] + ' luck value is: ' + str(
            mon['luck']))


# Press the green button in the gutter to run the script.
if __name__ == '__main__':

    print_results('https://replay.pokemonshowdown.com/gen1zu-2180241963')
