#!/usr/bin/env python3

from vtk import *

# Load the data
reader = vtkXMLImageDataReader()
reader.SetFileName("Isabel_3D.vti")
reader.Update()

# Create color transfer function
color_tf = vtkColorTransferFunction()
color_tf.AddRGBPoint(-4931.54, 0, 1, 1)
color_tf.AddRGBPoint(-2508.95, 0, 0, 1)
color_tf.AddRGBPoint(-1873.9, 0, 0, 0.5)
color_tf.AddRGBPoint(-1027.16, 1, 0, 0)
color_tf.AddRGBPoint(-298.031, 1, 0.4, 0)
color_tf.AddRGBPoint(2594.97, 1, 1, 0)

# Create opacity transfer function
opacity_tf = vtkPiecewiseFunction()
opacity_tf.AddPoint(-4931.54, 1.0)
opacity_tf.AddPoint(101.815, 0.002)
opacity_tf.AddPoint(2594.97, 0.0)

# Set up volume mapper
volume_mapper = vtkSmartVolumeMapper()
volume_mapper.SetInputData(reader.GetOutput())

# Set up volume
volume = vtkVolume()
volume.SetMapper(volume_mapper)
volume.SetProperty(vtkVolumeProperty())
volume.GetProperty().SetColor(color_tf)
volume.GetProperty().SetScalarOpacity(opacity_tf)

# Add an outline to the volume rendered data
outline = vtkOutlineFilter()
outline.SetInputData(reader.GetOutput())
outline_mapper = vtkPolyDataMapper()
outline_mapper.SetInputConnection(outline.GetOutputPort())
outline_actor = vtkActor()
outline_actor.SetMapper(outline_mapper)

# Get input from user if they want to use Phong shading
use_phong = input("Do you want to use Phong shading (yes/no)? ")
if use_phong.lower() == "yes":
    volume.GetProperty().ShadeOn()
    volume.GetProperty().SetAmbient(0.5)
    volume.GetProperty().SetDiffuse(0.5)
    volume.GetProperty().SetSpecular(0.5)

# Create a 1000x1000 sized render window
ren = vtkRenderer()
ren.SetBackground(0.9,0.9,0.9)
ren.AddVolume(volume)
ren.AddActor(outline_actor)

ren_win = vtkRenderWindow()
ren_win.SetSize(1000, 1000)
ren_win.AddRenderer(ren)

# Show the rendering result
iren = vtkRenderWindowInteractor()
iren.SetRenderWindow(ren_win)

ren.ResetCamera()
ren.GetActiveCamera().Azimuth(180)
ren.GetActiveCamera().Elevation(-5)
ren.ResetCameraClippingRange()

iren.Initialize()
iren.Start()
