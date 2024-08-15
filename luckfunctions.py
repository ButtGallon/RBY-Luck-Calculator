from pokemonlist import *
from movelist import *
def luckappend(line,results,mon,event,luckchange):
    #assign values to event multipliers
    eventmodifier = 1
    for move, info in moveList.items():
        if event.find(info['Name']) > -1:
            if info['Effect'] == 'unboost':
                eventmodifier = 1
            if info['Effect'] == 'confusion':
                eventmodifier = 1
            if info['Effect'] == 'flinch':
                eventmodifier = 3
            if info['Effect'] == 'frz':
                eventmodifier = 5
            if info['Effect'] == 'par':
                eventmodifier = 1
            if info['Effect'] == 'brn':
                eventmodifier = 1
            if info['Effect'] == 'psn':
                eventmodifier = 0.5
        if event.find('crit') > -1 or event.find('Crit') > -1:
            eventmodifier = 1
            break
        if event.find('miss') > -1 or event.find('hit by') > -1:
            eventmodifier = 2
            break
        if event.find('Paralysis') > -1:
            eventmodifier = 1.5
            break
        if event.find('In Confusion') > -1:
            eventmodifier = 2
            break
    startluck = mon['luck'] / 100
    mon['luck'] += luckchange * eventmodifier
    if luckchange!=0:
        results['luckcatalog'].append([line[1],mon['pokemon'] + ' (' + mon['coach'] + ')',event,round(startluck, 4),round(luckchange*eventmodifier/100, 4),round(mon['luck']/100, 4)])
    return results

def miss_function(line,attacker,target,move,moveaccuracy, results):
    results=luckappend(line,results,attacker,f"Mon missed a move ({move})",-(moveaccuracy))
    results=luckappend(line,results,target,f"Opponent missed a move ({move})",(moveaccuracy))
    #results['significantevents'].append([line[1],f"LUCK: {attacker['pokemon']} missed {move} against {target['pokemon']}"])
    return results

def roster_search(team,pokemon,results):
    if team=="p1a":
        team="team1"
    elif team=="p2a":
        team="team2"
    for mon in results[team]['roster']:
        if mon['nickname']==pokemon:
            pokemon=mon
    return pokemon

