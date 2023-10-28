# -*- coding: utf-8 -*-

import sys
import json
import re
from pathlib import Path
from tqdm.auto import tqdm
from autoeq.constants import SAMPLE_REGEX
from autoeq.frequency_response import FrequencyResponse
ROOT_PATH = Path(__file__).parent.parent
if str(ROOT_PATH) not in sys.path:
    sys.path.insert(1, str(ROOT_PATH))
from dbtools.constants import WEBAPP_PATH, MEASUREMENTS_PATH, TARGETS_PATH


def measurement_rank(entry):
    order = [
        {'source': 'oratory1990', 'form': 'over-ear', 'rig': 'unknown'},
        {'source': 'crinacle', 'form': 'over-ear', 'rig': 'GRAS 43AG-7'},
        {'source': 'innerfidelity', 'form': 'over-ear', 'rig': 'unknown'},
        {'source': 'rtings', 'form': 'over-ear', 'rig': 'unknown'},
        {'source': 'headphonecom', 'form': 'over-ear', 'rig': 'unknown'},
        {'source': 'crinacle', 'form': 'over-ear', 'rig': 'EARS + 711'},

        {'source': 'crinacle', 'form': 'in-ear', 'rig': 'Bruel & Kjaer 4620'},
        {'source': 'oratory1990', 'form': 'in-ear', 'rig': 'unknown'},
        {'source': 'crinacle', 'form': 'in-ear', 'rig': '711'},
        {'source': 'rtings', 'form': 'in-ear', 'rig': 'unknown'},
        {'source': 'innerfidelity', 'form': 'in-ear', 'rig': 'unknown'},
        {'source': 'headphonecom', 'form': 'in-ear', 'rig': 'unknown'},

        {'source': 'oratory1990', 'form': 'earbud', 'rig': 'unknown'},
        {'source': 'crinacle', 'form': 'earbud', 'rig': '711'},
        {'source': 'rtings', 'form': 'earbud', 'rig': 'unknown'},
        {'source': 'innerfidelity', 'form': 'earbud', 'rig': 'unknown'},
        {'source': 'headphonecom', 'form': 'earbud', 'rig': 'unknown'},
    ]
    return order.index({'source': entry['source'], 'form': entry['form'], 'rig': entry['rig']})


def write_entries_and_measurements():
    entries = dict()
    measurements = dict()
    for hp_path in tqdm(list(MEASUREMENTS_PATH.glob('*/data/**/*.csv'))):
        parts = hp_path.parts[hp_path.parts.index('data') + 1:]
        source = hp_path.parts[hp_path.parts.index('data') - 1]
        form = parts[0]
        rig = parts[1] if len(parts) == 3 else 'unknown'
        if source == 'crinacle' and rig == 'unknown':
            print(parts)
            print(hp_path)
            return
        name = parts[-1].replace('.csv', '')
        if SAMPLE_REGEX.search(name):
            # Skip individual samples
            continue
        if name not in entries:
            entries[name] = []
        if name not in measurements:
            measurements[name] = dict()
        if source not in measurements[name]:
            measurements[name][source] = dict()
        measurements[name][source][rig] = FrequencyResponse.read_from_csv(hp_path).to_dict()
        entries[name].append({
            'form': form, 'rig': rig, 'source': source
        })
    entries = {key: entries[key] for key in sorted(list(entries.keys()), key=lambda key: key)}
    for headphone in entries.keys():
        entries[headphone] = sorted(entries[headphone], key=lambda entry: measurement_rank(entry))
    with open(WEBAPP_PATH.joinpath('data', 'measurements.json'), 'w', encoding='utf-8') as fh:
        json.dump(measurements, fh, ensure_ascii=False, indent=4)
    with open(WEBAPP_PATH.joinpath('data', 'entries.json'), 'w', encoding='utf-8') as fh:
        json.dump(entries, fh, ensure_ascii=False, indent=4)


