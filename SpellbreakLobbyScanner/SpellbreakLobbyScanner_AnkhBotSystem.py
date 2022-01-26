import json
import os
import glob
import re

import clr
clr.AddReference("IronPython.SQLite.dll")
clr.AddReference("IronPython.Modules.dll")

#Script Infos
ScriptName = "SpellbreakLobbyScanner"
Website = "https://www.twitch.tv/almie__"
Description = "Gives you the amount of players in your spellbreak game."
Creator = "almie"
Version = "1.0.1"

#Globals
LOGS_FOLDER_PATH = r'%LOCALAPPDATA%\g3\Saved\Logs'
MATCH_START_STRING = 'InteractiveManager /Game/Maps/Longshot/Alpha/Alpha_Resculpt OnMatchStarted'
PLAYER_INFO_STRING = 'blob data for'
PORT_NUMBER_STRING = 'OnPartyTokenReceived'
PLAYER_DATA = None

class Rank(object):
    SORT_ORDER = ['Bronze', 'Silver', 'Gold', 'Platinum', 'Diamond', 'Legend']
    DISPLAY_EMOJI = {'Bronze': u'\U0001f7eb',
                    'Silver': u'\u2B1C',
                    'Gold': u'\U0001f7e8',
                    'Platinum': u'\U0001f4bf',
                    'Diamond': u'\U0001f48e',
                    'Legend': u'\U0001f451'}
    def __init__(self, name):
        self.name = name
        self.tier = name.split('_')[0]
        self.number = -1
        if self.name != 'Legend':
            self.number = name.split('_')[1]

    def displayName(self):
        if self.tier == 'Legend':
            return self.DISPLAY_EMOJI['Legend']
        else:
            return '{} {}'.format(self.DISPLAY_EMOJI[self.tier], self.number)

    def displayNameFull(self):
        if self.tier == 'Legend':
            return '{} Legend'.format(self.DISPLAY_EMOJI['Legend'])
        else:
            return '{} {} {}'.format(self.DISPLAY_EMOJI[self.tier], self.tier, self.number)

    def __str__(self):
        return self.name

    def __repr__(self):
        return 'Rank(name={})'.format(self.name)

    def __eq__(self, other):
        return self.name == other.name

    def __ne__(self, other):
        return not self.__eq__(other)

    def __gt__(self, other):
        if self.tier == other.tier:
            return self.number < other.number
        else:
            return self.SORT_ORDER.index(self.tier) > self.SORT_ORDER.index(other.tier)

    def __ge__(self, other):
        return self.__gt__(other) or self.__eq__(other)

    def __lt__(self, other):
        return not self.__ge__(other)

    def __le__(self, other):
        return not self.__gt__(other)

class Player(object):
    PLATFORMS = {'steam' : 'Steam', 'epic': 'Epic', 'xboxlive' : 'Xbox', 'psn' : 'PS', 'switch' : 'Switch'}
    def __init__(self, name, rank_solo='', rank_duo='', rank_squad=''):
        self.name = name
        self.rank_solo = rank_solo
        self.rank_duo = rank_duo
        self.rank_squad = rank_squad

        self.platform = ''

    def rank(self, gamemode):
        if gamemode == 'solo':
            return self.rank_solo
        elif gamemode == 'duo':
            return self.rank_duo
        elif gamemode == 'squad':
            return self.rank_squad

    def json_data(self):
        return {'name' : self.name,
                'rank_solo' : str(self.rank_solo),
                'rank_duo' : str(self.rank_duo),
                'rank_squad' : str(self.rank_squad),
                'platform': self.platform}

    @staticmethod
    def from_json(json_data):
        newPlayer = Player(json_data['name'], Rank(json_data['rank_solo']), Rank(json_data['rank_duo']), Rank(json_data['rank_squad']))
        newPlayer.platform = json_data.get('platform', '')
        return newPlayer
    @staticmethod
    def from_rawJson(json_data):
        newPlayer = Player(json_data['DisplayName'])
        newPlayer.rank_solo = Rank(json_data['LeagueTierIds']['UnrankedTierIds']['GameModeInfo:DA_BattleRoyale_Solo'].replace('LeagueTier:DA_LeagueTier_Unranked_Solo_', ''))
        newPlayer.rank_duo = Rank(json_data['LeagueTierIds']['UnrankedTierIds']['GameModeInfo:DA_BattleRoyale_Duo'].replace('LeagueTier:DA_LeagueTier_Unranked_Duo_', ''))
        newPlayer.rank_squad = Rank(json_data['LeagueTierIds']['UnrankedTierIds']['GameModeInfo:DA_BattleRoyale_Squad'].replace('LeagueTier:DA_LeagueTier_Unranked_Squad_', ''))
        newPlayer.platform = json_data['CurrentAccount'].split(':')[0]
        return newPlayer

