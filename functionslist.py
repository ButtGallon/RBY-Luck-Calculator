from luckfunctions import *
from pokemonlist import *

def activate_function(line, parsedlogfile, results):
    if line[3].split("|")[1] == "confusion":
        defendingteam = line[3].split(":", 1)[0]
        if defendingteam == "p1a":
            defender = roster_search(defendingteam, results['team1']['activemon'], results)
            attacker = roster_search("p2a", results['team2']['activemon'], results)
        elif defendingteam == "p2a":
            defender = roster_search(defendingteam, results['team2']['activemon'], results)
            attacker = roster_search("p1a", results['team1']['activemon'], results)
        results = luckappend(line, results, attacker, f"Mon is confused", -50)
        results = luckappend(line, results, defender, f"Opponent is confused", 50)
    return line, parsedlogfile, results


def boost_function(line, parsedlogfile, results):
    team = line[3].split(":")[0]
    mon = line[3].split(": ")[1].split("|")[0]
    stat = line[3].split("|")[1]
    boostnum = int(line[3].split("|")[2])
    mon = roster_search(team, mon, results)
    mon[stat] += boostnum
    return line, parsedlogfile, results


def cant_function(line, parsedlogfile, results):
    reason = line[3].split("|")[1]
    team = line[3].split(":")[0]
    pokemon = line[3].split("|")[0].split(": ")[1]
    pokemon = roster_search(team, pokemon, results)
    if team == "p1a":
        activemon = results['team2']['activemon']
        activemon = roster_search('p2a', activemon, results)
    elif team == "p2a":
        activemon = results['team1']['activemon']
        activemon = roster_search('p1a', activemon, results)
    if reason == "frz":
        pass
    elif reason == "par":
        results = luckappend(line, results, pokemon, f"Mon Could Not Move Due to Paralysis", -75)
        results = luckappend(line, results, activemon, f"Opponent Could Not Move Due to Paralysis", 75)
    return line, parsedlogfile, results


def curestatus_function(line, parsedlogfile, results):
    team = line[3].split(":", 1)[0]
    mon = line[3].split("|", 1)[0].split(" ", 1)[1]
    status = line[3].split("|")[1]
    try:
        mon = roster_search(team, mon, results)
        mon[status] = None
    except:
        turndata = list(
            filter(lambda x: x[1] == line[1] and x[0] < line[0] and x[2] in ["switch", "pull"], parsedlogfile))[::-1]
        for line_ in turndata:
            line_, parsedlogfile, results = switch_drag_function(line_, parsedlogfile, results)
        mon = roster_search(team, mon, results)
        mon[status] = None
    return line, parsedlogfile, results


def damage_function(line, parsedlogfile, results):
    team = line[3].split(":", 1)[0]
    if team == "p1a":
        otherteam = "p2a";
        otherteam_ = "team2";
        thisteam = "team1"
    elif team == "p2a":
        otherteam = "p1a";
        otherteam_ = "team1";
        thisteam = "team2"
    pokemon = line[3].split(" ", 1)[1].split("|")[0]
    healthremaining = int(line[3].split("|", 1)[1].split(" ", 1)[0].split("/", 1)[0].split("|", 1)[0])
    # searchroster
    pokemon = roster_search(team, pokemon, results)
    # redirect if no damage done
    if pokemon['remaininghealth'] == healthremaining:
        return line, parsedlogfile, results
    # update remaining health
    previoushealth = pokemon['remaininghealth']
    pokemon['remaininghealth'] = healthremaining
    damagedone = previoushealth - healthremaining
    # determine damager
    if line[3].find("[from]") > -1:
        # not direct damage
        cause = line[3].split("[from] ")[1].split('|')[0]
        damager = None;
        move = None
        if cause == "psn" and pokemon[cause] == None:
            cause = "tox"
        elif cause.find("Leech Seed") > -1 or cause.find("leechseed") > -1:
            damager = cause.split("|[of] ")[1].split(": ", 1)[1]
            team = cause.split("|[of] ")[1].split(": ", 1)[0]
            damager = roster_search(team, damager, results)
        elif cause in ['Recoil', 'recoil', 'High Jump Kick', 'highjumpkick', 'Jump Kick', 'jumpkick'] or cause.find("Recoil|[of] ") > -1 or cause.find(
                "recoil|[of] ") > -1:
            pokemon['hphealed'] += -damagedone
        else:
            if pokemon[cause] == pokemon['nickname'] :
                pokemon['hphealed'] += -damagedone
            else:
                damager = roster_search(otherteam, pokemon[cause], results)
        if damager:
            damager['damagedone'] += damagedone
        if cause == "confusion":
            activeopponent = roster_search(otherteam, results[otherteam_]['activemon'], results)
            # results['significantevents'].append([line[1],f"LUCK: {pokemon['pokemon']} hit itself in confusion caused by {pokemon['confusion']}."])
            results = luckappend(line, results, pokemon, f"Mon Hit Self In Confusion", -50)
            results = luckappend(line, results, activeopponent, f"Opponent Hit Self In Confusion", 50)
    else:
        # search for damager
        damager, move = damager_search(parsedlogfile, line, team, pokemon, results, damagedone)
    # update fainted
    if healthremaining == 0:
        pokemon['deaths'] = 1
        if damager and move:
            damager['kills'] += 1
            results['significantevents'].append(
                [line[1], f"{damager['pokemon']} killed {pokemon['pokemon']} with {move}"])
        elif damager and cause:
            damager['kills'] += 1
            results['significantevents'].append(
                [line[1], f"{damager['pokemon']} killed {pokemon['pokemon']} via {cause}"])
        else:
            results['significantevents'].append([line[1], f"{pokemon['pokemon']} fainted via {cause}"])
            results[thisteam]['selfdeaths'] += 1
    return line, parsedlogfile, results


