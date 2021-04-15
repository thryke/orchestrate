import os
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = r'C:\Program Files\QGIS 3.16\apps\Qt5\plugins'
os.environ['PATH'] += r';C:\Program Files\QGIS 3.16\apps\Qt5\bin'
os.environ['PROJ_LIB'] = r'C:\Program Files\QGIS 3.16\share\proj'

from qgis.core import *
from qgis.gui import *
from qgis.utils import *
from PyQt5 import *
from PyQt5.QtCore import *
import os
import sys
import shutil
import tempfile
import urllib.request
from zipfile import ZipFile
from glob import glob

from qgis.core import (QgsApplication, QgsCoordinateReferenceSystem, QgsFeature,
	               QgsGeometry, QgsProject, QgsRasterLayer, QgsVectorLayer)
from qgis.gui import QgsLayerTreeMapCanvasBridge, QgsMapCanvas
from qgis.PyQt.QtCore import Qt

from multiprocessing import Process, Pipe

from pyproj import Proj, Transformer

from random import randrange
import webbrowser


# Supply path to qgis install location
QgsApplication.setPrefixPath(r"C:\Program Files\QGIS 3.16\apps\qgis", True)

# Create a reference to the QgsApplication.  Setting the
# second argument to False disables the GUI.
app = QgsApplication([], True)

# Load providers
app.initQgis()

canvas = QgsMapCanvas()
canvas.setWindowTitle("Orchestrate QGIS Input Window")
canvas.setCanvasColor(Qt.white)
crs = QgsCoordinateReferenceSystem(3857)
project = QgsProject.instance()
canvas.setDestinationCrs(crs)

def convertToLatLong(x,y):
    x_f = float(x)
    y_f = float(y)
    transformer = Transformer.from_crs("epsg:3857", "epsg:4326")
    x_out,y_out = transformer.transform(x_f,y_f)
    return x_out, y_out

def convertToXY(latitude, longitude):
    transformer = Transformer.from_crs("epsg:4326", "epsg:3857")
    x_out,y_out = transformer.transform(latitude,longitude)
    return x_out, y_out


x_str = ""
y_str = ""

def display_point(pointTool):
    x_str,y_str = ('{:.4f}'.format(pointTool[0]), '{:.4f}'.format(pointTool[1]))
    closest = findClosestFeature(float(x_str), float(y_str))
    #closestFeatureSearch(closest)
    lat, lon = convertToLatLong(x_str, y_str)
    print(lat, lon)
    point = str(lat) + "," + str(lon)
    f = open("point.txt", "w")
    #f.write(point)
    for c in closest:
        f.write(str(c) + ", ")
    f.close()

pointTool = QgsMapToolEmitPoint(canvas)
pointTool.canvasClicked.connect(display_point)
canvas.setMapTool(pointTool)

urlWithParams = 'type=xyz&url=https://a.tile.openstreetmap.org/%7Bz%7D/%7Bx%7D/%7By%7D.png&zmax=19&zmin=0&crs=EPSG3857'
rlayer2 = QgsRasterLayer(urlWithParams, 'OpenStreetMap', 'wms')

if rlayer2.isValid():
    project.addMapLayer(rlayer2)
else:
    print('invalid layer')

# Download shp ne_10m_admin_0_countries.shp and associated files in the same directory
url = "https://www.naturalearthdata.com/http//www.naturalearthdata.com/download/10m/cultural/ne_10m_admin_0_countries.zip"
if not glob("ne_10m_admin_0_countries.*"):
    with urllib.request.urlopen(url) as response:
        with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
            shutil.copyfileobj(response, tmp_file)
        with ZipFile(tmp_file.name, 'r') as zipObj:
            # Extract all the contents of zip file in current directory
            zipObj.extractall()

layer_shp = QgsVectorLayer(os.path.join(os.path.dirname(__file__), "../../Merged.shp"), "Natural Earth", "ogr")

fields = layer_shp.fields().names()
fni = layer_shp.fields().indexFromName('VESSLTERMS')
unique_values = layer_shp.uniqueValues(fni)

