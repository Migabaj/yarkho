import re
import pandas as pd
import numpy as np
from typing import Tuple, List
from bs4 import BeautifulSoup, Comment
from collections import Counter

def collect_year(tei: BeautifulSoup) -> int:
    header = tei.find('teiheader')
    print_date = header.find('date', {'type': 'print'})
    premiere_date = header.find('date', {'type': 'premiere'})
    if premiere_date:
        if premiere_date['when'].isnumeric():
            return int(premiere_date['when'])
        elif '-' in premiere_date['when']:
            return int(premiere_date['when'].split('-')[0])
        else:
            return 0
    elif print_date:
        if print_date['when'].isnumeric():
            return int(print_date['when'])
        elif '-' in print_date['when']:
            return int(print_date['when'].split('-')[0])
        else:
            return 0
    else:
        return 0

def collect_persons_number(tei: BeautifulSoup) -> int:
    header = tei.find('teiheader')
    persons = header.find_all('person')
    return len(persons)

def collect_verses_number(tei :BeautifulSoup) -> int:
    ls = tei.find('text').find_all('l')
    if 'n' in ls[0].attrs:
        return(int(ls[-1]['n']))
    l_count = 0
    for l in ls:
        if 'part' in l.attrs:
            if l['part'] == 'I':
                l_count += 1
        else:
            l_count += 1
    return l_count

def collect_cues_number(tei: BeautifulSoup) -> int:
    return len(tei.find_all('sp'))

def collect_scenes_number(tei: BeautifulSoup) -> int:
    return len(tei.find_all('div', {'type': 'scene'}))

def collect_breaking_verses_number(tei: BeautifulSoup) -> int:
    l_part = tei.find_all('l', {'part': re.compile("M|F")})
    return len(l_part)
    
def collect_primary_data(tei: BeautifulSoup) -> Tuple[int, int, int, int, int, int]:
    year = collect_year(tei)
    persons = collect_persons_number(tei)
    verses = collect_verses_number(tei)
    cues = collect_cues_number(tei)
    scenes = collect_scenes_number(tei)
    breaking_verses = collect_breaking_verses_number(tei)
    return year, persons, verses, cues, scenes, breaking_verses

def separate_value_by_genre(dataframe: pd.DataFrame, values: List[str], name=False, tragedy4=False) -> dict:
    
    if name:
        values = ['name', *values]
        
    val_comedy = dataframe[dataframe['genre'] == 'comedy'][values]
    val_tragedy = dataframe[dataframe['genre'] == 'tragedy'][values]
    
    if tragedy4:
        val_tragedy13 = dataframe[(dataframe['genre'] == 'tragedy') & (dataframe['period'] != 4)][values]
        val_tragedy4 = dataframe[(dataframe['genre'] == 'tragedy') & (dataframe['period'] == 4)][values]
        return {'comedy': val_comedy,
                'tragedy13': val_tragedy13,
                'tragedy4': val_tragedy4,
                'tragedy': val_tragedy}
    else:
        return {'comedy': val_comedy,
                'tragedy': val_tragedy}

def mp_ac(sorted_desc_numbers1, sorted_desc_numbers2):
    i = 0
    j = 0
    if sorted_desc_numbers1[0] >= sorted_desc_numbers2[0]:
        number1 = sorted_desc_numbers1[0]
        number2 = sorted_desc_numbers2[0]
    else:
        number1 = sorted_desc_numbers2[0]
        number2 = sorted_desc_numbers1[0]
    
    while number1 > number2:
        number1 = sorted_desc_numbers1[i]
        i += 1
    included1 = sorted_desc_numbers1[i-1:]
    while number2 >= number1:
        number2 = sorted_desc_numbers2[j]
        j += 1
    included2 = sorted_desc_numbers2[:j-1]
    MP = ((len(included1)/len(sorted_desc_numbers1))+(len(included2)/len(sorted_desc_numbers2)))/2
    if np.mean(included1) > np.mean(included2):
        AC = np.mean(included1)/np.mean(included2)
    else:
        AC = np.mean(included2)/np.mean(included1)
    return MP, AC

def map_characters_to_social(play_soup, social_characters_dict, source=True):
    cast = play_soup.find_all('role')
    if source:
        cast_stati = [character['statut'] for character in cast]
        cast_stati_numbers = list(map(social_characters_dict.get, cast_stati))
    else:
        cast_stati = []
        for castitem_tag in play_soup.find_all('castitem'):
            properties = castitem_tag(text=lambda text: isinstance(text, Comment))
            if 'statut' in properties[2]:
                statut = properties[2].split('=')[1].strip('"')
                # print(statut)
            else:
                statut = ''
            cast_stati.append(statut)
        cast_stati_numbers = list(map(social_characters_dict.get, cast_stati))
    stati_count = Counter(cast_stati_numbers)
    for i in range(4):
        if i not in stati_count.keys():
            stati_count[i] = 0
    stati_count_with_names = {}
    for key in stati_count.keys():
        stati_count_with_names[f'social_{key}_character_amount'] = stati_count[key]
    return stati_count_with_names


if __name__ == '__main__':
    pass