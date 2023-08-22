# Import libraries
import vtk
import numpy as np
import random
from vtk import *
import time


## Load data
###################################
reader = vtkXMLImageDataReader()
reader.SetFileName("./Isabel_3D.vti")
reader.Update()
image_data = reader.GetOutput()

# Define the sampling percentage
# sampling_percentage = 5
sampling_percentage = input("Enter Sampling percentage in numbers: ").strip()

if not sampling_percentage.isdigit():
    print("Sampling percentage is not a number.")
    print("Exiting...")
    exit()

sampling_percentage = int(sampling_percentage)

method = input("Enter the reconstruction method (linear or nearest): ")

if method not in ["linear", "nearest"]:
    print("Invalid reconstruction method.")
    exit()

dims = image_data.GetDimensions() 
print("Dimension of the dataset:", dims)

dataArr = image_data.GetPointData().GetArray("Pressure")

# Define the indices of the eight corner points
corner_indices = [(0,0,0), (dims[0]-1,0,0), (0,dims[1]-1,0), (0,0,dims[2]-1), 
                  (dims[0]-1,dims[1]-1,0), (dims[0]-1,0,dims[2]-1), (0,dims[1]-1,dims[2]-1), 
                  (dims[0]-1,dims[1]-1,dims[2]-1)]

# Define the number of points to sample
num_points_to_sample = int(np.prod(dims) * sampling_percentage /100)

# Create an empty list to store the sampled points and scalar data
sampled_points = []
sampled_data = []

# Sample the corner points

nx, ny, nz = dims
for index in corner_indices:
  i, j, k = index
  linear_index = k*nx*ny + j*nx + i
  point = image_data.GetPoint(linear_index)
  # print(point)
  data = image_data.GetScalarComponentAsDouble(i, j, k, 0)
  # print(data)
  sampled_points.append(point)
  sampled_data.append(data)


# Sample the remaining points
point_indices = list(range(np.prod(dims)))
random.shuffle(point_indices)
for i in range(num_points_to_sample - len(corner_indices)):
  index = point_indices[i]
  point = image_data.GetPoint(index)
  p1, p2, p3 = map(int, point)
  data = image_data.GetScalarComponentAsDouble(p1,p2,p3, 0)
  sampled_points.append(point)
  sampled_data.append(data)

print("Creating sampled dataset...")

output_file_path = 'sampled_data_{}percent.vtp'.format(sampling_percentage)
# Create the VTP file
polydata = vtk.vtkPolyData()
points = vtk.vtkPoints()
for point in sampled_points:
    points.InsertNextPoint(point)
polydata.SetPoints(points)

# Add the scalar data to the point data
scalars = vtk.vtkFloatArray()
scalars.SetName("Pressure")
for data in sampled_data:
    scalars.InsertNextValue(data)
polydata.GetPointData().SetScalars(scalars)

# Write the VTP file to disk
writer = vtk.vtkXMLPolyDataWriter()
writer.SetFileName(output_file_path)
writer.SetInputData(polydata)
writer.Write()

print("Sampling completed...")
print("Creating reconstruction from the sample data...")

start_time = time.time()

from scipy.interpolate import griddata
from vtk.util.numpy_support import numpy_to_vtk,vtk_to_numpy

# Get the data values for the sampled points
data_vtk = polydata.GetPointData().GetArray("Pressure")
data = vtk_to_numpy(data_vtk)
# print(data)

# Extract the point coordinates from the polydata
points_vtk = polydata.GetPoints()
points = vtk_to_numpy(points_vtk.GetData())
# print("Shape of points", points.shape)

# Create the grid for reconstruction
x = np.linspace(0, dims[0] - 1, dims[0])
y = np.linspace(0, dims[1] - 1, dims[1])
z = np.linspace(0, dims[2] - 1, dims[2])
zz, yy, xx = np.meshgrid(z, y, x, indexing='ij')

# print("xx",xx.shape)
# print("yy",yy.shape)
# print("zz",zz.shape)

def replace_nans(data):
    # Replace any NaN values in the data with nearest neighbor values
    x, y, z = np.indices(data.shape)
    nan_mask = np.isnan(data)
    data[nan_mask] = griddata((x[~nan_mask], y[~nan_mask], z[~nan_mask]), data[~nan_mask], (x[nan_mask], y[nan_mask], z[nan_mask]), method='nearest')
    return data

if(method == 'nearest'):
  interp_data = griddata(points, data,(xx, yy, zz), method='nearest')
else:
  interp_data = griddata(points, data,(xx, yy, zz), method='linear', fill_value=np.nan)
  interp_data = replace_nans(interp_data)

# Create a VTKImageData object to store the reconstructed volume
volume = vtk.vtkImageData()
volume.SetDimensions(dims)
volume.SetSpacing(1, 1, 1)
volume.SetOrigin(0, 0, 0)

# Assign the reconstructed data to the volume
vtk_data = numpy_to_vtk(interp_data.flatten(), deep=True)
vtk_data.SetName('Pressure')
volume.GetPointData().SetScalars(vtk_data)

# Write the reconstructed volume to disk as a VTI file
writer = vtk.vtkXMLImageDataWriter()
writer.SetFileName('recons_{}{}.vti'.format(method, sampling_percentage))
writer.SetInputData(volume)
writer.Write()

end_time = time.time()
elapsed_time = end_time - start_time
elapsed_time = round(elapsed_time, 3)

print("Task Completed...")

def compute_SNR(arrgt, arr_recon):
    diff = arrgt - arr_recon
    sqd_max_diff = (np.max(arrgt) - np.min(arrgt))**2
    snr = 10 * np.log10(sqd_max_diff / np.mean(diff**2))
    return round(snr, 3)

# Calculate the SNR between the original and reconstructed volumes
arrgt = vtk_to_numpy(image_data.GetPointData().GetScalars())
arr_recon = vtk_to_numpy(volume.GetPointData().GetScalars())

# snr_nearest = computer_SNR(arrgt, arr_recon_nearest)
snr = compute_SNR(arrgt, arr_recon)

if method=='nearest':
  print("SNR for nearest interpolation from {} percent sample:".format(sampling_percentage), snr)
else:
  print("SNR for linear interpolation from {} percent sample:".format(sampling_percentage), snr)

print("Time taken for reconstruction from sampled data: {} seconds".format(elapsed_time))