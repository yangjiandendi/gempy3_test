"""
    This file is part of gempy.

    gempy is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    gempy is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with gempy.  If not, see <http://www.gnu.org/licenses/>.


Created on 14/06/2019

@author: Elisa Heim
"""

import warnings
import os


import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import seaborn as sns
import numpy as np
from os import path
import sys
# This is for sphenix to find the packages
sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )
from gempy.core.solution import Solution
from matplotlib.ticker import FixedFormatter, FixedLocator

class PlotSolution:
    #Todo plot data filtered for sections and map
    def __init__(self, model):

        self.model = model

        self._color_lot = dict(zip(self.model.surfaces.df['surface'], self.model.surfaces.df['color']))
        self._cmap = mcolors.ListedColormap(list(self.model.surfaces.df['color']))
        self._norm = mcolors.Normalize(vmin=0.5, vmax=len(self._cmap.colors)+0.5)

    def plot_map(self, solution: Solution = None, contour_lines=True, show_faults = True, show_data=False):
        if solution is not None:
            assert solution.geological_map is not None, 'Geological map not computed. Activate the topography grid.'
        else:
            solution = self.model.solutions
        geomap = solution.geological_map.reshape(self.model.grid.topography.values_3D[:,:,2].shape)
        if show_data:
            self.plot_data(direction='z')
        else:
            fig, ax = plt.subplots(figsize=(6,6))
        plt.imshow(geomap, origin="lower", extent=self.model.grid.topography.extent, cmap=self._cmap, norm=self._norm)
        if contour_lines==True and show_data==False:
            CS = ax.contour(self.model.grid.topography.values_3D[:, :, 2],  cmap='Greys', linestyles='solid',
                            extent=self.model.grid.topography.extent)
            ax.clabel(CS, inline=1, fontsize=10, fmt='%d')
            cbar = plt.colorbar(CS)
            cbar.set_label('elevation [m]')
        if show_faults == True:
            self.extract_section_fault_lines('topography')
        plt.title("Geological map", fontsize=15)
        plt.xlabel('X')
        plt.ylabel('Y')

    def extract_section_fault_lines(self, section_name=None, axes=None):
        # Todo merge this with extract fault lines
        faults = list(self.model.faults.df[self.model.faults.df['isFault'] == True].index)
        if section_name == 'topography':
            shape = self.model.grid.topography.resolution
            a = self.model.solutions.geological_map_scalfield
        else:
            l0, l1 = self.model.grid.sections.get_section_args(section_name)
            j = np.where(self.model.grid.sections.names == section_name)[0][0]
            shape = self.model.grid.sections.resolution[j]
            a = self.model.solutions.sections_scalfield[:, l0:l1]
        for fault in faults:
            f_id = int(self.model.series.df.loc[fault, 'order_series']) - 1
            block = a[f_id]
            level = self.model.solutions.scalar_field_at_surface_points[f_id][np.where(
                self.model.solutions.scalar_field_at_surface_points[f_id] != 0)]
            if section_name == 'topography':
                plt.contour(block.reshape(shape), 0, levels=level, colors=self._cmap.colors[f_id], linestyles='solid',
                            extent=self.model.grid.topography.extent)
            else:
                if axes is not None:
                    axes.contour(block.reshape(shape).T, 0, levels=level, colors=self._cmap.colors[f_id],
                                linestyles='solid',
                                extent=[0, self.model.grid.sections.dist[j],
                                        self.model.grid.regular_grid.extent[4],
                                        self.model.grid.regular_grid.extent[5]])
                else:
                    plt.contour(block.reshape(shape).T, 0, levels=level, colors=self._cmap.colors[f_id], linestyles='solid',
                             extent=[0, self.model.grid.sections.dist[j],
                                     self.model.grid.regular_grid.extent[4],
                                     self.model.grid.regular_grid.extent[5]])



    def plot_sections(self, show_traces=True, show_data=False, section_names = None, show_faults = True, show_topo=True,
                      figsize=(12,12)):
        assert self.model.solutions.sections is not None, 'no sections for plotting defined'
        if section_names is not None:
            if type(section_names) == list:
                section_names = np.array(section_names)
        else:
            section_names = self.model.grid.sections.names
        if show_traces:
            self.plot_section_traces(show_data=show_data, section_names=section_names, contour_lines=False)
        shapes = self.model.grid.sections.resolution
        zdist = self.model.grid.regular_grid.extent[5] - self.model.grid.regular_grid.extent[4]
        fig, axes = plt.subplots(nrows=len(section_names), ncols=1,figsize=figsize)
        #plt.subplots_adjust(bottom=0.5, top=3)
        for i, section in enumerate(section_names):
            j = np.where(self.model.grid.sections.names == section)[0][0]
            l0, l1 = self.model.grid.sections.get_section_args(section)
            if len(section_names) == 1:
                if show_faults:
                    self.extract_section_fault_lines(section, axes)
                if show_topo:
                    xy = self.slice_topo_for_sections(j)
                    #axes.plot(xy[:,0],xy[:,1])
                    axes.fill(xy[:, 0], xy[:, 1], 'k', zorder=10)

                axes.imshow(self.model.solutions.sections[0][l0:l1].reshape(shapes[j][0], shapes[j][1]).T,
                               origin='bottom',
                               cmap=self._cmap, norm=self._norm, extent=[0, self.model.grid.sections.dist[j],
                                                                         self.model.grid.regular_grid.extent[4],
                                                                         self.model.grid.regular_grid.extent[5]])

                labels, axname = self._make_section_xylabels(section, len(axes.get_xticklabels()) - 2)
                pos_list = np.linspace(0, self.model.grid.sections.dist[j], len(labels))
                axes.xaxis.set_major_locator(FixedLocator(nbins=len(labels), locs=pos_list))
                axes.xaxis.set_major_formatter(FixedFormatter((labels)))
                axes.set(title=self.model.grid.sections.names[j], xlabel=axname, ylabel='Z')

            else:
                if show_faults:
                    self.extract_section_fault_lines(section, axes[i])
                if show_topo:
                    xy = self.slice_topo_for_sections(j)
                    axes[i].fill(xy[:,0],xy[:,1],'k', zorder=10)
                    #axes[i].plot(xy[:, 0], xy[:, 1])
                axes[i].imshow(self.model.solutions.sections[0][l0:l1].reshape(shapes[j][0], shapes[j][1]).T,
                               origin='bottom',
                               cmap=self._cmap, norm=self._norm, extent=[0, self.model.grid.sections.dist[j],
                                                                         self.model.grid.regular_grid.extent[4],
                                                                         self.model.grid.regular_grid.extent[5]])

                labels, axname = self._make_section_xylabels(section, len(axes[i].get_xticklabels()) - 2)
                pos_list = np.linspace(0, self.model.grid.sections.dist[j], len(labels))
                axes[i].xaxis.set_major_locator(FixedLocator(nbins=len(labels), locs=pos_list))
                axes[i].xaxis.set_major_formatter(FixedFormatter((labels)))
                axes[i].set(title=self.model.grid.sections.names[j], xlabel=axname, ylabel='Z')
            #axes[i].set_aspect(self.model.grid.sections.dist[i] / zdist)
        fig.tight_layout()

    def _make_section_xylabels(self, section_name, n=5):
        j = np.where(self.model.grid.sections.names == section_name)[0][0]
        indexes = np.linspace(0, int(len(self.model.grid.sections.xaxis[j])), n).astype(int)
        indexes[-1] -= 1
        if len(np.unique(self.model.grid.sections.xaxis[j])) == 1:
            labels = self.model.grid.sections.yaxis[j][indexes].astype(int)
            axname = 'Y'
        elif len(np.unique(self.model.grid.sections.yaxis[j])) == 1:
            labels = self.model.grid.sections.xaxis[j][indexes].astype(int)
            axname = 'X'
        else:
            labels = [str(int(self.model.grid.sections.xaxis[j][indexes][i])) + ',\n' +
                      str(int(self.model.grid.sections.yaxis[j][indexes][i]))
                      for i in range(len(indexes))]
            axname = 'X,Y'
        return labels, axname

    def slice_topo_for_sections(self, j):
        startend = list(self.model.grid.sections.section_dict.values())[j]
        points = [(startend[0]), (startend[1])]
        if points[0][0] == points[1][0]:
            step = (self.model.grid.topography.extent[3] - self.model.grid.topography.extent[2]) / \
                   self.model.grid.topography.resolution[1]
            cell_number = np.round((points[0][1] - self.model.grid.topography.extent[2]) / step).astype(int)
            a = self.slice_topo_verthor('y', cell_number)
        elif points[0][1] == points[1][1]:
            step = (self.model.grid.topography.extent[1] - self.model.grid.topography.extent[0]) / \
                   self.model.grid.topography.resolution[0]
            cell_number = np.round((points[0][0] - self.model.grid.topography.extent[0]) / step).astype(int)
            a = self.slice_topo_verthor('x', cell_number)
        else:
            a = self.slice_topo_diagonal(points, j)
        # redistribute x values for plotting
        a[:,0] = np.linspace(0,self.model.grid.sections.dist[j][0], a.shape[0])
        a = np.append(a,
                      ([self.model.grid.sections.dist[j][0], a[:, 1][-1]],
                      [self.model.grid.sections.dist[j][0], self.model.grid.regular_grid.extent[5]],
                      [0, self.model.grid.regular_grid.extent[5]],
                      [0, a[:, 1][0]]))
        return a.reshape(-1, 2)

    def slice_topo_diagonal(self, points, j):
        ### I have checked, this is the most complicated way to do it.
        # calculate line equation
        x_coords, y_coords = zip(*points)
        A = np.vstack([x_coords, np.ones(len(x_coords))]).T
        m, c = np.linalg.lstsq(A, y_coords, rcond=None)[0]
        # print("Line Solution is y = {m}x + {c}".format(m=m,c=int(c)))
        idx_start_x = (np.abs(self.model.grid.topography.values_3D[:, :, 0][0, :] - points[0][0])).argmin()
        idx_end_x = (np.abs(self.model.grid.topography.values_3D[:, :, 0][0, :] - points[1][0])).argmin()
        xvals = self.model.grid.topography.values_3D[:, :, 0][0, :][idx_start_x:idx_end_x]
        yvals = (m * xvals[[0, -1]] + c).astype(int)
        idx_start_y = (np.abs(self.model.grid.topography.values_3D[:, :, 1][:, 0] - yvals[0])).argmin()
        idx_end_y = (np.abs(self.model.grid.topography.values_3D[:, :, 1][:, 0] - yvals[1])).argmin()
        box = self.model.grid.topography.values_3D[idx_start_x:idx_end_x, idx_start_y:idx_end_y][:, :, 2]

        zvals = np.diag(np.flipud(box))  # flip it to get the right diagonal
        print(xvals.shape, zvals.shape)
        if xvals.shape != zvals.shape:
            raise AssertionError
        return np.vstack([xvals, zvals]).T

    def slice_topo_verthor(self, direction='y', cell_number=1):
        '''cell_number: topography cell number, not regular grid'''
        x = self.model.grid.topography.values_3D[:, :, 0]
        y = self.model.grid.topography.values_3D[:, :, 1]
        z = self.model.grid.topography.values_3D[:, :, 2]

        if direction == 'y':
            a = x[cell_number, :]
            b = y[cell_number, :]
            c = z[cell_number, :]
            assert len(np.unique(b)) == 1
            topoline = np.dstack((a, c)).reshape(-1, 2).astype(int)

        elif direction == 'x':
            a = x[:, cell_number]
            b = y[:, cell_number]
            c = z[:, cell_number]
            assert len(np.unique(a)) == 1
            topoline = np.dstack((b, c)).reshape(-1, 2).astype(int)

        elif direction == "z":
            raise NotImplementedError

        return topoline


    def plot_section_traces(self, show_data=False, section_names=None, contour_lines = True):
        # fig = plt.figure()
        # ax = fig.add_subplot(111)
        if section_names is None:
            section_names = self.model.grid.sections.names

        if self.model.solutions.geological_map is not None:
            self.plot_map(self.model.solutions, contour_lines=contour_lines, show_data=show_data)
        elif self.model.solutions.lith_block.shape[0] != 0:
            print('implement block section')
            pass
            self.plot_block_section(self.model.solutions, cell_number=self.model.grid.regular_grid.resolution[2] - 1,
                                 direction='z', show_faults=False, show_topo=False, show_data=show_data)
            plt.title('Section traces, z direction')
        else:
            #fig = plt.figure()
            #plt.title('Section traces, z direction')
            if show_data:
                self.plot_data('z', 'all')
        for section in section_names:
            j = np.where(self.model.grid.sections.names == section)[0][0]
            plt.plot([self.model.grid.sections.points[j][0][0], self.model.grid.sections.points[j][1][0]],
                     [self.model.grid.sections.points[j][0][1], self.model.grid.sections.points[j][1][1]],
                     label=section, linestyle='--')

            plt.xlim(self.model.grid.regular_grid.extent[:2])
            plt.ylim(self.model.grid.regular_grid.extent[2:4])
            # ax.set_aspect(np.diff(geo_model.grid.regular_grid.extent[:2])/np.diff(geo_model.grid.regular_grid.extent[2:4]))
        plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)