def damager_search(parsedlogfile, line, team, pokemon, results, damagedone):
    damager = None
    move = None
    turndata = list(filter(lambda x: x[1] == line[1] and x[0] < line[0], parsedlogfile))[::-1]
    for line in turndata:
        if team == "p1a":
            if line[2] == "start" and line[3].find(f"p1a: {pokemon['nickname']}") > -1 and line[3].find(
                    "|Substitute") > -1:
                pokemon['hphealed'] += -damagedone
                break
            elif line[2] in ["move", "prepare"] and line[3].split(":", 1)[0] == "p2a" and line[3].find(
                    f"p1a: {pokemon['nickname']}") > -1:
                damager = line[3].split(" ", 1)[1].split("|", 1)[0]
                damager = roster_search("p2a", damager, results)
                damager['damagedone'] += damagedone
                move = line[3].split("|")[1]
                break
            elif line[2] in ["move", "prepare"] and line[3].split(":", 1)[0] == "p2a" and line[3].find("[still]") > -1:
                damager = line[3].split(" ", 1)[1].split("|", 1)[0]
                damager = roster_search("p2a", damager, results)
                damager['damagedone'] += damagedone
                move = line[3].split("|")[1]
                break
        elif team == "p2a":
            if line[2] == "start" and line[3].find(f"p2a: {pokemon['nickname']}") > -1 and line[3].find(
                    "|Substitute") > -1:
                pokemon['hphealed'] += -damagedone
                break
            elif line[2] in ["move", "prepare"] and line[3].split(":", 1)[0] == "p1a" and line[3].find(
                    f"p2a: {pokemon['nickname']}") > -1:
                damager = line[3].split(" ", 1)[1].split("|", 1)[0]
                damager = roster_search("p1a", damager, results)
                damager['damagedone'] += damagedone
                move = line[3].split("|")[1]
                break
            elif line[2] in ["move", "prepare"] and line[3].split(":", 1)[0] == "p1a" and line[3].find("[still]") > -1:
                damager = line[3].split(" ", 1)[1].split("|", 1)[0]
                damager = roster_search("p1a", damager, results)
                damager['damagedone'] += damagedone
                move = line[3].split("|")[1]
                break
    return damager, move


def detailschange_function(line, parsedlogfile, results):
    return line, parsedlogfile, results


def fieldstart_function(line, parsedlogfile, results):
    return line, parsedlogfile, results


def fieldend_function(line, parsedlogfile, results):
    return line, parsedlogfile, results


def heal_function(line, parsedlogfile, results):
    team = line[3].split(":", 1)[0]
    pokemon = line[3].split(" ", 1)[1].split("|")[0]
    healthremaining = int(line[3].split("|", 1)[1].split("/", 1)[0])
    # searchroster
    pokemon = roster_search(team, pokemon, results)
    # update remaining health
    previoushealth = pokemon['remaininghealth']
    pokemon['remaininghealth'] = healthremaining
    healthhealed = healthremaining - previoushealth
    # update health healed
    pokemon['hphealed'] += healthhealed
    return line, parsedlogfile, results


def message_function(line, parsedlogfile, results):
    line[3] = line[3].replace("lost due to inactivity.", "forfeited.")
    if line[3].find("forfeited.") > -1:
        ffcoach = line[3].split(" forfeited.")[0]
        if ffcoach == results['team1']['coach']:
            results['team1']['forfeit'] = 1
            lastactivemon = results['team2']['activemon']
            lastactivemon = roster_search('p2a', lastactivemon, results)
            for mon in results['team1']['roster']:
                if mon['deaths'] == 0:
                    lastactivemon['kills'] += 1
                mon['deaths'] = 1
        elif ffcoach == results['team2']['coach']:
            results['team2']['forfeit'] = 1
            lastactivemon = results['team1']['activemon']
            lastactivemon = roster_search('p1a', lastactivemon, results)
            for mon in results['team2']['roster']:
                if mon['deaths'] == 0:
                    lastactivemon['damagedone'] += mon['remaininghealth']
                    mon['remaininghealth'] = 0
                    lastactivemon['kills'] += 1
                    mon['deaths'] = 1
    return line, parsedlogfile, results