def write_targets():
    targets = [
        {
            'file': TARGETS_PATH.joinpath('autoeq_in-ear.csv'),
            'label': 'AutoEq In-ear',
            'compatible': [
                {'source': 'crinacle', 'form': 'in-ear', 'rig': '711'},
                {'source': 'oratory1990', 'form': 'in-ear', 'rig': 'unknown'},
                {'source': 'oratory1990', 'form': 'earbud', 'rig': 'unknown'}
            ],
            'recommended': [
                {'source': 'crinacle', 'form': 'in-ear', 'rig': '711'},
                {'source': 'oratory1990', 'form': 'in-ear', 'rig': 'unknown'},
                {'source': 'oratory1990', 'form': 'earbud', 'rig': 'unknown'}
            ],
            'bassBoost': {'fc': 105, 'q': 0.7, 'gain': 9.5}
        },
        {
            'file': TARGETS_PATH.joinpath('diffuse_field_5128_-1dBpoct.csv'),
            'label': 'Diffuse Field 5128 (-1 dB /oct)',
            'compatible': [{'source': 'crinacle', 'form': 'in-ear', 'rig': 'Bruel & Kjaer 4620'}],
            'recommended': [{'source': 'crinacle', 'form': 'in-ear', 'rig': 'Bruel & Kjaer 4620'}],
            'bassBoost': {'fc': 105, 'q': 0.7, 'gain': 0}
        },
        {
            'file': TARGETS_PATH.joinpath('diffuse_field_gras_kemar.csv'),
            'label': 'Diffuse Field GRAS KEMAR',
            'compatible': [],
            'recommended': [],
            'bassBoost': {'fc': 105, 'q': 0.7, 'gain': 0}
        },
        {
            'file': TARGETS_PATH.joinpath('diffuse_field_iso_11904-2.csv'),
            'label': 'Diffuse Field ISO 11904-2',
            'compatible': [],
            'recommended': [],
            'bassBoost': {'fc': 105, 'q': 0.7, 'gain': 0}
        },
        {
            'file': TARGETS_PATH.joinpath('zero.csv'),
            'label': 'Flat',
            'compatible': [],
            'recommended': [],
            'bassBoost': {'fc': 105, 'q': 0.7, 'gain': 0}
        },
        {
            'file': TARGETS_PATH.joinpath('harman_in-ear_2019v2_wo_bass.csv'),
            'label': 'Harman In-ear 2019',
            'compatible': [
                {'source': 'crinacle', 'form': 'in-ear', 'rig': '711'},
                {'source': 'oratory1990', 'form': 'in-ear', 'rig': 'unknown'},
                {'source': 'oratory1990', 'form': 'earbud', 'rig': 'unknown'}
            ],
            'recommended': [],
            'bassBoost': {'fc': 105, 'q': 0.7, 'gain': 9.5}
        },
        {
            'file': TARGETS_PATH.joinpath('harman_over-ear_2018_wo_bass.csv'),
            'label': 'Harman Over-ear 2018',
            'compatible': [
                {'source': 'crinacle', 'form': 'over-ear', 'rig': 'GRAS 43AG-7'},
                {'source': 'oratory1990', 'form': 'over-ear', 'rig': 'unknown'}
            ],
            'recommended': [
                {'source': 'crinacle', 'form': 'over-ear', 'rig': 'GRAS 43AG-7'},
                {'source': 'oratory1990', 'form': 'over-ear', 'rig': 'unknown'}
            ],
            'bassBoost': {'fc': 105, 'q': 0.7, 'gain': 6}
        },
        {
            'file': TARGETS_PATH.joinpath('headphonecom_autoeq_in-ear.csv'),
            'label': 'Headphone.com Legacy AutoEq In-ear',
            'compatible': [
                {'source': 'headphonecom', 'form': 'in-ear', 'rig': 'unknown'},
                {'source': 'headphonecom', 'form': 'earbud', 'rig': 'unknown'},
            ],
            'recommended': [
                {'source': 'headphonecom', 'form': 'in-ear', 'rig': 'unknown'},
                {'source': 'headphonecom', 'form': 'earbud', 'rig': 'unknown'},
            ],
            'bassBoost': {'fc': 105, 'q': 0.7, 'gain': 9.5}
        },
        {
            'file': TARGETS_PATH.joinpath('headphonecom_harman_in-ear_2019v2_wo_bass.csv'),
            'label': 'Headphone.com Legacy Harman In-ear 2019',
            'compatible': [{'source': 'headphonecom', 'form': 'in-ear', 'rig': 'unknown'}],
            'recommended': [],
            'bassBoost': {'fc': 105, 'q': 0.7, 'gain': 9.5}
        },
        {
            'file': TARGETS_PATH.joinpath('headphonecom_harman_over-ear_2018_wo_bass.csv'),
            'label': 'Headphone.com Legacy Harman Over-ear 2018',
            'compatible': [{'source': 'headphonecom', 'form': 'over-ear', 'rig': 'unknown'}],
            'recommended': [{'source': 'headphonecom', 'form': 'over-ear', 'rig': 'unknown'}],
            'bassBoost': {'fc': 105, 'q': 0.7, 'gain': 6}
        },
        {
            'file': TARGETS_PATH.joinpath('711_5128_delta.csv'),
            'label': '711/5128 Delta',
            'compatible': [
                {'source': 'crinacle', 'form': 'in-ear', 'rig': 'unknown'},
                {'source': 'oratory1990', 'form': 'in-ear', 'rig': 'unknown'},
                {'source': 'oratory1990', 'form': 'earbud', 'rig': 'unknown'},
            ],
            'recommended': [],
            'bassBoost': {'fc': 105, 'q': 0.7, 'gain': 0}
        },
        {
            'file': TARGETS_PATH.joinpath('innerfidelity_autoeq_in-ear.csv'),
            'label': 'Innerfidelity AutoEq In-ear',
            'compatible': [
                {'source': 'innerfidelity', 'form': 'in-ear', 'rig': 'unknown'},
                {'source': 'innerfidelity', 'form': 'earbud', 'rig': 'unknown'},
            ],
            'recommended': [
                {'source': 'innerfidelity', 'form': 'in-ear', 'rig': 'unknown'},
                {'source': 'innerfidelity', 'form': 'earbud', 'rig': 'unknown'},
            ],
            'bassBoost': {'fc': 105, 'q': 0.7, 'gain': 9.5}
        },
        {
            'file': TARGETS_PATH.joinpath('innerfidelity_harman_in-ear_2019v2_wo_bass.csv'),
            'label': 'Innerfidelity Harman In-ear 2019',
            'compatible': [
                {'source': 'innerfidelity', 'form': 'in-ear', 'rig': 'unknown'},
                {'source': 'innerfidelity', 'form': 'earbud', 'rig': 'unknown'},
            ],
            'recommended': [],
            'bassBoost': {'fc': 105, 'q': 0.7, 'gain': 9.5}
        },
        {
            'file': TARGETS_PATH.joinpath('innerfidelity_harman_over-ear_2018_wo_bass.csv'),
            'label': 'Innerfidelity Harman Over-ear 2018',
            'compatible': [{'source': 'innerfidelity', 'form': 'over-ear', 'rig': 'unknown'}],
            'recommended': [{'source': 'innerfidelity', 'form': 'over-ear', 'rig': 'unknown'}],
            'bassBoost': {'fc': 105, 'q': 0.7, 'gain': 6}
        },
        {
            'file': TARGETS_PATH.joinpath('rtings_autoeq_in-ear.csv'),
            'label': 'Rtings AutoEq In-ear',
            'compatible': [
                {'source': 'rtings', 'form': 'in-ear', 'rig': 'unknown'},
                {'source': 'rtings', 'form': 'earbud', 'rig': 'unknown'},
            ],
            'recommended': [
                {'source': 'rtings', 'form': 'in-ear', 'rig': 'unknown'},
                {'source': 'rtings', 'form': 'earbud', 'rig': 'unknown'},
            ],
            'bassBoost': {'fc': 105, 'q': 0.7, 'gain': 9.5}
        },
        {
            'file': TARGETS_PATH.joinpath('rtings_harman_in-ear_2019v2_wo_bass.csv'),
            'label': 'Rtings Harman In-ear 2019',
            'compatible': [
                {'source': 'rtings', 'form': 'in-ear', 'rig': 'unknown'},
                {'source': 'rtings', 'form': 'earbud', 'rig': 'unknown'},
            ],
            'recommended': [],
            'bassBoost': {'fc': 105, 'q': 0.7, 'gain': 9.5}
        },
        {
            'file': TARGETS_PATH.joinpath('rtings_harman_over-ear_2018_wo_bass.csv'),
            'label': 'Rtings Harman Over-ear 2018',
            'compatible': [{'source': 'rtings', 'form': 'over-ear', 'rig': 'unknown'}],
            'recommended': [{'source': 'rtings', 'form': 'over-ear', 'rig': 'unknown'}],
            'bassBoost': {'fc': 105, 'q': 0.7, 'gain': 6}
        },
    ]
    for target in targets:
        target['fr'] = FrequencyResponse.read_from_csv(target['file']).to_dict()
        del target['file']
    with open(WEBAPP_PATH.joinpath('data', 'targets.json'), 'w', encoding='utf-8') as fh:
        json.dump(targets, fh, ensure_ascii=False, indent=4)


def main():
    write_entries_and_measurements()
    write_targets()


if __name__ == '__main__':
    main()
