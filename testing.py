# -*- coding=utf8 -*-
import json

d = {
    'firstname': 'Melle',
    'secondname': 'Dijkstra',
    'foods': ['spaghetti', 'Christensen Skö♣ld'],
}

print(json.dumps(d))
