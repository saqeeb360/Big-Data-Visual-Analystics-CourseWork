## Import VTK
from vtk import *
#################################


## Load data
#################################
reader = vtkXMLImageDataReader()
reader.SetFileName('Isabel_2D.vti')
reader.Update()
data = reader.GetOutput()

## Count Number of cells, Dimension and Points in the dataset
##################################################################
print("Number of cells in the dataset:",data.GetNumberOfCells())
print("Dimension of the dataset:", data.GetDimensions())
print("Number of Points in the dataset:", data.GetNumberOfPoints())

## Create a surface representation from 2D uniform grid data
surface = vtkGeometryFilter()
surface.SetInputData(data)
surface.Update()

## Output of geometry filter is a vtkpolydata
pdata = surface.GetOutput()

## Print range of Pressure in the dataset
##################################################################
pressurRange = pdata.GetPointData().GetArray('Pressure').GetRange()
print("Range of pressure value in the dataset:",pressurRange)

## Print average of Pressure in the dataset
##################################################################
numPoints = data.GetNumberOfPoints()
dataArr = data.GetPointData().GetArray('Pressure')

pressureSum = 0
for pid1 in range(numPoints):
    # print(pid1, dataArr.GetTuple1(pid1))
    pressureSum = pressureSum + dataArr.GetTuple1(pid1)

averagePressure = pressureSum / numPoints
# Print the average pressure value
print("Average Pressure:", averagePressure)

## Cell Id = 10 (Change the Id for different cell)
##################################################################

myCellIdx = input("Enter an integer Index: ")

def check_string_is_int(string):
    try:
        int(string)
        return True
    except ValueError:
        return False

if check_string_is_int(myCellIdx):
    myCellIdx = int(myCellIdx)
    print("Cell Id selected:", myCellIdx) 
else:
    print("Wrong Input")
    myCellIdx = 0
    print("Default Cell Id selected:", myCellIdx) 

cell = data.GetCell(myCellIdx)
## Query the 4 corner points of the cell
##################################################################
pid1 = cell.GetPointId(0)
pid2 = cell.GetPointId(1)
pid3 = cell.GetPointId(3)
pid4 = cell.GetPointId(2)

## Print the 1D indices of the corner points
###################################################################
print('1D indices of the cell corner points:',pid1,pid2,pid3,pid4) ## in counter-clockwise order

## Print the coordinate of the points in the cell
###################################################################
print(data.GetPoint(pid1))
print(data.GetPoint(pid2))
print(data.GetPoint(pid3))
print(data.GetPoint(pid4))

x1, y1, z1 = data.GetPoint(pid1)
x2, y2, z2 = data.GetPoint(pid2)
x3, y3, z3 = data.GetPoint(pid3)
x4, y4, z4 = data.GetPoint(pid4)

# Compute the center location
centerX = (x1 + x2 + x3 + x4) / 4
centerY = (y1 + y2 + y3 + y4) / 4
centerZ = 25
center = (centerX, centerY, centerZ)

# Print the center location
###################################################################
print("Cell Center:", center)

val1 = dataArr.GetTuple1(pid1)
val2 = dataArr.GetTuple1(pid2)
val3 = dataArr.GetTuple1(pid3)
val4 = dataArr.GetTuple1(pid4)

# Print the Pressure value of the 4 points
###################################################################
print("Pressure value:", val1, val2, val3, val4)

# Print the average Pressure value of the 4 points
###################################################################
avgPressure = (val1+val2+val3+val4)/4
print("Average Pressure at the center:", avgPressure)

# ---------------------
# Question 2
# ---------------------

# Create a new VtkPolyData object
###################################################################
polydata = vtkPolyData()

# Create a points object and set the points
###################################################################
points = vtkPoints()
points.InsertNextPoint(x1, y1, 25)
points.InsertNextPoint(x2, y2, 25)
points.InsertNextPoint(x3, y3, 25)
points.InsertNextPoint(x4, y4, 25)
polydata.SetPoints(points)

# Assign a color to each point
###################################################################
colors = vtkUnsignedCharArray()
colors.SetNumberOfComponents(3)
colors.SetName("Colors")
colors.InsertNextTuple3(255, 0, 0) # Red
colors.InsertNextTuple3(0, 255, 0) # Green
colors.InsertNextTuple3(0, 0, 255) # Blue
colors.InsertNextTuple3(255, 255, 0) # Yellow
polydata.GetPointData().SetScalars(colors)

# Create Glyph Filter
###################################################################
vertexFilter = vtkVertexGlyphFilter()
vertexFilter.SetInputData(polydata)
vertexFilter.Update()

# Create a mapper
###################################################################
mapper = vtkPolyDataMapper()
mapper.SetInputConnection(vertexFilter.GetOutputPort())

# Create an actor
###################################################################
actor = vtkActor()
actor.SetMapper(mapper)
actor.GetProperty().SetPointSize(20)

# Create a renderer and add the actor to it
###################################################################
renderer = vtkRenderer()
renderer.SetBackground(1,1,1)
renderer.AddActor(actor)

# Create a render window and interactor
###################################################################
render_window = vtkRenderWindow()
render_window.SetSize(1400,1000)
render_window.AddRenderer(renderer)
interactor = vtkRenderWindowInteractor()
interactor.SetRenderWindow(render_window)

# Start the interaction
interactor.Initialize()
render_window.Render()
interactor.Start()