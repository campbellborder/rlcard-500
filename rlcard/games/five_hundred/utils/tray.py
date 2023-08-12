'''
    File name: five_hundred/utils/tray.py
    Author: Campbell Border
    Date created: 07/22/2023
'''

# TODO: why?
class Tray(object):

    def __init__(self, board_id: int):
        if board_id < 0 or board_id > 3:
            raise Exception(f'Tray: invalid board_id={board_id}')
        self.board_id = board_id

    @property
    def dealer_id(self):
        return self.board_id

    # TODO: why?
    @property
    def vul(self):
        vul_none = [0, 0, 0, 0]
        vul_n_s = [1, 0, 1, 0]
        vul_e_w = [0, 1, 0, 1]
        vul_all = [1, 1, 1, 1]
        basic_vuls = [vul_none, vul_n_s, vul_e_w, vul_all]
        return basic_vuls[self.board_id]

    def __str__(self):
        return f'{self.board_id}: dealer_id={self.dealer_id} vul={self.vul}'
