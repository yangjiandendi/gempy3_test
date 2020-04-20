"""
Adding topography to geological models
======================================

"""

import sys
sys.path.append("../../..")

import gempy as gp
import numpy as np
import matplotlib.pyplot as plt
import os


######################################################################
# 1. The common procedure to set up a model:
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 

geo_model = gp.create_model('Single_layer_topo')
data_path= '../..'
gp.init_data(geo_model, extent=[450000, 460000, 70000,80000,-1000,500],resolution = (50,50,50),
                         path_i = data_path+"/data/input_data/tut-ch1-7/onelayer_interfaces.csv",
                         path_o = data_path+"/data/input_data/tut-ch1-7/onelayer_orient.csv")

# use happy spring colors! 
geo_model.surfaces.colors.change_colors({'layer1':'#ff8000','basement':'#88cc60'})

# %matplotlib inline
gp.map_series_to_surfaces(geo_model, {'series':('layer1','basement')})

s = {'s1': ([450000,75000],[460000,75500],[100,100])}
geo_model.grid.create_section_grid(s)


######################################################################
# 2. Adding topography
# ~~~~~~~~~~~~~~~~~~~~
# 


######################################################################
# 2 a. Load from raster file
# ^^^^^^^^^^^^^^^^^^^^^^^^^^
# 

fp = data_path+"/data/input_data/tut-ch1-7/bogota.tif"

geo_model.set_topography(source='gdal',filepath=fp)


######################################################################
# 2 b. create fun topography
# ^^^^^^^^^^^^^^^^^^^^^^^^^^
# 


######################################################################
# If there is no topography file, but you think that your model with
# topography would look significantly cooler, you can use gempys function
# to generate a random topography based on a fractal grid:
# 

geo_model.set_topography(source='random')


######################################################################
# It has additional keywords to play around with: - fd: fractal dimension,
# defaults to 2.0. The higher (try 2.9), the rougher the landscape will
# be. - d_z: height difference. If none, last 20% of the model in z
# direction. - extent: extent in xy direction. If none,
# geo_model.grid.extent - resolution: resolution of the topography array.
# If none, geo_model.grid.resoution. Increasing the resolution leads to
# much nicer geological maps!
# 

geo_model.set_topography(source='random',fd=1.9, d_z=np.array([0,250]), resolution=np.array([200,200]))


######################################################################
# Note that each time this function is called, a new random topography is
# created. If you particularly like the generated topography or if you
# have loaded a large file with gdal, you can save the topography object
# and load it again later:
# 

#save
geo_model.grid.topography.save('test_topo')

#load
geo_model.set_topography(source='saved',filepath='test_topo.npy')


######################################################################
# Compute model
# ~~~~~~~~~~~~~
# 

gp.set_interpolation_data(geo_model,
                          compile_theano=True,
                          theano_optimizer='fast_compile')

gp.compute_model(geo_model, compute_mesh=False, set_solutions=True)


######################################################################
# Visualize:
# ^^^^^^^^^^
# 
# Now, the solutions object does also contain the computed geological map.
# It can be visualized using the plot_map function:
# 

gp.plot.plot_map(geo_model, contour_lines=False, show_data=False)

gp.plot.plot_section(geo_model, cell_number=4, block=geo_model.solutions.lith_block,
                         direction='y', show_data=True,show_faults=False)

gp.plot.plot_section_by_name(geo_model,'s1')
