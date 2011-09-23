## Example puts 1000 records to the mongodb collection "data".

from pymongo import Connection
from random import randint

connection = Connection()
db = connection['datadb']
collection = db['data']

names = ('eugene', 'yuriy', 'alex', 'max', 'arseniy', 'oleh')
surnames = ('koval', 'senko', 'vasylenko', 'reva', 'kuts', 'chystyakov',
         'bystrikov', 'chakabum', 'asyutin', 'konovalyuk', 'slabkyy')

# Push some data.
for i in xrange(1000):
    data = {'id': i,
            'name': names[randint(0, len(names)-1)]}
    collection.save(data)


