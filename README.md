# Artemis Cosmos Eastern Front Mod
Mod for the Artemis Cosmos Spaceship Bridge Simulator game that provides pirate-related features. Primarily for use by the Eastern Front online group.

###  To download the latest version:
1) Go to https://github.com/quaris628/ArtemisEasternFrontMod/releases/latest
2) Download the "Source Code" zip file.

### To install:

If you are using linux or configured your filesystem to be case-sensitive (if you don't know what this means then you can almost certainly ignore this): Before you install this mod, open your vanilla install's `data/missions/` directory, and check its subfolders' capitalization. If the names contain uppercase letters, then change them to lowercase letters (for example, change "LegendaryMissions" to "legendarymissions"). (Why this is necessary: vanilla issue [#698](https://github.com/artemis-sbs/LegendaryMissions/issues/698) .) There's no need to do this for subfolders of subfolders.

In short, you need to overwrite the vanilla game's files with the mod's files.
In more detail...
1) Unzip the mod files (in windows, right-click the zip file you downloaded, then select "Extract All...")
2) Browse to your Artemis Cosmos folder that contains the game files that you wish to apply this mod to. (If you bought Artemis Cosmos through Steam, you can open this folder by: starting in your Library window, right-click Artemis Cosmos in the list of your games, hover over "Manage", then select "Browse local files".)
3) Optional, but strongly recommended: Create a backup copy of your entire Artemis Cosmos folder.
4) Take the mod files you extracted and copy them into your Artemis Cosmos folder, such that the mod files overwrite the vanilla files. (Copying the sbs_utils and data folders are all that's necessary for the mod to work, but you should also copy at least the license file and maybe the readme file too.)
5) A window should appear that says the destination already has files with the same names. (If this doesn't happen, then something went wrong in step 4.) When this happens, choose to replace the files in the destination.
If installation was successful, then when the game window opens you should see this mod's name and version beside the Cosmos logo.

"Do I need to install this mod for clients, or just the server?" - You must install on all clients, and the server.

### To report bugs, give feedback, etc:

If you believe the bug/feedback/etc is only pertinent to this mod, then create a public issue on github ( https://github.com/quaris628/ArtemisCosmosEasternFrontMod/issues ) or you may privately email me at `quaris314@gmail.com`.
If this is about a crash or other bug you encountered during a specific game session, then uploading the log file(s) for that session might help diagnose the issue. You can find log files inside a /q_logs/ folder inside the folder of the mission you ran (for example, data/missions/legendarymissions/q_logs/). The timestamps in their names are when the mission was initialized (or restarted).

If you believe the bug/feedback/etc is only pertinent to vanilla Artemis Cosmos, then create a github issue here: https://github.com/artemis-sbs/LegendaryMissions/issues

If you are unsure whether the bug/feedback/etc is pertinent to this mod or vanilla, then assume it's pertinent to this mod; I should be able to sort out which is which, and if it's vanilla I'll forward it.

# List of features:

Pirates
- Added the following Pirate player ship types
  - Advanced Longbow
  - Toranado
  - Pirate Bulk Cargo
  - Pirate Science Vessel
  - GrayBeard's Ghost
- Added the following pirate docking stations
  - Smuggler's Den
    - Unarmed
	- Always allows Pirates, TSN civilian, CAP, and Ximni player ships to dock
	- Never allows TSN military player ships to dock
    - Does not supply nukes or mines to TSN civilian player ships
  - ShoShuShen
    - Armed
	- Always allows Pirates, TSN military, CAP, and Ximni player ships to dock
	- Never allows TSN civilian player ships to dock
    - Does not supply nukes or mines to TSN military player ships
    - Each game will have at most one ShoShuShen station
- Pirate player ships start near pirate stations, when possible
- Added the following pirate NPC ships:
  - Bulk Cargo
  - Science Vessel
  - Strongbow
  - Longbow

Civilian Air Patrol
- Added the following CAP player ship type
  - Jager
- CAP player ships may loot, like Pirate player ships
- CAP player ships may always dock at TSN stations, like TSN player ships

TSN
- Made the following TSN player ship types salvaged (worsen their beam damage and energy efficiency by 10%)
  - Light Cruiser
  - Battle Cruiser
  - Carrier
  - Light Carrier
  - Battleship
  - Warpster
  - Missle Cruiser
  - Destroyer (also renamed to Milita Enforcer)
  - Escort (also renamed to Milita Escort)
  - Heavy Cruiser
  - Scout
- Disabled the following TSN player ship types
  - Mine Layer
  - Juggernaut
  - Dreadnought
- TSN Bomber no longer carries nukes and can only carry 5 mines
- Rename TSN and civilian vessel types to civil militia (-related) names
  - Destroyer renamed to Militia Enforcer
  - Escort renamed to Militia Escort
  - Luxury Liner renamed to Colony Ship
  - Command Starbase renamed to Local Militia Command
- Reduced TSN Transport speed from 1.0 to 0.8
- TSN player ships start near TSN stations, when possible
- In peacetime, DS1 is always a TSN command station (to prevent issues with the ambassador quest)

Neutral Civilians
- Added the following Neutral Civilian station type
  - Salvage Yard
  - Unarmed
    - Scattered around the Salvage Yard station are wrecks and derelict ships
    - Never allows TSN military ships to dock
    - All non-TSN-military player ships start the game with permission to dock
    - Salvage Yards get angry at ships who destroy their wrecks or derelict ships
    - If a Salvage Yard gets angry enough at a player ship, then they ban that player ship from docking
    - One Salvage Yard banning a player makes other Salvage Yards more angry at the player
    - Does not supply nukes or mines to Pirate player ships
- A pirate player ship who destroys a Neutral Civilian vessel gets permabanned from TSN stations

Single-seat craft docking permissions
- Single-seat craft whose mothership is a player ship may only dock where their mothership always has been and always will be able to dock at
  - For example: A Pirate Adventure shuttle cannot dock at a TSN Science Station, because its Pirate mothership wasn't always able to dock at the TSN Science station, and might not be able to in the future either.
- Single-seat craft whose mothership is a Pirate station may only dock at Pirate player ships and stations
- Single-seat craft whose mothership is a TSN or civilian station may only dock at TSN or civilian player ships and stations
- Single-seat craft may only change their mothership to a ship or station that they can dock at

Pirate-TSN Relations
- Pirate player ships that do not have permission to dock at TSN stations cannot successfully give orders to TSN NPC ships
- TSN player ships cannot successfully give orders to pirate NPC ships and stations
- Pirate single-seat craft whose mothership is a pirate docking station will have their enemy kills rewarded by the TSN gifting ordinance to that docking station

Scramble:
- Scramble mode can be toggled from the game setup screen's player ships tab, and the default is configurable in settings.yaml
- When Scramble mode is enabled:
  - On the console selection screen, player ship names and classes will be hidden, and some text describing the scramble situation shows at the top of the screen
 - On the game setup screen's player ships tab, buttons will show that, when
   clicked, randomize player ship names and classes
 - When the game starts, players won't start right away. Other in-game events
   will happen, such as enemies advancing on friendly bases. The players only
   start after a certain amount of time, or when the "Scramble now!" button on
   the server mainscreen (or in operator mode, the gamemaster screen) is clicked.
 - How long the game runs before the players start the game can be changed on the game setup screen, and after the game has started the delay can be made longer or cut short from the server mainscreen or a gamemaster client
 - When players start, the red alert siren will sound
 - If there is a player ship that can loot and all bases get destroyed, then the
   game ends instead of continuing like it normally would
- These are configurable in settings.yaml:
  - Whether scramble mode is enabled by default
  - The default delay before players start the game
  - Whether the red alert siren sounds when players start

Misc:
- GUI colors are rusy red and orange
- Reduce Mine damage by 25% (from 8 to 6)
- Set the default player ships to the following
  - Ship 1: Pirate Strongbow named Farside
  - Ship 2: Pirate Brigantine named Fulminatae
  - Ship 3: Pirate Advanced Longbow named Jimi-Saru
  - Ship 4: Pirate Toranado named Apocalypse
  - Ship 5: TSN Light Cruiser name Academia
  - Ship 6: Pirate Bulk Cargo named Rum Runner
  - Ship 7: CAP Jager named Broadsides
  - Ship 8: Pirate GrayBeard's Ghost named GrayBeard's Ghost
- Differentiate front and rear shield icons on internal engineering grid (vanilla feature request (197)[https://github.com/artemis-sbs/LegendaryMissions/issues/197])
- Mirror beam icon for starboard-side beams on internal engineering grid (for pirate ships only)

These independent mods are included:
- [Comprehensive Enhancements Mod](https://github.com/quaris628/ArtemisCosmosComprehensiveEnhancementsMod) v0.4, which includes these independent mods:
  - [Unofficial Patch](https://github.com/quaris628/ArtemisCosmosUnofficialPatch) v1.12
  - [Cheery Beeps Mod](https://github.com/quaris628/ArtemisCosmosCheeryBeepsMod) v1.2

#  Compatibility:

Supported vanilla versions:
- 1.3.0

Mission Compatibility:

Mission | Is it ok to run this mission with this mod installed? | Does the Eastern Front Mod work? | Comments
--- | --- | --- | ---
[Legendary Missions](https://github.com/artemis-sbs/LegendaryMissions) | Yes | Yes |
[Secret Meeting](https://github.com/artemis-sbs/SecretMeeting) | Yes | Yes |
[Walk The Line](https://github.com/artemis-sbs/WalkTheLine) | Yes | Yes |
[remote_mssion_pick](https://github.com/artemis-sbs/remote_mission_pick) | Yes | Yes | Other missions started via remote_mission_pick will have the same compatibility as if they were started via any other way.
All Others | No | - |

Mod compatibility:

Mod (& version) | Is it ok to install both mods? | In what order should they be installed? | Would the Eastern Front Mod work? | Comments
--- | --- | --- | --- | ---
[Unofficial Patch](https://github.com/quaris628/ArtemisCosmosUnofficialPatch) v1.12 | Yes, but there's no reason to | Unofficial Patch first, Eastern Front Mod second | Yes | The Eastern Front Mod already includes the Unofficial Patch
[Cheery Beeps Mod](https://github.com/quaris628/ArtemisCosmosCheeryBeepsMod) any version | Yes, but there's no reason to | Any | Yes | The Eastern Front Mod already includes the Cheery Beeps Mod
[Comprehensive Enhancements Mod](https://github.com/quaris628/ArtemisCosmosComprehensiveEnhancementsMod) v0.4 | Yes, but there's no reason to | Comprehensive Enhancements Mod first, Eastern Front Mod second | Yes | The Eastern Front Mod already includes the Comprehensive Enhancements Mod
[TSN Mod](https://github.com/tsnrp/TSN-Cosmos-Mod) Conversion | No | - | - |
[TNG Mod](https://github.com/ScornMandark/Cosmos-TNG-Mod) v0.2.3 | No | - | - |
[Anime Fan Mod](https://artemis.forumchitchat.com/post/cosmos-anime-fan-mod-13799377?pid=1344460893) | No | - | - |

Disclaimer: I have not tested every mod and mission combination. Instead, this compatibility information is simply based on which files are modified/provided by each mod or mission. While this should be mostly accurate, there's a chance you'll run into problems with a mod combination even if this table claims it's compatible.

# Credits

Contributors:
- Quaris - General mission scripting, porting ship types from EF mod v3.5
- PirateLord - Graphics assets, gameplay design and balance
- Bassellope - Reorienting beams concept

Mission scripting assistance from:
- Doug Reichard
- Astrolamb
- Bassellope

Playtesting and feedback:
- PirateLord
- Bassellope
- Gypsyjuggler
- Bart
- Asiansnowman
- steveoe
- Dave Trinh
- PoingFerret
- TroyDThompson
- Liberty4All
- VonErebos

Special thanks to:
- Thom Robertson for sharing development versions of Artemis Cosmos
- Bassellope for hosting playtests
