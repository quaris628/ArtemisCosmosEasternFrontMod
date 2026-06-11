
def is_downgraded_tsn(ship_type_key):
    # EF mod v3.5 retired: light cruiser, scout, battleship, missile cruiser, carrier
    # These new types were added in Cosmos: tsn_battle_cruiser, tsn_light_carrier, tsn_warpster, tsn_destroyer tsn_heavy_cruiser
    # (making any of these new types scrapped was considered, but not done)
    # As a general rule, battleship or lighter should be retired; anything else should be scrapped
    return ship_type_key in {"tsn_light_cruiser", "tsn_battle_cruiser", "tsn_carrier", "tsn_light_carrier", "tsn_battleship", "tsn_warpster", "tsn_missile_cruiser", "tsn_destroyer", "tsn_escort", "tsn_heavy_cruiser", "tsn_scout"}
    
    # TODO and should TSN shuttle, fighter, and bomber be retired or otherwise changed?
    # In EF they actually had their top speed boosted (all types, not just tsn), and no other changes

def get_disabled_for_players_tsn_ship_type_keys():
    # EF mod v3.5 scrapped the dreadnought, mine layer, juggernaut by vastly decreasing their beam damage 20x and worsening efficiency by 12x.
    # It was originally desired to completely disable selecting them, but that wasn't working in artemis 2.
    # In Cosmos, we can completely disallow selecting them!
    return {"tsn_mine_layer", "tsn_juggernaut", "tsn_dreadnought"}

def downgrade_tsn_name_prefix():
    return "Slvg "

def downgrade_tsn_description_suffix():
    # EF mod v3.5 description: "... with 10% less energy efficiancy and beam damage due to retirement."
    return "\n10% worse energy efficiency and beam damage due to years in a ship graveyard before being retrofitted by cadet engineers."

def downgrade_tsn_beam_damage_coeff():
    return 0.9

def downgrade_tsn_energy_cost_coeff():
    return 1.1