def move_function(line, parsedlogfile, results):
    # Check for wrap trapping
    if line[3].find("[from]Wrap") > -1 or line[3].find("[from]Fire Spin") > -1 or line[3].find("[from]Bind") > -1 or line[3].find("[from]Clamp") > -1:
        return line, parsedlogfile, results
    notothermove = True
    if line[3].find("[from]Mirror Move") > -1 or line[3].find("[from]Mimic") > -1:
        notothermove = False
    # parse line
    move = line[3].split("|")[1]
    attackingteam = line[3].split(":", 1)[0]
    attacker = line[3].split("|", 1)[0].split(" ", 1)[1]
    attacker = roster_search(attackingteam, attacker, results)
    try:
        defendingteam = line[3].split("|")[2].split(":", 1)[0]
        target = line[3].split("|")[2].split(" ", 1)[1]
        target = roster_search(defendingteam, target, results)
    except:
        defendingteam = None;
        target = None
    # append to movelist
    if move in attacker['moves'] and notothermove:
        attacker['moves'][move]['uses'] += 1
        attacker['moves'][move]['hits'] += 1
    elif notothermove:
        attacker['moves'][move] = {
            'uses': 1,
            'hits': 1,
            'crits': 0,
            'posssecondaryeffects': 0,
            'secondaryeffects': 0,
        }
    # check if paralyzed
    if attackingteam == "p1a":
        opponent = results['team2']['activemon']
        opponent = roster_search('p2a', opponent, results)
    elif attackingteam == "p2a":
        opponent = results['team1']['activemon']
        opponent = roster_search('p1a', opponent, results)
    if attacker['par'] != None:
        results = luckappend(line, results, attacker, f"Mon Broke Through Paralysis", 25)
        results = luckappend(line, results, opponent, f"Opponent Broke Through Paralysis", -25)

    # check for immunity
    turndata = list(filter(lambda x: x[1] == line[1] and x[0] > line[0], parsedlogfile))
    turndata_ = list(filter(lambda x: x[1] == line[1] and x[0] < line[0], parsedlogfile))
    notimmune = True
    targetalive = True
    movedfirst = True
    if line[3].find("[notarget]") > -1:
        targetmon = False
    else:
        targetmon = True
    try:
        for line_ in turndata:
            if line_[2] == "immune" and line_[3].find(defendingteam) > -1 and line_[3].find(target['nickname']) > -1:
                notimmune = False
            if line_[2] == "damage" and line_[3].find(defendingteam) > -1 and line_[3].find(target['nickname']) > -1 and \
                    line_[3].find("|0 fnt") > -1 and line_[3].find("[from]") == -1:
                targetalive = False
            if line_[2] in ['switch', 'drag'] and line_[3].find(attackingteam) > -1:
                break
        for line_ in turndata_:
            if line_[2] in ["move", "switch"] and line_[3].split(": ")[0] == defendingteam:
                movedfirst = False
    except:
        pass
    # support moves
    supportmoves = ['Haze', 'Leech Seed', 'Toxic', 'Stun Spore', 'Poison Powder',
                    'Disable', 'Glare', 'Hypnosis', 'Mist', 'Poison Gas',
                    'Sing', 'Sleep Powder', 'Spore', 'Thunder Wave']
    # check for support
    if move in supportmoves:
        attacker['support'] += 1
        results['significantevents'].append([line[1], f"{attacker['pokemon']} provided support by using {move}"])
    # moves that can miss
    movesthatcanmiss = dict([['Absorb', 100], ['Acid', 100],['Aurora Beam', 100], ['Barrage', 85],
                             ['Bind', 75], ['Bite', 100], ['Blizzard', 90], ['Body Slam', 100],
                             ['Bone Club', 85], ['Bonemerang', 90], ['Bubble', 100], ['Bubble Beam', 100],
                             ['Clamp', 75], ['Comet Punch', 85], ['Confuse Ray', 100], ['Confusion', 100],
                             ['Constrict', 100], ['Counter', 100], ['Crabhammer', 85], ['Cut', 95],
                             ['Dig', 100], ['Disable', 55], ['Dizzy Punch', 100], ['Double Kick', 100],
                             ['Double-Edge', 100], ['Double Slap', 85], ['Dragon Rage', 100], ['Dream Eater', 100],
                             ['Drill Peck', 100], ['Earthquake', 100], ['Egg Bomb', 75], ['Ember', 100],
                             ['Explosion', 100], ['Fire Blast', 85], ['Fire Punch', 100], ['Fire Spin', 70],
                             ['Fissure', 30], ['Flamethrower', 100], ['Flash', 70], ['Fly', 95],
                             ['Fury Attack', 85], ['Fury Swipes', 80], ['Glare', 75], ['Growl', 100],
                             ['Guillotine', 30], ['Gust', 100], ['Headbutt', 100], ['High Jump Kick', 90],
                             ['Horn Attack', 100], ['Horn Drill', 30], ['Hydro Pump', 80], ['Hyper Beam', 90],
                             ['Hyper Fang', 90], ['Hypnosis', 60], ['Ice Beam', 100], ['Ice Punch', 100],
                             ['Jump Kick', 95], ['Karate Chop', 100], ['Kinesis', 80], ['Leech Life', 100],
                             ['Leech Seed', 90], ['Leer', 100], ['Lick', 100], ['Lovely Kiss', 75],
                             ['Low Kick', 90], ['Mega Drain', 100], ['Mega Kick', 75], ['Mega Punch', 85],
                             ['Mimic', 100], ['Night Shade', 100], ['Pay Day', 100], ['Peck', 100],
                             ['Petal Dance', 100], ['Pin Missile', 85], ['Poison Gas', 55], ['Poison Sting', 100],
                             ['Poisonpowder', 75], ['Pound', 100], ['Psybeam', 100], ['Psychic', 100],
                             ['Psywave', 80], ['Quick Attack', 100], ['Rage', 100], ['Razor Leaf', 95],
                             ['Razor Wind', 75], ['Roar', 100], ['Rock Slide', 90], ['Rock Throw', 65],
                             ['Rolling Kick', 85], ['Sand-Attack', 100], ['Scratch', 100], ['Screech', 85],
                             ['Seismic Toss', 100], ['Selfdestruct', 100], ['Sing', 55], ['Skull Bash', 100],
                             ['Sky Attack', 90], ['Slam', 75], ['Slash', 100], ['Sleep Powder', 75],
                             ['Sludge', 100], ['Smog', 100], ['Smokescreen', 100], ['Solar Beam', 100],
                             ['Sonic Boom', 90], ['Spike Cannon', 100], ['Spore', 100], ['Stomp', 100],
                             ['Strength', 100], ['String Shot', 95], ['Struggle', 100], ['Stun Spore', 75],
                             ['Submission', 80], ['Super Fang', 90], ['Supersonic', 55], ['Surf', 100],
                             ['Tackle', 95], ['Tail Whip', 100], ['Take Down', 85], ['Thrash', 100],
                             ['Thunder', 70], ['Thunder Wave', 100], ['Thunderbolt', 100], ['Thunder Punch', 100],
                             ['Thunder Shock', 100], ['Toxic', 85], ['Tri Attack', 100], ['Twineedle', 100],
                             ['Vise Grip', 100], ['Vine Whip', 100], ['Water Gun', 100], ['Waterfall', 100],
                             ['Whirlwind', 100], ['Wing Attack', 100], ['Wrap', 85]])
    # check for miss
    movehit = True
    if line[3].find("|[miss]") > -1 and notimmune and targetmon:
        acc_modifier = accuracy_modifier(attacker['accuracy'], target['evasion'])
        results = miss_function(line, attacker, target, move, movesthatcanmiss[move]*acc_modifier, results)
        if notothermove:
            attacker['moves'][move]['hits'] += -1
        movehit = False
    # check if can miss
    if move in movesthatcanmiss.keys() and notimmune and targetmon and movehit:
        try:
            acc_modifier = accuracy_modifier(attacker['accuracy'], target['evasion'])
            results = luckappend(line, results, attacker, f"Mon did not miss ({move})",
                                 100 - min((movesthatcanmiss[move] * acc_modifier) - 0.39, 100))
            results = luckappend(line, results, target, f"Mon hit by ({move}) ",
                                 -(100 - min((movesthatcanmiss[move] * acc_modifier) - .39, 100)))
        except:
            pass
    # check if can crit
    movesthatcancrit = ['Absorb', 'Acid', 'Aurora Beam', 'Barrage', 'Barrier', 'Bind', 'Bite', 'Blizzard', 'Body Slam',
                        'Bone Club', 'Bonemerang', 'Bubble', 'Bubble Beam', 'Clamp', 'Comet Punch', 'Confusion',
                        'Constrict', 'Crabhammer', 'Cut', 'Dig', 'Dizzy Punch', 'Double Kick', 'Double Slap',
                        'Double-Edge', 'Dream Eater', 'Drill Peck', 'Earthquake', 'Egg Bomb', 'Ember', 'Explosion',
                        'Fire Blast', 'Fire Punch', 'Fire Spin', 'Flamethrower', 'Fly', 'Fury Attack', 'Fury Swipes',
                        'Gust', 'Headbutt', 'High Jump Kick', 'Horn Attack', 'Hydro Pump', 'Hyper Beam', 'Hyper Fang',
                        'Ice Beam', 'Ice Beam', 'Ice Punch', 'Jump Kick', 'Karate Chop', 'Leech Life', 'Lick',
                        'Low Kick', 'Mega Drain', 'Mega Kick', 'Mega Punch', 'Pay Day', 'Peck', 'Petal Dance',
                        'Pin Missile', 'Poison Sting', 'Pound', 'Psybeam', 'Psychic', 'Quick Attack', 'Rage',
                        'Razor Leaf', 'Razor Wind', 'Rock Slide', 'Rock Throw', 'Rolling Kick', 'Scratch', 'Self-Destruct',
                        'Skull Bash', 'Sky Attack', 'Slam', 'Slash', 'Sludge', 'Smog', 'Solar Beam', 'Spike Cannon',
                        'Stomp', 'Strength', 'Struggle', 'Submission', 'Surf', 'Swift', 'Tackle', 'Take Down', 'Thrash',
                        'Thunder', 'Thunder Punch', 'Thunder Shock', 'Thunderbolt', 'Tri Attack', 'Twineedle', 'Vine Whip',
                        'Vise Grip', 'Water Gun', 'Waterfall', 'Wing Attack', 'Wrap']
    increasedcrit = ['Crabhammer', 'Karate Chop', 'Razor Leaf', 'Slash']
    nextline = parsedlogfile[line[0]+1]
    if nextline[2] != 'crit':
        if move in increasedcrit and notimmune and targetmon and movehit:
            try:
                results = luckappend(line, results, attacker, f"Mon did not land a crit with ({move})", -critChance_function(attacker['pokemon'], True))
                results = luckappend(line, results, target, f"Mon was not crit by ({move})", critChance_function(attacker['pokemon'], True))
            except Exception as e:
                print(e)
        elif move in movesthatcancrit and notimmune and targetmon and movehit:
            try:
                results = luckappend(line, results, attacker, f"Mon did not land a crit with ({move})", -critChance_function(attacker['pokemon'], False))
                results = luckappend(line, results, target, f"Mon was not crit by ({move})", critChance_function(attacker['pokemon'], False))
            except:
                pass
    elif nextline[2] == 'crit':
        if move in increasedcrit and notimmune and targetmon and movehit:
            try:
                nextline, parsedlogfile, results = crit_function(nextline, parsedlogfile, results, True)
            except Exception as e:
                print(e)
        elif move in movesthatcancrit and notimmune and targetmon and movehit:
            try:
                nextline, parsedlogfile, results = crit_function(nextline, parsedlogfile, results, False)
            except:
                pass
    # moves with secondary effect
    statusdict = dict([['Blizzard', 'frz'], ['Body Slam', 'par'], ['Ember', 'brn'], ['Fire Blast', 'brn'],
                       ['Fire Punch', 'brn'], ['Flamethrower', 'brn'], ['Ice Beam', 'frz'], ['Ice Punch', 'frz'],
                       ['Lick', 'par'], ['Poison Sting', 'psn'], ['Sludge', 'psn'], ['Smog', 'psn'], ['Thunder', 'par'],
                       ['Thunderbolt', 'frz'], ['Thunder Punch', 'par'], ['Thunder Shock', 'par'], ['Twineedle', 'psn']])
    immunebytype = {
        'par': [],
        'brn': ['Arcanine', 'Charizard', 'Charmander', 'Charmeleon', 'Flareon', 'Growlithe',
                'Magmar', 'Moltres', 'Ninetales', 'Ponyta', 'Rapidash', 'Vulpix'],
        'psn': ['Arbok', 'Beedrill', 'Bellsprout', 'Bulbasaur', 'Ekans', 'Gastly', 'Gengar',
                'Gloom', 'Golbat', 'Grimer', 'Haunter', 'Ivysaur', 'Kakuna', 'Koffing', 'Muk',
                'Nidoking', 'Nidoqueen', 'Nidoran-F', 'Nidoran-M', 'Nidorina', 'Nidorino',
                'Oddish', 'Tentacool', 'Tentacruel', 'Venomoth', 'Venonat', 'Venusaur',
                'Victreebel', 'Vileplume', 'Weedle', 'Weepinbell', 'Weezing', 'Zubat'],
        'tox': ['Arbok', 'Beedrill', 'Bellsprout', 'Bulbasaur', 'Ekans', 'Gastly', 'Gengar',
                'Gloom', 'Golbat', 'Grimer', 'Haunter', 'Ivysaur', 'Kakuna', 'Koffing', 'Muk',
                'Nidoking', 'Nidoqueen', 'Nidoran-F', 'Nidoran-M', 'Nidorina', 'Nidorino',
                'Oddish', 'Tentacool', 'Tentacruel', 'Venomoth', 'Venonat', 'Venusaur',
                'Victreebel', 'Vileplume', 'Weedle', 'Weepinbell', 'Weezing', 'Zubat'],
        'frz': ['Articuno', 'Cloyster', 'Dewgong', 'Jynx', 'Lapras'],
        'slp': [],
    }
    immunebygen1 = {
        'Body Slam': ['Chansey', 'Clefable', 'Clefairy', 'Ditto', 'Dodrio', 'Doduo',
                      'Eevee', 'Farfetchd', 'Fearow', 'Jigglypuff', 'Kangaskhan',
                      'Lickitung', 'Meowth', 'Persian', 'Pidgeot', 'Pidgeotto',
                      'Pidgey', 'Porygon', 'Raticate', 'Rattata', 'Snorlax',
                      'Spearow', 'Tauros', 'Wigglytuff'],
        'Lick': ['Gastly', 'Haunter', 'Gengar'],
        'Thunder': ['Electabuzz', 'Electrode', 'Jolteon', 'Magnemite', 'Magneton',
                    'Pikachu', 'Raichu', 'Voltorb', 'Zapdos'],
        'Thunder Punch': ['Electabuzz', 'Electrode', 'Jolteon', 'Magnemite', 'Magneton',
                    'Pikachu', 'Raichu', 'Voltorb', 'Zapdos'],
        'Thunderbolt': ['Electabuzz', 'Electrode', 'Jolteon', 'Magnemite', 'Magneton',
                    'Pikachu', 'Raichu', 'Voltorb', 'Zapdos'],
        'Thunder Shock': ['Electabuzz', 'Electrode', 'Jolteon', 'Magnemite', 'Magneton',
                    'Pikachu', 'Raichu', 'Voltorb', 'Zapdos']
    }
    notimmunebytype = True
    notstatused = True
    turndata = list(filter(lambda x: x[1] == line[1] and x[0] > line[0], parsedlogfile))
    for line_ in turndata:
        if line_[2] == "curestatus":
            line_, parsedlogfile, results = curestatus_function(line_, parsedlogfile, results)
    if move in statusdict.keys() and (
            target['psn'] != None or target['tox'] != None or target['par'] != None or target['frz'] != None or target[
        'brn'] != None or target['slp'] != None):
        notstatused = False
    if move in statusdict.keys():
        status = statusdict[move]
        if target['pokemon'] in immunebytype[status]:
            notimmunebytype = False
        if (move in immunebygen1) and (target['pokemon'] in immunebygen1[move]):
            notimmunebytype = False
    moveswithsecondaryeffect = dict(
        [['Acid', 10], ['Aurora Beam', 10], ['Bite', 10], ['Blizzard', 10], ['Body Slam', 30], ['Bone Club', 10],
         ['Bubble', 10], ['Bubble Beam', 10], ['Confusion', 10], ['Constrict', 10], ['Ember', 10], ['Fire Blast', 30],
         ['Fire Punch', 10], ['Flamethrower', 10], ['Headbutt', 30], ['Hyper Fang', 10], ['Ice Beam', 10], ['Ice Punch', 10],
         ['Lick', 30], ['Low Kick', 30], ['Poison Sting', 20], ['Psybeam', 10], ['Psychic', 33], ['Rolling Kick', 30],
         ['Sludge', 30], ['Smog', 30], ['Stomp', 30], ['Thunder', 10], ['Thunderbolt', 10], ['Thunder Punch', 10],
         ['Thunder Shock', 10], ['Twineedle', 20]])
    flinchmoves = ['Bite', 'Bone Club', 'Headbutt', 'Hyper Fang', 'Low Kick', 'Rolling Kick', 'Stomp']
    if (move in moveswithsecondaryeffect.keys() and notimmune and notstatused and targetmon and notimmunebytype
            and movehit and targetalive and (movedfirst or move not in flinchmoves)):
        try:
            # check for secondary effect
            results = secondary_check(attacker, target, move, line, results, parsedlogfile, attackingteam, notothermove)
        except:
            pass
    # check for suicide moves
    if move in ["Explosion", "Self-Destruct"]:
        # search for miss
        turndata = list(filter(lambda x: x[1] == line[1] and x[0] > line[0], parsedlogfile))[::-1]
        miss = False
        if line[3].find("[notarget]") > -1:
            miss = True
        for line in turndata:
            if (line[2] == "miss" and line[3].split(": ")[0] == attackingteam) or (
                    line[2] == "immune" and line[3].split(": ")[0] == defendingteam):
                miss = True
        if miss == False or move in ["Explosion", "Self-Destruct"]:
            attacker['deaths'] += 1
            attacker['hphealed'] += -attacker['remaininghealth']
            attacker['remaininghealth'] = 0
            if attackingteam == "p1a":
                results['team1']['selfdeaths'] += 1
            elif attackingteam == "p2a":
                results['team2']['selfdeaths'] += 1
    return line, parsedlogfile, results


