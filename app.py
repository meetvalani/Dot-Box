from flask import Flask, make_response, request, render_template, redirect
import random
import time
import threading
import json
import sys
from copy import deepcopy

app = Flask(__name__, static_folder='')


class PlayerData:

    def __init__(self):
        self.all_size = dict()
        self.id = 0

    def set_id(self):
        self.id = 0 if self.id == 1 else 1

    def get_id(self, id):
        return self.id

    def set_size(self, size, key):
        self.all_size[key] = size

    def get_size(self, key):
        return self.all_size[key]

    def get_color(self, player_id, key):
        database[key]['point'][player_id] += 1
        database[key]['turn'] = 0 if database[key]['turn'] == 1 else 1
        if player_id == 0:
            return "green"
        else:
            return "blue"


player_data = PlayerData()
players = []
names = dict()
database = dict()
key = 0


def get_cordinates(x1, y1, x2, y2):
    if x1 == x2:
        aa = [x1+1, min(y1, y2)+1]
        return aa
    else:
        bb = [min(x1, x2)+1, y1+1]
        return bb


def line_saver(ls, key):
    a, b, x, y = ls
    if a == x:
        if b > y:
            b, y = y, b
    else:
        if a > x:
            a, x = x, a
    database[key]['saved_lines'][get_line_string(a, b, x, y)] = 1
    database[key]['saved_lines'][get_line_string(x, y, a, b)] = 1


def get_line_string(a, b, c, d):
    if a == c:
        return 'm'+str(a)+'m'+str(min(b, d))+'m'+str(c)+'m'+str(max(b, d))
    else:
        return 'm'+str(min(a, c))+'m'+str(b)+'m'+str(max(a, c))+'m'+str(d)


def point_updater(x1, y1, x2, y2, key, save_line, player_id):
    x1, y1, x2, y2 = y1, x1, y2, x2
    xx = [x1, y1, x2, y2]
    if x1 == x2:
        if y1 > y2:
            y1, y2 = y2, y1
    else:
        if x1 > x2:
            x1, x2 = x2, x1
    tmp = get_line_string(x1, y1, x2, y2)
    if tmp in database[key]['saved_lines'].keys():
        database[key]['turn'] = 0 if database[key]['turn'] == 1 else 1
        return ""
    line_saver(xx, key)
    return_string = ""
    if x1 == x2:
        # up-down
        #return_string += '<rect width="50" height="50" x="" y="" style="fill:'+player_data.get_color(player_id, key)+';stroke-opacity:0.7"'
        up_tmp_lines = [get_line_string(
            x1-1, y1, x2-1, y2), get_line_string(x1, y1, x1-1, y1), get_line_string(x2, y2, x2-1, y2)]
        for each in up_tmp_lines:
            if each not in database[key]['saved_lines']:
                break
        else:
            xx, yy = get_cordinates(x1, y1, x2, y2)
            # up
            return_string += '<rect width="50" height="50" y="' + \
                str((xx-1)*50)+'" x="'+str((yy)*50) + \
                '" style="fill:' + \
                player_data.get_color(player_id, key)+';stroke-opacity:0.7"/>'
        down_tmp_lines = [get_line_string(
            x1+1, y1, x2+1, y2), get_line_string(x1, y1, x1+1, y1), get_line_string(x2, y2, x2+1, y2)]
        for each in down_tmp_lines:
            if each not in database[key]['saved_lines']:
                break
        else:
            xx, yy = get_cordinates(x1, y1, x2, y2)
            # down
            return_string += '<rect width="50" height="50" y="' + \
                str((xx)*50)+'" x="'+str((yy)*50) + \
                '" style="fill:' + \
                player_data.get_color(player_id, key)+';stroke-opacity:0.7"/>'
    else:
        # left-right
        left_tmp_lines = [get_line_string(x1, y1-1, x1, y1), get_line_string(
            x1, y1-1, x2, y2-1), get_line_string(x2, y2-1, x2, y2)]
        for each in left_tmp_lines:
            if each not in database[key]['saved_lines']:
                break
        else:
            xx, yy = get_cordinates(x1, y1, x2, y2)
            # left
            return_string += '<rect width="50" height="50" y="' + \
                str((xx)*50)+'" x="'+str((yy-1)*50) + \
                '" style="fill:' + \
                player_data.get_color(player_id, key)+';stroke-opacity:0.7"/>'

        right_tmp_lines = [get_line_string(x1, y1, x1, y1+1), get_line_string(
            x1, y1+1, x2, y1+1), get_line_string(x2, y2, x2, y2+1)]
        for each in right_tmp_lines:
            if each not in database[key]['saved_lines']:
                break
        else:
            xx, yy = get_cordinates(x1, y1, x2, y2)
            # right
            return_string += '<rect width="50" height="50" y="' + \
                str((xx)*50)+'" x="'+str((yy)*50) + \
                '" style="fill:' + \
                player_data.get_color(player_id, key)+';stroke-opacity:0.7"/>'
    return return_string


