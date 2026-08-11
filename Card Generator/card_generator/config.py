from pathlib import Path

# Generator Settings
GALACTIC_ENCOUNTER_TIERS = ['grunt', 'commander', 'boss']
DARK_BASE_ENCOUNTER_TIERS = GALACTIC_ENCOUNTER_TIERS + ['ultra_burst','Falkner', 'Bugsy', 'Whitney', 'Morty', 'Chuck', 'Jasmine', 'Pryce', 'Clair', 'Weak Grunt', 'Moderate Grunt', 'Strong Grunt', 'Weak Ace', 'Moderate Ace', 'Strong Ace', 'Weak Plasma Grunt', 'Moderate Plasma Grunt', 'Strong Plasma Grunt', 'Weak Plasma Ace', 'Moderate Plasma Ace', 'Strong Plasma Ace','Palmer', 'Thorton', 'Dahlia', 'Darach', 'Argenta', 'Caitlin', 'Flannery', 'Wattson', 'Juan', 'Sidney', 'Norman', 'Winona', 'Mars', 'Jupiter', 'Saturn', 'Sird', 'Charon', 'Cyrus', 'Proton', 'Ariana', 'Archer', 'Will', 'Koga', 'Bruno', 'Karen', 'Lance', 'Queen', 'Colress']
SPECIFIC_HELD_ITEM_BASE_LOOKUP = {
    'scroll_of_nobility': ['Noble Form'],
    'Adamant Crystal': ['Adamant Origin Forme'],
    'Blue Orb': ['Alpha Primal Forme'],
    'Cornerstone Mask': ['Cornerstone Mask'],
    'DNA Splicer': ['Black DnA', 'White DnA'],
    'Gracidae Flower': ['Sky Forme'],
    'Griseous Orb': ['Griseous Origin Forme'],
    'Hearthflame Mask': ['Hearthflame Mask'],
    'Jade Orb': ['Delta Mega Forme'],
    'Lustrous Globe': ['Lustrous Origin Forme'],
    'Meteorite': ['Attack Forme', 'Defense Forme', 'Speed Forme'],
    'N-Lunarizer': ['Dawn Wings'],
    'N-Solarizer': ['Dusk Mane'],
    'Prison Bottle': ['Unbound Forme'],
    'Red Orb': ['Omega Primal Forme'],
    'Reins of Unity': ['Ice Rider', 'Shadow Rider'],
    'Reveal Glass': ['Therian Forme'],
    'Rusted Shield': ['Crowned Shield'],
    'Rusted Sword': ['Crowned Sword'],
    'Scroll of Power': ['Single Strike Style', 'Rapid Strike Style'],
    'Secret Key': ['Frost Forme', 'Fan Forme', 'Heat Forme', 'Mow Forme', 'Wash Forme'],
    'Wellspring Mask': ['Wellspring Mask'],
    'Dynamax Band': ['Gigantamax Form'],
    'Mega Stone': ['Mega Form', 'Mega Form X', 'Mega Form Y'],
    'Ultranecrozium Z': ['Ultra'],
    'Zygarde Cube': ['50% Forme', 'Complete Forme']
}