def player_function(line, parsedlogfile, results):
    if line[3].split("|", 1)[0] == "p1":
        results['team1']['coach'] = line[3].split("|")[1]
    elif line[3].split("|", 1)[0] == "p2":
        results['team2']['coach'] = line[3].split("|")[1]
    return line, parsedlogfile, results


def poke_function(line, parsedlogfile, results):
    adjustedmon = line[3].split("|")[1]
    if line[3].split("|", 1)[0] == "p1":
        results['team1']['roster'].append({
            'pokemon': line[3].split("|")[1], 'startform': adjustedmon, 'nickname': adjustedmon,
            'kills': 0, 'deaths': 0, 'causeofdeath': None, 'support': 0, 'damagedone': 0, 'hphealed': 0, 'luck': 0,
            'remaininghealth': 100, 'lines': [],
            'confusion': None, 'psn': None, 'brn': None, 'par': None, 'frz': None, 'tox': None, 'slp': None,
            'atk': 0, 'def': 0, 'spa': 0, 'spd': 0, 'spe': 0, 'accuracy': 0, 'evasion': 0,
            'Focus Energy': False, 'moves': {}
        })
    elif line[3].split("|", 1)[0] == "p2":
        results['team2']['roster'].append({
            'pokemon': line[3].split("|")[1], 'startform': adjustedmon, 'nickname': adjustedmon,
            'kills': 0, 'deaths': 0, 'causeofdeath': None, 'support': 0, 'damagedone': 0, 'hphealed': 0, 'luck': 0,
            'remaininghealth': 100, 'lines': [],
            'confusion': None, 'psn': None, 'brn': None, 'par': None, 'frz': None, 'tox': None, 'slp': None,
            'atk': 0, 'def': 0, 'spa': 0, 'spd': 0, 'spe': 0, 'accuracy': 0, 'evasion': 0,
            'Focus Energy': False, 'moves': {}
        })
    return line, parsedlogfile, results


