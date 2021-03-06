# make compact report.json files
# extract max-combo boards only
# add more property
# sort boards

import json
import os
import re
from collections import OrderedDict
from functools import cmp_to_key
import time
# import gzip
# import shutil
from board import Board


simulation_times = 10000

input_folder = 'output/'
folder_prefix = 'done_'
input_file_name = 'report.json'

output_folder = 'output/compact/'
output_file_name = 'report.json'
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

compare_order = [
    ('main_damage_multiplier_avg', 1),
    ('combo_count_avg', 1),
    ('combo_count', 1),
    ('main_combo_count', 1),
    ('matched_main_count', 1),
    ('matched_count', 1),
    ('drop_times', -1)
]

def compare(obj1, obj2):
    for property, higher_better in compare_order:
        if property not in obj1:
            continue
        if obj1[property] != obj2[property]:
            if obj1[property] > obj2[property]:
                return higher_better
            else:
                return higher_better * -1
    return 0

def main():

    print('simulation_times:', simulation_times)

    board = Board()

    for folder_name in os.listdir(input_folder):
        if not folder_name.startswith(folder_prefix):
            continue

        output_sub_folder = output_folder + folder_name + '/'
        if os.path.exists(output_sub_folder):
            continue

        input_file_path = input_folder + folder_name + '/' + input_file_name
        print('handling ' + input_file_path)

        with open(input_file_path, 'r') as in_file:
            data = json.load(in_file, object_pairs_hook=OrderedDict)

            # data['simulation_times'] = simulation_times

            # delete not max combo boards
            keys = list(data['combo_to_boards'].keys())
            for combo_count in keys:
                if int(combo_count) != data['max_combo']:
                    data['combo_to_boards'].pop(combo_count, None)

            for combo_count in data['combo_to_boards'].keys():
                if int(combo_count) != data['max_combo']:
                    continue

                board_objs = data['combo_to_boards'][combo_count]
                board_count = len(board_objs)
                print('total boards: {}'.format(board_count))

                start_time = time.time()
                board_counter = 0
                for board_obj in board_objs:
                    board_counter += 1
                    matched_count = sum([matched for color, matched in board_obj['combos']])
                    board_obj['matched_count'] = matched_count

                    if 'main_matched_count' in board_obj:
                        board_obj['matched_main_count'] = board_obj['main_matched_count']
                        board_obj.pop('main_matched_count', None)

                    board_obj['matched_other_count'] = matched_count - board_obj['matched_main_count']

                    # simulate matching and get average combos and damage
                    board.set_board_with_output_board(board_obj['board'])
                    result = board.calc_main_damage()
                    board_obj['main_damage_multiplier'] = result['main_damage_multiplier']

                    simu_result = board.calc_average_main_damage(simulation_times)
                    for key in simu_result.keys():
                        board_obj[key] = simu_result[key]

                    # board = board_obj['board']
                    # board_obj.pop('board', None)
                    # board_obj['board'] = board

                    # print progress
                    if board_counter % 10 == 0:
                        proportion = board_counter / board_count
                        elapsed_time = time.time() - start_time
                        remaining_time = elapsed_time / proportion * (1 - proportion)
                        print('board: {} / {}, elapsed: {:.1f}, remaining: {:.1f}'.format(
                            board_counter, board_count, elapsed_time, remaining_time
                        ), end='\r')

                print('sorting boards...', end='\r')
                board_objs.sort(key=cmp_to_key(compare), reverse=True)

        if not os.path.exists(output_sub_folder):
            os.makedirs(output_sub_folder)
        with open(output_sub_folder + output_file_name, 'w') as out_file:
            json.dump(data, out_file, separators=(',',':'))

        # with open(output_sub_folder + output_file_name, 'rb') as f_in:
        #     with gzip.open(output_sub_folder + output_file_name + '.gz', 'wb') as f_out:
        #         shutil.copyfileobj(f_in, f_out)

if __name__ == '__main__':
    main()