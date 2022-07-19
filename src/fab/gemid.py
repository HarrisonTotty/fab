'''
Contains definitions concerned with fetching Gem ID and leaderboard information.
'''

from __future__ import annotations

import dataclasses
import pandas

from typing import Optional

LEADERBOARDS_URL = 'https://fabtcg.com/leaderboards'

@dataclasses.dataclass
class PlayerProfile:
    '''
    Represents a particular Flesh and Blood player profile (Gem ID).

    Tip: Warning
      At this time `PlayerProfile` objects created via the `from_gemid()` or
      `search()` methods work by parsing the HTML tables embedded on [the
      official website](https://fabtcg.com/leaderboards/). Please be respectful
      by limiting query volumes to numbers comparable to what could be done
      manually via the browser.

    Attributes:
      country: The country code of the player.
      id: The Gem ID of the player.
      name: The name of the player.
      elo_cc: The Constructed Elo Rating of the player.
      elo_lim: The Limited Elo Rating of the player.
      rank_elo_cc: The rank of the player's Constructed Elo Rating.
      rank_elo_lim: The rank of the player's Limited Elo Rating.
      rank_xp: The lifetime rank of the player in total XP.
      rank_xp_90: The 90-day XP rank of the player.
      xp: The lifetime total XP of the player.
      xp_90: The XP of the player over the last 90 days.
    '''

    country: str
    id: int
    name: str
    elo_cc: Optional[int] = None
    elo_lim: Optional[int] = None
    rank_elo_cc: Optional[int] = None
    rank_elo_lim: Optional[int] = None
    rank_xp: Optional[int] = None
    rank_xp_90: Optional[int] = None
    xp: Optional[int] = None
    xp_90: Optional[int] = None

    @staticmethod
    def from_gemid(id: int) -> PlayerProfile:
        '''
        Creates a `PlayerProfile` object from the specified Gem ID.

        Args:
          id: The Gem ID of the player.

        Returns:
          A player profile record associated with the specified Gem ID.
        '''
        try:
            results = [p for p in PlayerProfile.search(id) if p.id == id]
        except Exception as e:
            raise Exception(f'unable to fetch player profile - {e}')
        if not results:
            raise Exception(f'unable to locate player profile associated with id "{id}"')
        return results[0]

    @staticmethod
    def search(query: int | str) -> list[PlayerProfile]:
        '''
        Searches the offical leaderboards for player profiles by player name or
        Gem ID.

        Args:
          query: The player name or Gem ID to search for.

        Returns:
          A list of player profiles matching the search query.
        '''
        agg_data: dict[int, PlayerProfile] = {}
        for mode in ['xpall', 'xp90', 'elo_cons', 'elo_lim']:
            try:
                data = pandas.read_html(
                    f'{LEADERBOARDS_URL}/?mode={mode}&query={query}'
                )[0].to_dict('records')
            except Exception as e:
                raise Exception(f'unable to fetch leaderboard data - {e}')
            for entry in data:
                name_parts = entry['Name'].rsplit(' ', 1)
                name = name_parts[0]
                gem_id = int(name_parts[1].replace('(', '').replace(')', ''))
                if not gem_id in agg_data:
                    agg_data[gem_id] = PlayerProfile(
                        country = entry['Country'],
                        id = gem_id,
                        name = name
                    )
                if mode == 'xpall':
                    agg_data[gem_id].rank_xp = entry['Rank (Lifetime)']
                    agg_data[gem_id].xp = entry['XP (Lifetime)']
                elif mode == 'xp90':
                    agg_data[gem_id].rank_xp = entry['Rank (90 Days)']
                    agg_data[gem_id].xp = entry['XP (90 Days)']
                elif mode == 'elo_cons':
                    agg_data[gem_id].elo_cc = entry['Rating']
                    agg_data[gem_id].rank_elo_cc = entry['Rank']
                elif mode == 'elo_lim':
                    agg_data[gem_id].elo_lim = entry['Rating']
                    agg_data[gem_id].rank_elo_lim = entry['Rank']
        return list(agg_data.values())