def secondary_check(attacker,target,move,line,results,parsedlogfile,attackingteam,notothermove):
    if notothermove:
        attacker['moves'][move]['posssecondaryeffects']+=1
    moveswithsecondaryeffect=dict([
    ['Acid', ['unboost', 'def|1',target['nickname'], .1,f"{target['pokemon']} suffered a stat drop via secondary effect by {attacker['pokemon']} with {move}"]],
    ['Aurora Beam', ['unboost', 'atk|1',target['nickname'], .1,f"{target['pokemon']} suffered a stat drop via secondary effect by {attacker['pokemon']} with {move}"]],
    ['Bite', ['cant', 'flinch',target['nickname'], .1,f"{target['pokemon']} was flinched by {attacker['pokemon']} with {move}"]],
    ['Blizzard', ['status', 'frz',target['nickname'],.1,f"{target['pokemon']} was frozen by {attacker['pokemon']} with {move}"]],
    ['Body Slam', ['status', 'par',target['nickname'],.3,f"{target['pokemon']} was paralyzed by {attacker['pokemon']} with {move}"]],
    ['Bone Club', ['cant', 'flinch',target['nickname'], .1,f"{target['pokemon']} was flinched by {attacker['pokemon']} with {move}"]],
    ['Bubble', ['unboost', 'spe|1',target['nickname'], .1,f"{target['pokemon']} suffered a stat drop via secondary effect by {attacker['pokemon']} with {move}"]],
    ['Bubble Beam', ['unboost', 'spe|1',target['nickname'], .1,f"{target['pokemon']} suffered a stat drop via secondary effect by {attacker['pokemon']} with {move}"]],
    ['Confusion', ['start', 'confusion',target['nickname'], .1,f"{target['pokemon']} was confused by {attacker['pokemon']} with {move}"]],
    ['Constrict', ['unboost', 'spe|1',target['nickname'], .1,f"{target['pokemon']} suffered a stat drop via secondary effect by {attacker['pokemon']} with {move}"]],
    ['Ember', ['status', 'brn',target['nickname'],.1,f"{target['pokemon']} was burned by {attacker['pokemon']} with {move}"]],
    ['Fire Blast', ['status', 'brn',target['nickname'],.3,f"{target['pokemon']} was burned by {attacker['pokemon']} with {move}"]],
    ['Fire Punch', ['status', 'brn',target['nickname'],.1,f"{target['pokemon']} was burned by {attacker['pokemon']} with {move}"]],
    ['Flamethrower', ['status', 'brn',target['nickname'],.1,f"{target['pokemon']} was burned by {attacker['pokemon']} with {move}"]],
    ['Headbutt', ['cant', 'flinch', target['nickname'], .3, f"{target['pokemon']} was flinched by {attacker['pokemon']} with {move}"]],
    ['Hyper Fang', ['cant', 'flinch', target['nickname'], .1, f"{target['pokemon']} was flinched by {attacker['pokemon']} with {move}"]],
    ['Ice Beam', ['status', 'frz',target['nickname'],.1,f"{target['pokemon']} was frozen by {attacker['pokemon']} with {move}"]],
    ['Ice Punch', ['status', 'frz',target['nickname'],.1,f"{target['pokemon']} was frozen by {attacker['pokemon']} with {move}"]],
    ['Lick', ['status', 'par',target['nickname'],.3,f"{target['pokemon']} was paralyzed by {attacker['pokemon']} with {move}"]],
    ['Low Kick', ['cant', 'flinch', target['nickname'], .3, f"{target['pokemon']} was flinched by {attacker['pokemon']} with {move}"]],
    ['Poison Sting', ['status', 'psn',target['nickname'],.2,f"{target['pokemon']} was poisoned by {attacker['pokemon']} with {move}"]],
    ['Psybeam', ['start', 'confusion',target['nickname'], .1,f"{target['pokemon']} was confused by {attacker['pokemon']} with {move}"]],
    ['Psychic', ['unboost', 'spa|1',target['nickname'], .33,f"{target['pokemon']} suffered a stat drop via secondary effect by {attacker['pokemon']} with {move}"]],
    ['Rolling Kick', ['cant', 'flinch', target['nickname'], .3, f"{target['pokemon']} was flinched by {attacker['pokemon']} with {move}"]],
    ['Sludge', ['status', 'psn',target['nickname'],.3,f"{target['pokemon']} was poisoned by {attacker['pokemon']} with {move}"]],
    ['Smog', ['status', 'psn',target['nickname'],.3,f"{target['pokemon']} was poisoned by {attacker['pokemon']} with {move}"]],
    ['Thunder', ['status', 'par',target['nickname'],.1,f"{target['pokemon']} was paralyzed by {attacker['pokemon']} with {move}"]],
    ['Thunderbolt', ['status', 'par',target['nickname'],.1,f"{target['pokemon']} was paralyzed by {attacker['pokemon']} with {move}"]],
    ['Thunder Punch', ['status', 'par',target['nickname'],.1,f"{target['pokemon']} was paralyzed by {attacker['pokemon']} with {move}"]],
    ['Thunder Shock', ['status', 'par',target['nickname'],.1,f"{target['pokemon']} was paralyzed by {attacker['pokemon']} with {move}"]],
    ['Twineedle', ['status', 'psn',target['nickname'],.2,f"{target['pokemon']} was poisoned by {attacker['pokemon']} with {move}"]],])

    move_=moveswithsecondaryeffect[move]
    turndata=list(filter(lambda x: x[1] == line[1] and x[0] > line[0], parsedlogfile))
    secondaryEffectLanded = False
    hittingsubstitute = False
    for line_ in turndata:
        if line_[2]==move_[0] and line_[3].find(move_[1])>-1 and line_[3].find(move_[2])>-1:
            #results['significantevents'].append([line[1],f"LUCK: {move_[4]}"])
            secondaryEffectLanded = True
            results=luckappend(line,results,attacker,f"Mon landed secondary effect from ({move})",(1-move_[3])*100)
            results=luckappend(line,results,target,f"Mon was hit with secondary effect from ({move})",-(1-move_[3])*100)
            if notothermove:
                attacker['moves'][move]['secondaryeffects']+=1
            if move_[0]=="status" or move_[0]=="start":
                target[move_[1]]=attacker['nickname']
        if line_[3].find('|Substitute') > -1:
            hittingsubstitute = True
    freezeclause = False
    if attackingteam == 'p1a':
        defendingteam = 'team2'
    if attackingteam == 'p2a':
        defendingteam = 'team1'
    for mon in results[defendingteam]['roster']:
        if mon['frz'] != None:
            freezeclause = True
    if secondaryEffectLanded == False and  hittingsubstitute == False and (move_[1] != 'frz' or freezeclause == False):
        results = luckappend(line, results, attacker,f"Mon did not land secondary effect from ({move})", -move_[3]*100)
        results = luckappend(line, results, target,f"Mon avoided secondary effect from ({move})", move_[3]*100)
    return results

