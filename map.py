import folium as f

import csv as c

# create a map object
cle_map = f.Map(location=[41.4993, -81.6944], zoom_start=12)


# get the information from the csv file and use the map to display markers on the map
def add_markers():
    color = 'green'
    with open('mexican_restaurants1.csv', 'r') as csv_file:
        csv_reader = c.reader(csv_file)
        next(csv_reader)
        for line in csv_reader:
            f.Marker([float(line[6]), float(line[7])],
                     icon=f.Icon(color=color),
                     popup=[line[1], "custom rating: " + line[5]]).add_to(cle_map)


if __name__ == '__main__':
    add_markers()
    cle_map.save('map.html')