def replace_function(line, parsedlogfile, results):
    # replaceteam=line[3].split(": ")[0]
    # replacenickname=line[3].split("|")[0].split(": ",1)[1]
    # replacemon=line[3].split("|")[1]
    # mon=roster_search(replaceteam,replacemon,results)
    # if mon!=replacemon:
    #    mon['nickname']=replacenickname
    return line, parsedlogfile, results

def sethp_function(line, parsedlogfile, results):
    if line[3].find("|[from] move: Pain Split") > -1 and len(line[3].split("|")) > 4:
        targetteam = line[3].split(":", 1)[0]
        target = line[3].split("|", 1)[0].split(" ", 1)[1]
        targethealth = int(line[3].split("|", 1)[1].split("/")[0])
        attackingteam = line[3].split("|")[2].split(":", 1)[0]
        attacker = line[3].split("|")[2].split(" ", 1)[1]
        attackerhealth = int(line[3].split("|")[3].split("/")[0])
        # find mons
        target = roster_search(targetteam, target, results)
        attacker = roster_search(attackingteam, attacker, results)
        targetstarthealth = target['remaininghealth']
        attacherstarthealth = attacker['remaininghealth']
        target['remaininghealth'] = targethealth
        attacker['remaininghealth'] = attackerhealth
        damagedone = targetstarthealth - targethealth
        hphealed = attackerhealth - attacherstarthealth
        attacker['damagedone'] += damagedone
        attacker['hphealed'] += hphealed
    elif line[3].find("|[from] move: Pain Split") > -1:
        setmon = line[3].split("|")[0].split(": ")[1]
        setmonhealth = int(line[3].split("|")[1].split("/")[0])
        # look up move data
        turndata = list(filter(lambda x: x[1] == line[1] and x[0] < line[0] and x[2] == "move", parsedlogfile))[::-1][0]
        targetteam = turndata[3].split("|")[2].split(": ", 1)[0]
        target = turndata[3].split("|")[2].split(": ", 1)[1]
        attackingteam = turndata[3].split(": ")[0]
        attacker = turndata[3].split("|")[0].split(": ", 1)[1]
        target_ = roster_search(targetteam, target, results)
        attacker_ = roster_search(attackingteam, attacker, results)
        targetstarthealth = target_['remaininghealth']
        attacherstarthealth = attacker_['remaininghealth']
        if setmon == target:
            target_['remaininghealth'] = setmonhealth
            damagedone = targetstarthealth - setmonhealth
            attacker_['damagedone'] += damagedone
        elif setmon == attacker:
            attacker_['remaininghealth'] = setmonhealth
            hphealed = setmonhealth - attacherstarthealth
            attacker_['hphealed'] += hphealed
    return line, parsedlogfile, results