# fill categories
categories = []
for unique_value in unique_values:
    # initialize the default symbol for this geometry type
    symbol = QgsSymbol.defaultSymbol(layer_shp.geometryType())
    symbol.setOpacity(0.5)

    obstruction_color = QtGui.QColor('#ffee00')
    wreck_color  = QtGui.QColor('#00bbff')

    # assigning different colors based on point type
    if unique_value == "OBSTRUCTION":
        symbol.setColor(obstruction_color)
    else:
        symbol.setColor(wreck_color)
    # configure a symbol layer
    layer_style = {}
    layer_style['outline'] = '#000000'
    symbol_layer = QgsSimpleFillSymbolLayer.create(layer_style)

    # replace default symbol layer with the configured one
    if symbol_layer is not None:
        symbol.changeSymbolLayer(0, symbol_layer)

    # create renderer object
    category = QgsRendererCategory(unique_value, symbol, str(unique_value))
    # entry for the list of category items
    categories.append(category)

# create renderer object
renderer = QgsCategorizedSymbolRenderer('VESSLTERMS', categories)

# assign the created renderer to the layer
if renderer is not None:
    layer_shp.setRenderer(renderer)

def findClosestFeature(x,y):
    awois_features = layer_shp.getFeatures()
    shortestDistance = float("inf")
    closestFeatureId = -1
    lat,lon = convertToLatLong(x,y)
    point = QgsGeometry(QgsPoint(lon,lat))
    closestGeometry = QgsGeometry(QgsPoint(0,0))
    attrs = []

    # loop through all features
    for aFeature in awois_features:
        fGeo = aFeature.geometry()
        dist = fGeo.distance(point)
        # update closest point, check to see if =-1 to because of some points with null coordinates
        if dist < shortestDistance and dist != -1:
            shortestDistance = dist
            closestFeature = aFeature.id()
            closestGeometry = aFeature.geometry()
            attrs = aFeature.attributes()

    # cleaning the description field if it's not null because of some formatting issues
    if attrs[11] != "NULL":
        original_description = attrs[11]
        # some description fields are not of type str, so this cleaning doesn't work on them
        if type(original_description) == str:
            cleaned_description = " ".join(original_description.split())
            attrs[11] = cleaned_description
        else: 
            cleaned_description = original_description
    
    # display information about the closest feature
    print("Closest feature: ", closestFeature, "\nFeature geometry: ",  closestGeometry, "\nDistance: ", shortestDistance, "\nAttributes: ", attrs)
    
    attrs_str = ""
    for a in attrs:
        print(attrs.index(a))
        print(len(attrs)-1)
        if attrs.index(a) != len(attrs)-1:
            if type(a) == str:
                attrs_str += a + ", "
            else:
                attrs_str += "NULL" + ", "
        else:
            if type(a) == str:
                attrs_str += a
            else:
                attrs_str += "NULL"

    print(attrs_str)
    return attrs

# TODO: move this to second client (requires fixing networking), add searching for provided year sunk instead of description checking when available
def closestFeatureSearch(attr):
    description = attr[11]
    cleaned = " ".join(description.split())
    query = attr[1]
    numbers_in_description = [int(s) for s in cleaned.split() if s.isdigit()]
    for num in numbers_in_description:
        if num >= 1500 and num <= 2100:
            query += " " + str(num)

    print(query)
    
    url = 'https://www.google.com/search?q=site%3Awrecksite.eu+' + query
    webbrowser.open(url)


if not layer_shp.isValid():
    print("Layer failed to load!")

project.addMapLayer(layer_shp)

print(layer_shp.crs().authid())
print(rlayer2.crs().authid())
canvas.setExtent(layer_shp.extent())
canvas.setLayers([rlayer2, layer_shp])
canvas.zoomToFullExtent()
canvas.freeze(True)
canvas.show()
canvas.refresh()
canvas.freeze(False)
canvas.repaint()
bridge = QgsLayerTreeMapCanvasBridge(
    project.layerTreeRoot(),
    canvas
)

def run_when_project_saved():
    print('Saved')

project.projectSaved.connect(run_when_project_saved)

project.write('my_new_qgis_project.qgz')

def run_when_application_state_changed(state):
    print('State changed', state)

app.applicationStateChanged.connect(run_when_application_state_changed)

exitcode = app.exec()
QgsApplication.exitQgis()
sys.exit(True)