class PlayerData(object):
    file_path = os.path.join(os.path.dirname(__file__), 'player_data.json')
    def __init__(self):
        self.players = []
        self.latestLogPath = ''

        self.currentGameMode = ''
        self.currentRegion = ''
        self.currentPort = ''

        self.queuePopped = False
        self.latestQueueTimestamp = ''
        self.latestMatchStartTimeStamp = ''
        self.queueCheckInProgress = False

    def writeData(self):
        json_data = {}

        #players
        json_data['players'] = []
        for player in self.players:
            json_data['players'].append(player.json_data())

        #log
        json_data['latestLogPath'] = self.latestLogPath

        #match info
        json_data['currentGameMode'] = self.currentGameMode
        json_data['currentRegion'] = self.currentRegion
        json_data['currentPort'] = self.currentPort

        json_data['latestQueueTimestamp'] = self.latestQueueTimestamp
        json_data['latestMatchStartTimeStamp'] = self.latestMatchStartTimeStamp

        with open(self.file_path, 'w') as f:
            json.dump(json_data, f)

    def readData(self):
        json_data = None
        with open(self.file_path, 'r') as f:
            try:
                json_data = json.load(f)
            except ValueError:
                return
        if not json_data:
            return

        #players
        self.players = []
        for json_player in json_data.get('players', []):
            self.players.append(Player.from_json(json_player))

        #log
        self.latestLogPath = json_data.get('latestLogPath', '')

        #match info
        self.currentGameMode = json_data.get('currentGameMode', '')
        self.currentRegion = json_data.get('currentRegion', '')
        self.currentPort = json_data.get('currentPort', '')

        self.latestQueueTimestamp = json_data.get('latestQueueTimestamp', '')
        self.latestMatchStartTimeStamp = json_data.get('latestMatchStartTimeStamp', '')


    def getLatestLogPath(self):
        log_files = glob.glob(os.path.expandvars(LOGS_FOLDER_PATH)+'\*log')
        latest_file = max(log_files, key=os.path.getctime)
        return latest_file

    def checkForQueuePop(self):
        self.queueCheckInProgress = True
        from datetime import datetime
        Parent.Log(ScriptName, '[{}] Check For Queue Pop - popped: {} - last queue: {} - last match: {}'.format(
            datetime.now().strftime("%H:%M:%S:%f"),
            str(self.queuePopped),
            self.latestQueueTimestamp,
            self.latestMatchStartTimeStamp
        ))
        import time
        time.sleep(0.25)
        with open(self.getLatestLogPath(), 'r') as f:
            logLines = f.readlines()
            for line in reversed(logLines):
                if line.count(PORT_NUMBER_STRING) > 0 and not self.queuePopped:
                    match = re.search("^\[([0-9\.:-]+)\].+OnPartyTokenReceived { Port => ([0-9]+)", line)
                    queueTimestamp = match.group(1)
                    if queueTimestamp <= self.latestQueueTimestamp:
                        break
                    self.latestQueueTimestamp = queueTimestamp
                    self.currentPort = match.group(2)
                    self.queuePopped = True
                    Parent.Log(ScriptName, "Queue Popped! (Port {})".format(self.currentPort))
                    Parent.SendTwitchMessage("Queue Popped! (Port {})".format(self.currentPort))
                    break
                if line.count(MATCH_START_STRING) > 0 and not self.queuePopped:
                    break
                if line.count(MATCH_START_STRING) > 0 and self.queuePopped:
                    self.newMatch()
        Parent.Log(ScriptName, '[{}] Check For Queue Pop DONE --------------------------------------- ---------------------------------- ------------------------------------------------'.format(datetime.now().strftime("%H:%M:%S:%f")))
        self.queueCheckInProgress = False

    def newMatch(self):
        self.players = []
        with open(self.getLatestLogPath(), 'r') as f:
            logLines = f.readlines()
            latestMatchFound = False
            for line in reversed(logLines):
                if line.count(MATCH_START_STRING) > 0 and not latestMatchFound:
                    latestMatchFound = True
                    match = re.search("^\[([0-9\.:-]+)\].+Alpha_Resculpt OnMatchStarted !json({.+})$", line)
                    matchStartTimeStamp = match.group(1)
                    if matchStartTimeStamp <= self.latestMatchStartTimeStamp:
                        return
                    self.latestMatchStartTimeStamp = matchStartTimeStamp
                    self.queuePopped = False
                    matchInfoRaw = json.loads(match.group(2))
                    self.currentGameMode = matchInfoRaw['game_mode']
                    self.currentRegion = matchInfoRaw['region']
                    continue
                if line.count(MATCH_START_STRING) > 0 and latestMatchFound:
                    break
                if line.count(PLAYER_INFO_STRING) > 0 and latestMatchFound:
                    match = re.search("blob data for .+: ({.+}) !json({.+})$", line)
                    playerInfoRaw = json.loads(match.group(1))
                    player = Player.from_rawJson(playerInfoRaw)
                    self.players.append(player)
                if line.count(PORT_NUMBER_STRING) > 0 and latestMatchFound:
                    match = re.search("^\[([0-9\.:-]+)\].+OnPartyTokenReceived { Port => ([0-9]+)", line)
                    self.latestQueueTimestamp = match.group(1)
                    self.currentPort = match.group(2)
        self.writeData()
        highestRank = max([pl.rank(self.currentGameMode) for pl in self.players])
        playersWithHighestRank = [pl for pl in self.players if pl.rank(self.currentGameMode) == highestRank]
        playersHighestText = 'players' if len(playersWithHighestRank) > 1 else 'player'
        Parent.SendTwitchMessage('New {mode} match with {pl} players on {region} (port {port})! The highest ranked {playertext} with {maxrank}: {maxrankname}'.format(
                                    mode=self.currentGameMode,
                                    pl=len(self.players),
                                    region=self.currentRegion,
                                    port=self.currentPort,
                                    playertext=playersHighestText,
                                    maxrank=highestRank.displayNameFull(),
                                    maxrankname=', '.join([pl.name for pl in playersWithHighestRank])
                                    ))
        Parent.Log(ScriptName, 'New {mode} match with {pl} players on {region} (port {port})! The highest ranked {playertext} with {maxrank}: {maxrankname}'.format(
                                    mode=self.currentGameMode,
                                    pl=len(self.players),
                                    region=self.currentRegion,
                                    port=self.currentPort,
                                    playertext=playersHighestText,
                                    maxrank=highestRank.displayNameFull(),
                                    maxrankname=', '.join([pl.name for pl in playersWithHighestRank])
                                    ))

        Parent.Log(ScriptName, str([(pl.name, pl.rank(self.currentGameMode)) for pl in self.players]))