def critChance_function(mon, increasedCrit):
    pokemonData = pokemonList[mon]
    if increasedCrit:
        critChance = pokemonData['BaseSpeed'] * 100/64
    else:
        critChance = pokemonData['BaseSpeed'] * 100/512
    if critChance > 100:
        critChance = 100
    return critChance

def crit_function(line,parsedlogfile,results, increasedRate):
    crittedteam=line[3].split(":",1)[0]
    crittedmon=line[3].split(" ",1)[1]
    crittedmon_=roster_search(crittedteam,crittedmon,results)
    turndata=list(filter(lambda x: x[1] == line[1] and x[0] < line[0], parsedlogfile))
    turndata=turndata[::-1]
    for line_ in turndata:
        if crittedteam=="p1a" and line_[2]=="move" and line_[3].split(":",1)[0]=="p2a" and line_[3].split("|")[2]==f"{crittedteam}: {crittedmon}":
            attackingteam="p2a"
            attacker=line_[3].split("|",1)[0].split(" ",1)[1]
            attacker=roster_search(attackingteam,attacker,results)
            results=luckappend(line,results,attacker,f"Mon landed a critical hit",100-critChance_function(attacker['pokemon'], increasedRate))
            results=luckappend(line,results,crittedmon_,f"Mon was hit by a critical hit",-(100-critChance_function(attacker['pokemon'], increasedRate)))
            move=line_[3].split("|")[1]
            notothermove=True
            if line_[3].find("[from]Mirror Move")>-1 or line_[3].find("[from]Mimic")>-1:
                notothermove=False
            if notothermove:
                attacker['moves'][move]['crits']+=1
            #results['significantevents'].append([line[1],f"LUCK: {attacker['pokemon']} landed a crit on {crittedmon_['pokemon']} with {move}"])
        elif crittedteam=="p2a" and line_[2]=="move" and line_[3].split(":",1)[0]=="p1a" and line_[3].split("|")[2]==f"{crittedteam}: {crittedmon}":
            attackingteam="p1a"
            attacker=line_[3].split("|",1)[0].split(" ",1)[1]
            attacker=roster_search(attackingteam,attacker,results)
            results = luckappend(line, results, attacker, f"Mon landed a critical hit",
                                 100 - critChance_function(attacker['pokemon'], increasedRate))
            results = luckappend(line, results, crittedmon_, f"Mon was hit by a critical hit",
                                 -(100 - critChance_function(attacker['pokemon'], increasedRate)))
            move=line_[3].split("|")[1]
            notothermove=True
            if line_[3].find("[from]Mirror Coat")>-1 or line_[3].find("[from]Mimic")>-1:
                notothermove=False
            if notothermove:
                attacker['moves'][move]['crits']+=1
            #results['significantevents'].append([line[1],f"LUCK: {attacker['pokemon']} landed a crit on {crittedmon_['pokemon']} with {move}"])
    return line,parsedlogfile,results