def status_function(line, parsedlogfile, results):
    team = line[3].split(":", 1)[0]
    if team == "p1a":
        team_ = 'team1';
        otherteam = "p2a"
    elif team == "p2a":
        team_ = 'team2';
        otherteam = "p1a"
    mon = line[3].split("|", 1)[0].split(" ", 1)[1]
    status = line[3].split("|")[1]
    mon = roster_search(team, mon, results)
    if line[3].find("[from] move: Rest") > -1 and line[3].find("|slp") > -1:
        turndata = list(filter(lambda x: x[1] == line[1] and x[0] > line[0], parsedlogfile))
        for line_ in turndata:
            if line_[2] == "heal" and line_[3].find(mon['nickname']) > -1:
                mon['slp'] = mon['nickname']
                mon['tox'] = None;
                mon['psn'] = None;
                mon['brn'] = None;
                mon['frz'] = None;
                mon['par'] = None
    else:
        movesthatcausestatus = dict([
            ['tox', ['Toxic']],
            ['psn', ['Poison Powder', 'Poison Gas']],
            ['brn', []],
            ['par', ['Thunder Wave', 'Glare', 'Stun Spore']],
            ['slp', ['Spore', 'Sleep Powder', 'Hypnosis', 'Lovely Kiss', 'Sing']],
            ['frz', []]
        ])
        statusmoves = movesthatcausestatus[status]
        turndata = list(filter(lambda x: x[1] == line[1] and x[0] < line[0], parsedlogfile))
        turndata = turndata[::-1]
        for line_ in turndata:
            if line_[2] == "move":
                move = line_[3].split("|")[1]
                attackingteam = line_[3].split(":", 1)[0]
                attacker = line_[3].split("|", 1)[0].split(" ", 1)[1]
                if move in statusmoves and team != attackingteam:
                    mon[status] = attacker
                    break
    return line, parsedlogfile, results