#on script load/reload
def Init():
    global PLAYER_DATA
    PLAYER_DATA = PlayerData()
    PLAYER_DATA.readData()
    Parent.Log(ScriptName, 'Script Initialized')

#on command typed into twitch chat
def Execute(data):
    global PLAYER_DATA
    if data.IsChatMessage():
        Parent.Log(ScriptName, 'Execute Command {} {}'.format(data.GetParam(0), data.GetParam(1)))
        if data.GetParam(0) == "!sb": #and Parent.HasPermission(data.User, "moderator", "Get Spellbreak Lobby Information"):
            if data.GetParam(1) == "players":
                playersByRank = sorted(PLAYER_DATA.players, key=lambda pl: pl.rank(PLAYER_DATA.currentGameMode), reverse=True)
                Parent.SendTwitchMessage(' | '.join(["{0} ({1})".format(player.name, player.rank(PLAYER_DATA.currentGameMode).displayName()) for player in playersByRank]))
            if data.GetParam(1) == "ranks":
                Parent.SendTwitchMessage(', '.join(["{} - {}".format(Rank.DISPLAY_EMOJI[tier], tier) for tier in Rank.SORT_ORDER]))
            if data.GetParam(1) == "info":
                requestedUser = data.Message.replace("!sb info ", "")
                foundPlayer = None
                if requestedUser in [pl.name for pl in PLAYER_DATA.players]:
                    foundPlayer = PLAYER_DATA.players[[pl.name for pl in PLAYER_DATA.players].index(requestedUser)]
                else:
                    for player in PLAYER_DATA.players:
                        if requestedUser.lower() in player.name.lower():
                            foundPlayer = player
                            break
                if foundPlayer:
                    Parent.SendTwitchMessage("Info about {name} | {platform} | Ranks - BR Solo: {rank_solo}, BR Duo: {rank_duo}, BR Squad: {rank_squad}".format(
                                            name=foundPlayer.name,
                                            platform=foundPlayer.platform,
                                            rank_solo=foundPlayer.rank_solo.displayNameFull(),
                                            rank_duo=foundPlayer.rank_duo.displayNameFull(),
                                            rank_squad=foundPlayer.rank_squad.displayNameFull()))
                else:
                    Parent.SendTwitchMessage("Cound find player with the name {} in the current match.".format(requestedUser))
            if data.GetParam(1) == 'server':
                Parent.SendTwitchMessage('Current region: {} | Current port: {}'.format(PLAYER_DATA.currentRegion, PLAYER_DATA.currentPort))

#abc
def Tick():
    global PLAYER_DATA
    if not PLAYER_DATA.queueCheckInProgress:
        PLAYER_DATA.checkForQueuePop()
    return
