import sys
from matplotlib import pyplot
from math import *
from numpy import std
from scipy.stats import spearmanr

attrs = ['life', 'gni', 'expected_school', 'mean_school', 'pop']

class Region:
    def __init__(self, *data):
        self.country = data[0]
        self.name = data[1]

        #for i in range(len(attrs)):
        #    getattr(self, attrs[i]) = data[i + 2]

        self.life = data[2]
        self.gni = data[3]
        self.expected_school = data[4]
        self.mean_school = data[5]
        self.pop = data[6]
        self.score = 0
        self.count = 0
        self.sd = 0

    def __repr__(self):
        return f'{self.country} life = {self.life}, gni = {self.gni}, expected school = {self.expected_school}, mean school = {self.mean_school}, pop = {self.pop}, count = {self.count}, sd = {self.sd}'

def analyze(data1, data2):
    corr, _ = spearmanr(data1, data2)
    print('Spearmans correlation: %.3f' % corr)

def plot(data1, data2, **kwargs):
    pyplot.scatter(data1, data2, s = [9]*len(data1), **kwargs)


params = ["Country",
        "Region",
        "Life expectancy",
        "GNI per capita",
        "Expected years schooling",
        "Mean years schooling",
        "Population size",
        "Count"]

regions = {}
frame = []

with open('hdi-stuff.tsv', 'r') as f:
    for line in f:
        name, *vals = line.split('\t')
        name = name.strip()
        if not vals:
            country = name
            regions[country] = {}
            continue
            
        vals = list(map(float, vals))
        regions[country][name] = Region(country, name, *vals)
        frame.append(regions[country][name])

print(f'{len(regions)} regions')
singletons = [country for country in regions if len(regions[country]) == 1]
print(f'{len(singletons)} singletons')


# Blue zone analysis
print(f'Analyzing blue zones')
blues = ['Australia', 'Greece', 'Italy', 'Japan', 'South Korea', 'Spain', 'Switzerland']
#'China','Monaco']
analyze([region.life for region in frame if region.country in blues],
        [log(region.gni) for region in frame if region.country in blues])

eu = [
    "Austria",
    "Belgium",
    "Bulgaria",
    "Croatia",
    "Cyprus",
    "Czech Republic",
    "Denmark",
    "Estonia",
    "Finland",
    "France",
    "Germany",
    "Greece",
    "Hungary",
    "Ireland",
    "Italy",
    "Latvia",
    "Lithuania",
    "Luxembourg",
    "Malta",
    "Netherlands",
    "Poland",
    "Portugal",
    "Romania",
    "Slovakia",
    "Slovenia",
    "Spain",
    "Sweden"
]

other_europe = [
    "Russian Federation",
    "Ukraine",
    "Belarus",
    "Switzerland",
    "Serbia",
    "Norway",
    "Bosnia Herzegovina",
    "Albania",
    "Moldova",
    "North Macedonia",
    "Kosovo",
    "Montenegro",
    "Iceland",
    "Andorra",
    "Monaco",
    "Liechtenstein",
    "San Marino"
]

other_north_america = [
    "Canada",
    "Guatemala",
    "Cuba",
    "Haiti",
    "Dominican Republic",
    "Honduras",
    "Nicaragua",
    "El Salvador",
    "Costa Rica",
    "Panama",
    "Jamaica",
    "Trinidad & Tobago",
    "Belize",
    "Bahamas",
    "Barbados",
    "Saint Lucia",
    "Grenada",
    "Saint Vincent and the Grenadines",
    "Antigua and Barbuda",
    "Dominica",
    "Saint Kitts and Nevis"
]

other_east_asia = [
    "Japan",
    "Mongolia",
    "North Korea",
    "South Korea",
    "Taiwan"
]

other_south_asia = [
    "Afghanistan",
    "Bangladesh",
    "Bhutan",
    "Nepal",
    "Maldives",
    "Pakistan",
    "Sri Lanka"
]

# More blue zones
# Don't draw China - it's an outlier
for country in blues:
    plot([regions[country][region].life for region in regions[country]],
        [log(regions[country][region].gni) for region in regions[country]])

pyplot.xlabel("Life expectancy")
pyplot.ylabel("Log income")
pyplot.show()