# File Paths
COMPONENT_DIR = Path(__file__).parent
ROOT_DIR = COMPONENT_DIR.parent
CARD_ASSETS_DIR = COMPONENT_DIR.parent / 'generator_assets'
OUTPUT_DIR = COMPONENT_DIR / 'output'
DECK_OBJECT_OUTPUT_DIR = OUTPUT_DIR / 'Deck Objects'
ABILITY_MOVES_OUTPUT_DIR = OUTPUT_DIR / 'abilities' / 'moves'
ABILITY_CARD_FRONTS_OUTPUT_DIR = OUTPUT_DIR / 'abilities' / 'card_fronts'
ABILITY_CARD_BACKS_OUTPUT_DIR = OUTPUT_DIR / 'abilities' / 'card_backs'
ABILITY_DECKS_OUTPUT_DIR = OUTPUT_DIR / 'abilities' / 'decks'
CHANCE_CARD_FRONTS_OUTPUT_DIR = OUTPUT_DIR / 'chance' / 'card_fronts'
CHANCE_CARD_BACKS_OUTPUT_DIR = OUTPUT_DIR / 'chance' / 'card_backs'
CHANCE_DECKS_OUTPUT_DIR = OUTPUT_DIR / 'chance' / 'decks'
DISASTER_CARD_FRONTS_OUTPUT_DIR = OUTPUT_DIR / 'disaster' / 'card_fronts'
DISASTER_CARD_BACKS_OUTPUT_DIR = OUTPUT_DIR / 'disaster' / 'card_backs'
DISASTER_DECKS_OUTPUT_DIR = OUTPUT_DIR / 'disaster' / 'decks'
EXCAVATED_CARD_FRONTS_OUTPUT_DIR = OUTPUT_DIR / 'excavated' / 'card_fronts'
EXCAVATED_CARD_BACKS_OUTPUT_DIR = OUTPUT_DIR / 'excavated' / 'card_backs'
EXCAVATED_DECKS_OUTPUT_DIR = OUTPUT_DIR / 'excavated' / 'decks'
FORTUNE_CARD_FRONTS_OUTPUT_DIR = OUTPUT_DIR / 'fortune' / 'card_fronts'
FORTUNE_CARD_BACKS_OUTPUT_DIR = OUTPUT_DIR / 'fortune' / 'card_backs'
FORTUNE_DECKS_OUTPUT_DIR = OUTPUT_DIR / 'fortune' / 'decks'
INFLUENCE_CARD_FRONTS_OUTPUT_DIR = OUTPUT_DIR / 'influence' / 'card_fronts'
INFLUENCE_CARD_BACKS_OUTPUT_DIR = OUTPUT_DIR / 'influence' / 'card_backs'
INFLUENCE_DECKS_OUTPUT_DIR = OUTPUT_DIR / 'influence' / 'decks'
LEGENDS_CARD_FRONTS_OUTPUT_DIR = OUTPUT_DIR / 'legends' / 'card_fronts'
LEGENDS_CARD_BACKS_OUTPUT_DIR = OUTPUT_DIR / 'legends' / 'card_backs'
LEGENDS_DECKS_OUTPUT_DIR = OUTPUT_DIR / 'legends' / 'decks'
POKEMON_MOVES_OUTPUT_DIR = OUTPUT_DIR / 'pokemon' / 'moves'
POKEMON_CARD_FRONTS_OUTPUT_DIR = OUTPUT_DIR / 'pokemon' / 'card_fronts'
POKEMON_CARD_BACKS_OUTPUT_DIR = OUTPUT_DIR / 'pokemon' / 'card_backs'
POKEMON_DECKS_OUTPUT_DIR = OUTPUT_DIR / 'pokemon' / 'decks'
SHRINE_CARD_FRONTS_OUTPUT_DIR = OUTPUT_DIR / 'shrine' / 'card_fronts'
SHRINE_CARD_BACKS_OUTPUT_DIR = OUTPUT_DIR / 'shrine' / 'card_backs'
SHRINE_DECKS_OUTPUT_DIR = OUTPUT_DIR / 'shrine' / 'decks'
SUNKEN_CARD_FRONTS_OUTPUT_DIR = OUTPUT_DIR / 'sunken' / 'card_fronts'
SUNKEN_CARD_BACKS_OUTPUT_DIR = OUTPUT_DIR / 'sunken' / 'card_backs'
SUNKEN_DECKS_OUTPUT_DIR = OUTPUT_DIR / 'sunken' / 'decks'
TACTICS_MOVES_OUTPUT_DIR = OUTPUT_DIR / 'tactics' / 'moves'
TACTICS_CARD_FRONTS_OUTPUT_DIR = OUTPUT_DIR / 'tactics' / 'card_fronts'
TACTICS_DECKS_OUTPUT_DIR = OUTPUT_DIR / 'tactics' / 'decks'
TM_MOVES_OUTPUT_DIR = OUTPUT_DIR / 'tm' / 'moves'
TM_FRONTS_OUTPUT_DIR = OUTPUT_DIR / 'tm' / 'card_fronts'
TM_BACKS_OUTPUT_DIR = OUTPUT_DIR / 'tm' / 'card_backs'
TM_DECKS_OUTPUT_DIR = OUTPUT_DIR / 'tm' / 'decks'
TRAINERS_CARD_OUTPUT_DIR = OUTPUT_DIR / 'trainers'
UTILITY_CARD_FRONTS_OUTPUT_DIR = OUTPUT_DIR / 'utility' / 'card_fronts'
UTILITY_CARD_BACKS_OUTPUT_DIR = OUTPUT_DIR / 'utility' / 'card_backs'
UTILITY_DECKS_OUTPUT_DIR = OUTPUT_DIR / 'utility' / 'decks'
VANILLA_EMBLEM_PATH = CARD_ASSETS_DIR / 'emblems' / 'vanilla.png'
CARD_FRONTS_DECK_IMG = '{j}a_deck.png'
CARD_BACKS_DECK_IMG = '{j}b_deck.png'
CARD_OBJECT_TEMPLATE = CARD_ASSETS_DIR / 'object_templates' / 'card.json'
DECK_OBJECT_TEMPLATE = CARD_ASSETS_DIR / 'object_templates' / 'deck.json'

# URLs
ART_FORM_URL = 'https://www.serebii.net/pokemon/art'

# Fonts
FONT_DIR = CARD_ASSETS_DIR / 'fonts'
ORIENTAL_PATH = str(FONT_DIR / 'la_oriental.otf')
BARLOW_PATH = str(FONT_DIR / 'barlow.ttf')
BARLOW_BOLD_PATH = str(FONT_DIR / 'Barlow-Bold.ttf')
# CJK body/title fallback (Windows): used when rendering Chinese cube text
CJK_FONT_PATH = r'C:\Windows\Fonts\msyh.ttc'
CJK_BOLD_FONT_PATH = r'C:\Windows\Fonts\msyhbd.ttc'
# Microsoft JhengHei (正黑體) — QUEST effect body
CJK_JH_FONT_PATH = r'C:\Windows\Fonts\msjh.ttc'
CJK_JH_BOLD_FONT_PATH = r'C:\Windows\Fonts\msjhbd.ttc'

# Colours
DARK_COLOUR = (37, 37, 50)
WHITE_COLOUR = (255, 255, 255)