def grid_generator(size):
    tmp = [[0 for i in range(size+1)]for j in range(size+1)]
    return tmp


@app.route('/')
def index():
    return render_template('index.html', host_ip=sys.argv[1], port_no=sys.argv[2])


@app.route('/start')
def start():
    global players, key
    name = request.args.get("player_name")
    grid_size = int(request.args.get("grid_size"))
    players.append(name)
    if len(players) == 1:
        name = "Player 1:"+name
        players[0] = name
        key = str(random.randint(1000000, 9999999))
        player_data.set_size(min(grid_size, 10), key)
        return render_template('waiting.html', player_name=name, host_ip=sys.argv[1], port_no=sys.argv[2])
    else:
        name = "Player 2:"+name
        players[1] = name
        size = max(min(player_data.get_size(key), grid_size), 3)
        player_data.set_size(size, key)
        return render_template('waiting.html', player_name=name, host_ip=sys.argv[1], port_no=sys.argv[2])


@app.route('/wait')
def wait():
    global key, players
    if len(players) == 1:
        return str(0)
    else:
        if str(key) not in names.keys():
            names.update({str(key): deepcopy(players)})
        players = []
        return str(json.dumps({'key': key}))


@app.route('/grid')
def grid2():
    return render_template('grid.html', host_ip=sys.argv[1], port_no=sys.argv[2])


@app.route('/ajax/<methods>')
def ajax(methods):
    global database, names, player_data

    if methods == 'done':
        key = request.args.get('key')
        if database[key]['done']:
            try:
                database[key]['done'] = True
            except:
                pass
            return "gone"
        else:
            database[key]['done'] = 1
        return "ok"

    if methods == 'get_grid':
        key = request.args.get('key')
        if str(key) in database.keys():
            return str(json.dumps(database[key]))
        else:
            try:
                size = player_data.get_size(key)
                database[str(key)] = {'point': [0, 0], 'grid': grid_generator(
                    size), 'size': size, 'line': "", 'saved_lines': dict(), 'line_string': "", 'square': "", 'players': names[key], 'player_id': 0, 'turn': 0, 'box': (size-1)**2, 'done': 0}
                return str(json.dumps(database[key]))
            except KeyError:
                return str('gobackhome')

    if methods == 'update':
        key = request.args.get('key')
        player_name = request.args.get('player_id')
        player_id = 0 if player_name == database[key]['players'][0] else 1
        save_line = request.args.get('save_line')
        x1 = int(request.args.get('x1'))
        y1 = int(request.args.get('y1'))
        x2 = int(request.args.get('x2'))
        y2 = int(request.args.get('y2'))
        database[key]['grid'][y1][x1] = 1
        database[key]['grid'][y2][x2] = 1
        database[key]['grid'][y1][x1] = 1
        database[key]['grid'][y2][x2] = 1
        database[key]['grid_dot'] = database[key]['grid'][:]
        xx = point_updater(x1, y1, x2, y2, key, save_line, player_id)
        database[key]['line_string'] += xx

        return str(json.dumps(database[key]))

    if methods == 'update_line':
        key = request.args.get('key')
        player_name = request.args.get('player_id')
        player_id = 0 if player_name == database[key]['players'][0] else 1
        if player_id == database[key]['turn']:
            database[key]['turn'] = 0 if database[key]['turn'] == 1 else 1
            database[key]['line'] += request.args.get('line')
            return "valid"
        return "invalid"


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Command usage: python app.py host port')
        exit(0)
    try:
        app.run(host=sys.argv[1], port=sys.argv[2], debug=True)
    except Exception as error:
        print(error)
