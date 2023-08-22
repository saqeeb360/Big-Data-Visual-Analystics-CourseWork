#!/usr/bin/env python3

# Import vtk library
from vtk import *

## Load data
###################################
reader = vtkXMLImageDataReader()
reader.SetFileName("Isabel_2D.vti")
reader.Update()
image_data = reader.GetOutput()

# Input contour value 
contour_value = input("Enter an contour value: ")

def check_string_is_number(string):
    try:
        float(string)
        return True
    except ValueError:
        return False

if check_string_is_number(contour_value):
    contour_value = float(contour_value)
    print("Contour value:", contour_value) 
else:
    print("Wrong Input")
    contour_value = 100
    print("Default Contour value:", contour_value) 

# Create VTK PolyData object
poly_data = vtkPolyData()

# Create vtkCellArray to store contour segments
lines_array = vtkCellArray()

# Create vtkPoints to store point cordinates of the contour points
points = vtkPoints()

# Get dimensions of image data
dimensions = image_data.GetDimensions()

# Calculate the number of cells in the grid
num_cells = (dimensions[0]-1) * (dimensions[1]-1)

# Get scalar pressure data
dataArr = image_data.GetPointData().GetArray('Pressure')

print("Computing result. Wait ...")
for cell_index in range(num_cells):

    # Checking the progress
    if(cell_index % 10000 == 0):
        print(cell_index / 10000, "out of 6 parts completed.")

    cell = image_data.GetCell(cell_index)
    
    # Get the points in counter-clockwise order
    pids = cell.GetPointId(0),cell.GetPointId(1),cell.GetPointId(3),cell.GetPointId(2), cell.GetPointId(0)

    # Get the pressure value at each point in the cell
    vals = [dataArr.GetTuple1(i) for i in pids]

    # Counting number of edges on cell with isocontour points 
    count_seg = 0
    for index in range(4):
        if(vals[index] < contour_value < vals[index+1]) or (vals[index+1] < contour_value < vals[index]):
            count_seg += 1

    # If 2 edges having isocontour 
    if(count_seg == 2):
        # Make a polyline 
        line = vtkPolyLine()
        line.GetPointIds().SetNumberOfIds(2)

        count_seg = 0
        for indexx in range(4):
            if(vals[indexx] < contour_value < vals[indexx+1]) or (vals[indexx+1] < contour_value < vals[indexx]):
                t = (contour_value - vals[indexx]) / (vals[indexx+1] - vals[indexx])
                x1, y1, z1 = image_data.GetPoint(pids[indexx])
                x2, y2, z2 = image_data.GetPoint(pids[indexx+1])
                
                # print("t", t)
                # print("p1",x1, y1, z1)
                # print("p2",x2, y2, z2)

                # Getting the isocontour coordinates on the edge
                x_intersect = t * (x2 - x1) + x1
                y_intersect = t * (y2 - y1) + y1
                z_intersect = t * (z2 - z1) + z1
                # print("p_int", x_intersect,y_intersect,z_intersect)
                
                # Adding the points
                point_id = points.InsertNextPoint(x_intersect, y_intersect, z_intersect)
                
                # Add the isocontour segment to the vtkCellArray object
                line.GetPointIds().SetId(count_seg, point_id)
                count_seg += 1
        lines_array.InsertNextCell(line)

    poly_data.SetLines(lines_array)
    poly_data.SetPoints(points)


polydata_writer = vtkXMLPolyDataWriter()
polydata_writer.SetInputData(poly_data)
polydata_writer.SetFileName("output.vtp")
polydata_writer.Write()
print("Task Completed.\nSee the output.vtp file for isoconture surface.")