def start_function(line, parsedlogfile, results):
    if len(results['team1']['roster']) == 0:
        results = team_search(parsedlogfile, results)
        return line, parsedlogfile, results
    if line[3].split("|")[1] == "confusion":
        mon = line[3].split("|")[0].split(": ")[1]
        team = line[3].split(": ")[0]
        mon_ = roster_search(team, mon, results)
        if line[3].find("[fatigue]") > -1:
            mon_['confusion'] = mon
        else:
            turndata = list(filter(lambda x: x[0] < line[0] and x[1] == line[1] and x[2] == "move", parsedlogfile))[
                       ::-1]
            movesthatconfuse = ['Confuse Ray','Supersonic']
            for line_ in turndata:
                move = line_[3].split("|")[1]
                team_ = line_[3].split(": ")[0]
                attacker = line_[3].split("|")[0].split(": ")[1]
                if move in movesthatconfuse and team_ != team:
                    mon_['confusion'] = attacker
    if line[3].find("Focus Energy") > -1:
        mon = line[3].split("|")[0].split(": ")[1]
        team = line[3].split(": ")[0]
        mon = roster_search(team, mon, results)
        mon['Focus Energy'] = True
    return line, parsedlogfile, results


def switch_drag_function(line, parsedlogfile, results):
    if line[3].split(":", 1)[0] == "p1a":
        for mon in results['team1']['roster']:
            mon['atk'] = 0;
            mon['def'] = 0;
            mon['spa'] = 0;
            mon['spe'] = 0;
            mon['accuracy'] = 0;
            mon['evasion'] = 0;
            mon['Focus Energy'] = False
        results, line = namecheck(results, line, 1)
    elif line[3].split(":", 1)[0] == "p2a":
        for mon in results['team2']['roster']:
            mon['atk'] = 0;
            mon['def'] = 0;
            mon['spa'] = 0;
            mon['spe'] = 0;
            mon['accuracy'] = 0;
            mon['evasion'] = 0;
            mon['Focus Energy'] = False
        results, line = namecheck(results, line, 2)
    return line, parsedlogfile, results


def alternate_switch_drag_function(line, parsedlogfile, results):
    if line[3].split(":", 1)[0] == "p1a":
        for mon in results['team1']['roster']:
            mon['atk'] = 0;
            mon['def'] = 0;
            mon['spa'] = 0;
            mon['spd'] = 0;
            mon['spe'] = 0;
            mon['accuracy'] = 0;
            mon['evasion'] = 0;
            mon['Focus Energy'] = False
            if mon['pokemon'] in ['Chansey', 'Blissey', 'Starmie', 'Celebi', 'Roselia', 'Swablu', 'Altaria', 'Budew',
                                  'Happiny', 'Shaymin']:
                results, mon = reset_status(results, mon)
        results, line = namecheck(results, line, 1)
    elif line[3].split(":", 1)[0] == "p2a":
        for mon in results['team2']['roster']:
            mon['atk'] = 0;
            mon['def'] = 0;
            mon['spa'] = 0;
            mon['spd'] = 0;
            mon['spe'] = 0;
            mon['accuracy'] = 0;
            mon['evasion'] = 0;
            mon['Focus Energy'] = False
            if mon['pokemon'] in ['Chansey', 'Blissey', 'Starmie', 'Celebi', 'Roselia', 'Swablu', 'Altaria', 'Budew',
                                  'Happiny', 'Shaymin']:
                results, mon = reset_status(results, mon)
        results, line = namecheck(results, line, 2)
    return line, parsedlogfile, results


def reset_status(results, mon):
    mon['tox'] = None
    mon['psn'] = None
    mon['brn'] = None
    mon['par'] = None
    mon['slp'] = None
    mon['frz'] = None
    return results, mon


def unboost_function(line, parsedlogfile, results):
    team = line[3].split(":")[0]
    mon = line[3].split(": ")[1].split("|")[0]
    stat = line[3].split("|")[1]
    boostnum = int(line[3].split("|")[2])
    mon = roster_search(team, mon, results)
    mon[stat] += -boostnum
    return line, parsedlogfile, results


def weather_function(line, parsedlogfile, results):

    return line, parsedlogfile, results


def win_function(line, parsedlogfile, results):
    winner = line[3]
    if winner == results['team1']['coach']:
        results['team1']['wins'] = 1
    elif winner == results['team2']['coach']:
        results['team2']['wins'] = 1
    return line, parsedlogfile, results


def zpower_function(line, parsedlogfile, results):

    return line, parsedlogfile, results


def namecheck(results, line, teamnumber):
    nicknamesearch = line[3].split(" ", 1)[1].split("|")
    healthremaining = int(line[3].split("|")[2].split("/", 1)[0])
    if nicknamesearch[0] != nicknamesearch[1] and nicknamesearch[1].find(f"{nicknamesearch[0]}-") == -1:
        for item in results[f'team{teamnumber}']['roster']:
            if item['pokemon'] == nicknamesearch[1]:
                item['nickname'] = nicknamesearch[0]
                priorhealth = item['remaininghealth']
                item['hphealed'] += healthremaining - priorhealth
                item['remaininghealth'] = healthremaining
    else:
        for item in results[f'team{teamnumber}']['roster']:
            if item['pokemon'] == nicknamesearch[1] == -1:
                item['startform'] = nicknamesearch[0]
                item['nickname'] = nicknamesearch[0]
                priorhealth = item['remaininghealth']
                item['hphealed'] += healthremaining - priorhealth
                item['remaininghealth'] = healthremaining
    results[f'team{teamnumber}']['activemon'] = nicknamesearch[0]
    if line[2] == "switch":
        results[f'team{teamnumber}']['timesswitched'] += 1
    return results, line

