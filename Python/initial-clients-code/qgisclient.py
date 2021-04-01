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

# Supply path to qgis install location
QgsApplication.setPrefixPath(r"C:\Program Files\QGIS 3.16\apps\qgis", True)

# Create a reference to the QgsApplication.  Setting the
# second argument to False disables the GUI.
app = QgsApplication([], True)

# Load providers
app.initQgis()

# Write your code here to load some layers, use processing
# algorithms, etc.
canvas = QgsMapCanvas()
canvas.setWindowTitle("Orchestrate QGIS Input Window")
canvas.setCanvasColor(Qt.white)
crs = QgsCoordinateReferenceSystem(3857)
project = QgsProject.instance()
canvas.setDestinationCrs(crs)

#point = ()

#def send_point(point, socket):
#    socket.send(point.encode('utf-8'))

def convertToLatLong(x,y):
    x_f = float(x)
    y_f = float(y)
    # inProj =('epsg:3857')
    # outProj=('epsg:4326')
    # x_out, y_out = transform(inProj,outProj,x_f,y_f)
    transformer = Transformer.from_crs("epsg:3857", "epsg:4326")
    x_out,y_out = transformer.transform(x_f,y_f)
    return x_out, y_out

def convertToXY(latitude, longitude):
    # inProj=('epsg:4326')
    # outProj =('epsg:3857')
    # x_out, y_out = transform(inProj,outProj,latitude,longitude)
    transformer = Transformer.from_crs("epsg:4326", "epsg:3857")
    x_out,y_out = transformer.transform(latitude,longitude)
    return x_out, y_out


x_str = ""
y_str = ""

def display_point(pointTool):
    x_str,y_str = ('{:.4f}'.format(pointTool[0]), '{:.4f}'.format(pointTool[1]))
    closest = findClosestFeature(float(x_str), float(y_str))
    lat, lon = convertToLatLong(x_str, y_str)
    point = str(lat) + "," + str(lon)
    f = open("point.txt", "w")
    #f.write(point)
    for c in closest:
        f.write(str(c) + ", ")
    f.close()

pointTool = QgsMapToolEmitPoint(canvas)
pointTool.canvasClicked.connect(display_point)
canvas.setMapTool(pointTool)

#layer = QgsVectorLayer(r"C:\Users\Ryan\Desktop\shapefiles_dresden\gis_osm_landuse_a_07_1.shp","land use", "ogr")

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

#layer_shp = QgsVectorLayer(os.path.join(os.path.dirname(__file__), "ne_10m_admin_0_countries.shp"), "Natural Earth", "ogr")
layer_shp = QgsVectorLayer(os.path.join(os.path.dirname(__file__), "../../AWOIS_Wrecks.shp"), "Natural Earth", "ogr")
layer2_shp = QgsVectorLayer(os.path.join(os.path.dirname(__file__), "../../ENC_Wrecks.shp"), "Natural Earth", "ogr")

def findClosestFeature(x,y):
    awois_features = layer_shp.getFeatures()
    enc_features = layer2_shp.getFeatures()
    shortestDistance = float("inf")
    closestFeatureId = -1
    lat,lon = convertToLatLong(x,y)
    point = QgsGeometry(QgsPoint(lon,lat))
    closestGeometry = QgsGeometry(QgsPoint(0,0))
    attrs = []

    for aFeature in awois_features:
        fGeo = aFeature.geometry()
        dist = fGeo.distance(point)
        if dist < shortestDistance:
            shortestDistance = dist
            closestFeature = aFeature.id()
            closestGeometry = aFeature.geometry()
            attrs = aFeature.attributes()

    for eFeature in enc_features:
        fGeo = eFeature.geometry()
        dist = fGeo.distance(point)
        if dist < shortestDistance:
            shortestDistance = dist
            closestFeature = eFeature.id()
            closestGeometry = eFeature.geometry()
            attrs = eFeature.attributes()
    
    print("Closest feature: ", closestFeature, ", Feature geometry: ",  closestGeometry, ", Distance: ", shortestDistance, ", Attributes: ", attrs)
    return attrs




if not layer_shp.isValid():
    print("Layer failed to load!")

if not layer2_shp.isValid():
    print("Layer failed to load!")

project.addMapLayer(layer_shp)
project.addMapLayer(layer2_shp)

print(layer_shp.crs().authid())
print(layer2_shp.crs().authid())
print(rlayer2.crs().authid())
canvas.setExtent(layer_shp.extent())
canvas.setExtent(layer2_shp.extent())
canvas.setLayers([rlayer2, layer_shp, layer2_shp])
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