print("Regions")
for i in range(len(attrs) - 1):
    print(f'Analyzing {attrs[i]} and {attrs[i+1]}')
    analyze([getattr(region, attrs[i]) for region in frame],
            [getattr(region, attrs[i + 1]) for region in frame])



# Several countries mark all their regions with the same life expectancy. Only one country (Cuba) appears to do this for GNI.
# Rank countries by each feature, then combine to form a naive HDI
for attr in ['life', 'gni', 'expected_school']:
    order = sorted(frame, key=lambda region: -getattr(region, attr))
    for pos in range(len(frame)):
        order[pos].score += pos

# Add groupings for continents
regions['East Asia'] = {}
regions['East Asia']['Total'] = Region('East Asia', 'Total', 0, 0, 0, 0, 0)
for country in other_east_asia:
    regions['East Asia'][country] = regions[country]['Total']

for region in regions['China'].values():
    if region.name != 'Total':
        regions['East Asia'][region.name] = region

regions['South Asia'] = {}
regions['South Asia']['Total'] = Region('South Asia', 'Total', 0, 0, 0, 0, 0)
for country in other_south_asia:
    regions['South Asia'][country] = regions[country]['Total']

for region in regions['India'].values():
    if region.name != 'Total':
        regions['South Asia'][region.name] = region

regions['North America'] = {}
regions['North America']['Total'] = Region('North America', 'Total', 0, 0, 0, 0, 0)
for country in other_north_america:
    regions['North America'][country] = regions[country]['Total']
regions['North America']['United States'] = regions['United States']['Total']

regions['North America (Split)'] = {}
regions['North America (Split)']['Total'] = Region('North America (Split)', 'Total', 0, 0, 0, 0, 0)
for country in other_north_america:
    regions['North America (Split)'][country] = regions[country]['Total']

for region in regions['United States'].values():
    if region.name != 'Total':
        regions['North America (Split)'][region.name] = region
del regions['North America (Split)']['Hawaii']

regions['EU'] = {}
regions['EU']['Total'] = Region('EU', 'Total', 0, 0, 0, 0, 0)
for country in eu:
    regions['EU'][country] = regions[country]['Total']

regions['Europe'] = {}
regions['Europe']['Total'] = Region('Europe', 'Total', 0, 0, 0, 0, 0)
for country in other_europe:
    regions['Europe'][country] = regions[country]['Total']

for region in regions['EU']:
    if region != 'Total':
        regions['Europe'][region] = regions['EU'][region]

bigguns = ['United States', 'EU', 'India', 'China']
colors = ['grey', 'blue', 'orange', 'red']
print(list(zip(bigguns, colors)))
for country, color in zip(bigguns, colors):
    plot([regions[country][region].life for region in regions[country]
            if region != 'Total'],
        [log(regions[country][region].gni) for region in regions[country]
            if region != 'Total'],
        color = color,
        label = country)

pyplot.xlabel("Life expectancy")
pyplot.ylabel("Log income")
pyplot.legend()
pyplot.show()

# Collect scores for each country
scores = {}
for country in regions:
    if country not in scores:
        scores[country] = []
    for region in regions[country]:
        # Careful, we're using Total regions in continents
        if region != 'Total':
            scores[country] += [regions[country][region].score]

# Extra stats for multi-region countries
countries = [
    regions[country]['Total']
    for country in regions]
for country in countries:
    country.count = max(len(regions[country.country]) - 1, 1)
    country.sd = round(std(scores[country.country]), 1) \
            if country.count > 1 else 0


print(f'Analyzing log population and count')
analyze([country.pop for country in countries],
        [country.count for country in countries])


# Variability is automatically and unfairly 0 for singletons
countries = [country for country in countries if country.count > 1]
print(f'Analyzing variability and count')
analyze([country.sd for country in countries],
        [country.count for country in countries])
print(f'Analyzing variability and population')
analyze([country.sd for country in countries],
        [country.pop for country in countries])

countries = sorted(countries, key = lambda country: country.count)[-30:]
countries = sorted(countries, key = lambda country: country.sd)
for country in countries:
    print(f'{country.country.ljust(16)}\t{country.count}\t{country.sd}')
    #print(sorted(scores[country.country]))