def initializeoutput():
    # initialize output json
    results = {}
    results['team1'] = {}
    results['team2'] = {}
    results['team1']['coach'] = ""
    results['team2']['coach'] = ""
    results['team1']['roster'] = []
    results['team2']['roster'] = []
    results['team1']['wins'] = 0
    results['team2']['wins'] = 0
    results['team1']['forfeit'] = 0
    results['team2']['forfeit'] = 0
    results['team1']['score'] = 0
    results['team2']['score'] = 0
    results['team1']['timesswitched'] = -1
    results['team2']['timesswitched'] = -1
    results['team1']['selfdeaths'] = 0
    results['team2']['selfdeaths'] = 0
    results['team1']['remaininghealth'] = 0
    results['team2']['remaininghealth'] = 0
    results['team1']['totalhealth'] = 0
    results['team2']['totalhealth'] = 0
    results['team1']['kills'] = 0
    results['team2']['kills'] = 0
    results['team1']['deaths'] = 0
    results['team2']['deaths'] = 0
    results['team1']['luck'] = 0
    results['team2']['luck'] = 0
    results['team1']['damagedone'] = 0
    results['team2']['damagedone'] = 0
    results['team1']['hphealed'] = 0
    results['team2']['hphealed'] = 0
    results['team1']['support'] = 0
    results['team2']['support'] = 0
    results['team1']['activemon'] = None
    results['team2']['activemon'] = None
    results['team1']['Leech Seed'] = None
    results['team2']['Leech Seed'] = None
    results['numberofturns'] = 0
    results['turns'] = []
    results['replay'] = ""
    results['significantevents'] = []
    results['luckcatalog'] = []
    results['errormessage'] = []
    return results


def roster_search(team, pokemon, results):
    if team == "p1a":
        team = "team1"
    elif team == "p2a":
        team = "team2"
    if team == "p1":
        team = "team1"
    elif team == "p2":
        team = "team2"
    match = False
    for mon in results[team]['roster']:
        if mon['nickname'] == pokemon:
            pokemon = mon
            match = True
            break
    if match == False:
        for mon in results[team]['roster']:
            if mon['nickname'].find(pokemon) > -1:
                pokemon = mon
                match = True
                break
    return pokemon

def pokemon_in_team(team, pokemon, results):
    if team == "p1a":
        team = "team1"
    elif team == "p2a":
        team = "team2"
    if team == "p1":
        team = "team1"
    elif team == "p2":
        team = "team2"
    match = False
    for mon in results[team]['roster']:
        if mon['pokemon'] == pokemon:
            pokemon = mon['pokemon']
            match = True
            break
    if match == False:
        for mon in results[team]['roster']:
            if mon['pokemon'].find(pokemon) > -1:
                pokemon = mon['pokemon']
                match = True
                break
    return match

def team_search(parsedlogfile, results):

    for line in parsedlogfile:
        if line[3][:3] == 'p1a' and line[2] == 'switch':
            adjustedmon = line[3].split("|")[1]
            nickname = line[3].split("|")[0].split(": ", )[1]
            if len(results['team1']['roster']) == 0 or pokemon_in_team('team1', adjustedmon, results) == False:
                results['team1']['roster'].append({
                    'pokemon': adjustedmon, 'startform': adjustedmon, 'nickname': nickname,
                    'kills': 0, 'deaths': 0, 'causeofdeath': None, 'support': 0, 'damagedone': 0, 'hphealed': 0,
                    'luck': 0,
                    'remaininghealth': 100, 'lines': [],
                    'confusion': None, 'psn': None, 'brn': None, 'par': None, 'frz': None, 'tox': None, 'slp': None,
                    'atk': 0, 'def': 0, 'spa': 0, 'spd': 0, 'spe': 0, 'accuracy': 0, 'evasion': 0,
                    'Focus Energy': False, 'moves': {}
                })
        elif line[3][:3] == 'p2a' and line[2] == 'switch':
            adjustedmon = line[3].split("|")[1]
            nickname = line[3].split("|")[0].split(": ", )[1]
            if len(results['team2']['roster']) == 0 or pokemon_in_team('team2', adjustedmon, results) == False:
                results['team2']['roster'].append({
                    'pokemon': adjustedmon, 'startform': adjustedmon, 'nickname': nickname,
                    'kills': 0, 'deaths': 0, 'causeofdeath': None, 'support': 0, 'damagedone': 0, 'hphealed': 0,
                    'luck': 0,
                    'remaininghealth': 100, 'lines': [],
                    'confusion': None, 'psn': None, 'brn': None, 'par': None, 'frz': None, 'tox': None, 'slp': None,
                    'atk': 0, 'def': 0, 'spa': 0, 'spd': 0, 'spe': 0, 'accuracy': 0, 'evasion': 0,
                    'Focus Energy': False, 'moves': {}
                })

    return results

def accuracy_modifier(accuracy, evasion):
    accuracy = accuracy_chart(accuracy)
    evasion = accuracy_chart(evasion)
    return accuracy / evasion


def accuracy_chart(boost):
    if boost == -6:
        return .333
    elif boost == -5:
        return .375
    elif boost == -4:
        return .429
    elif boost == -3:
        return .50
    elif boost == -2:
        return .60
    elif boost == -1:
        return .75
    elif boost == 0:
        return 1
    elif boost == 1:
        return 1.333
    elif boost == 2:
        return 1.667
    elif boost == 3:
        return 2
    elif boost == 4:
        return 2.333
    elif boost == 5:
        return 2.667
    elif boost == 6:
        return 3