#!/usr/env/pytho
import matplotlib
matplotlib.use('Qt4Agg') 
from matplotlib import pyplot as plt
from matplotlib import cm
import numpy as np
import nibabel as nib
import scipy.ndimage

img = nib.load('/Applications/freesurfer/subjects/EC121_test/acpc/T1.nii')
ct = nib.load('/Applications/freesurfer/subjects/EC121_test/CT/rCT.nii')
img = nib.load('/Applications/freesurfer/subjects/EC143/mri/orig.nii')
ct = nib.load('/Applications/freesurfer/subjects/EC143/CT/rCT.nii')

affine = img.affine
codes = nib.orientations.axcodes2ornt(nib.orientations.aff2axcodes(affine))
img_data = nib.orientations.apply_orientation(img.get_data(), codes)
voxel_sizes = nib.affines.voxel_sizes(affine)
nx,ny,nz=np.array(img_data.shape, dtype='float')

inv_affine = np.linalg.inv(affine)
img_clim = np.percentile(img_data, (1., 99.))

#ct_data = ct.get_data()
ct_codes =nib.orientations.axcodes2ornt(nib.orientations.aff2axcodes(ct.affine))
ct_data = nib.orientations.apply_orientation(ct.get_data(), ct_codes)

cx,cy,cz=np.array(ct.shape, dtype='float')
current_slice = np.array([nx/2, ny/2, nz/2], dtype=np.int)

# Resample both images to the highest resolution
voxsz = (256, 256, 256)
if ct.shape != voxsz:
	print("Resizing voxels in CT")
	ct_data = scipy.ndimage.zoom(ct_data, [voxsz[0]/cx, voxsz[1]/cy, voxsz[2]/cz])
if img.shape != voxsz:
	print("Resizing voxels in MRI")
	img_data = scipy.ndimage.zoom(img_data, [voxsz[0]/nx, voxsz[1]/ny, voxsz[2]/nz])

nx,ny,nz = [256, 256, 256]
cx,cy,cz = [256, 256, 256]

fig=plt.figure()
im = []
ct_im = []

cursor = []
cursor2 = []

ax1 = fig.add_subplot(221)
ax1.set_axis_bgcolor('k')
im.append(plt.imshow(img_data[nx/2,:,:].T, cmap=cm.gray, aspect='auto'))
ct_im.append(plt.imshow(ct_data[nx/2,:,:].T, cmap=cm.hot, aspect='auto',alpha=0.5, vmin=1000, vmax=3000))
cursor.append(plt.plot([ny/2, ny/2], [ax1.get_ylim()[0]+1, ax1.get_ylim()[1]-1], color=[0, 1, 0] ))
cursor2.append(plt.plot([ax1.get_xlim()[0]+1, ax1.get_xlim()[1]-1], [nz/2, nz/2], color=[0, 1, 0] ))
plt.gca().invert_yaxis()
ax1.set_xticks([])
ax1.set_yticks([])
ax1.set_xlabel('Inferior')
ax1.set_ylabel('Posterior')
ax1.axis([0,ny,0,nz])

ax2 = fig.add_subplot(222)
ax2.set_axis_bgcolor('k')
im.append(plt.imshow(img_data[:,ny/2,:].T, cmap=cm.gray, aspect='auto'))
ct_im.append(plt.imshow(ct_data[:,ny/2,:].T, cmap=cm.hot, alpha=0.5, vmin=1000, vmax=3000, aspect='auto'))
cursor.append(plt.plot([nx/2, nx/2], [ax2.get_ylim()[0]+1, ax2.get_ylim()[1]-1], color=[0, 1, 0] ))
cursor2.append(plt.plot([ax2.get_xlim()[0]+1, ax2.get_xlim()[1]-1], [nz/2, nz/2], color=[0, 1, 0] ))
plt.gca().invert_yaxis()
ax2.axis([0,nx,0,nz])
ax2.set_xticks([])
ax2.set_yticks([])
ax2.set_xlabel('Inferior')
ax2.set_ylabel('Left')

ax3 = fig.add_subplot(223)
ax3.set_axis_bgcolor('k')
im.append(plt.imshow(img_data[:,:,nz/2].T, cmap=cm.gray, aspect='auto'))
ct_im.append(plt.imshow(ct_data[:,:,nz/2].T, cmap=cm.hot, alpha=0.5, vmin=1000, vmax=3000, aspect='auto'))
cursor.append(plt.plot([nx/2, nx/2], [ax3.get_ylim()[0]+1, ax3.get_ylim()[1]-1], color=[0, 1, 0] ))
cursor2.append(plt.plot([ax3.get_xlim()[0]+1, ax3.get_xlim()[1]-1], [ny/2, ny/2], color=[0, 1, 0] ))
plt.gca().invert_yaxis()
ax3.set_xticks([])
ax3.set_yticks([])
ax3.axis([0,nx,0,ny])
ax3.set_xlabel('Posterior')
ax3.set_ylabel('Left')

ax4 = fig.add_subplot(224)
im.append(plt.imshow(ct_data.max(0).T, cmap=cm.gray, aspect='auto'))
cursor.append(plt.plot([ny/2, ny/2], [ax4.get_ylim()[0]+1, ax4.get_ylim()[1]-1], color=[0, 1, 0] ))
cursor2.append(plt.plot([ax4.get_xlim()[0]+1, ax4.get_xlim()[1]-1], [nz/2, nz/2], color=[0, 1, 0] ))
ax4.set_xticks([])
ax4.set_yticks([])
plt.gca().invert_yaxis()
ax4.axis([0,ny,0,nz])

#ax4.axis()

im.append(current_slice)

plt.tight_layout()

def on_key(event):
	print('You pressed', event.key)
	bb1=ax1.get_position()
	bb2=ax2.get_position()
	bb3=ax3.get_position()
	bb4=ax4.get_position()

	# Transform coordinates to figure coordinates
	fxy = fig.transFigure.inverted().transform((event.x, event.y))
	print event.x, event.y
	if event.key == 'pageup' or event.key == 'pagedown':
		if event.key == 'pagedown':
			sgn = -1
		else:
			sgn = 1
		if bb1.contains(fxy[0],fxy[1]):
			current_slice[0] = current_slice[0] + 1*sgn
		elif bb2.contains(fxy[0],fxy[1]):
			current_slice[1] = current_slice[1] + 1*sgn
		elif bb3.contains(fxy[0],fxy[1]):
			current_slice[2] = current_slice[2] + 1*sgn
		update_figure_data(im, ct_im, cursor, cursor2, current_slice)

	plt.gcf().canvas.draw()

def on_scroll(event):
	# Zoom on scroll
	stepsz = 10.
	bb1=ax1.get_position()
	bb2=ax2.get_position()
	bb3=ax3.get_position()
	bb4=ax4.get_position()

	# Transform coordinates to figure coordinates
	fxy = fig.transFigure.inverted().transform((event.x, event.y))
	
	# If you clicked the first subplot
	if bb1.contains(fxy[0],fxy[1]):
		xlims = ax1.get_xlim()
		ylims = ax1.get_ylim()
		xstep = event.step*stepsz
		ystep = event.step*stepsz*np.float(nz)/ny
		ax1.set_xlim(xlims[0]+xstep, xlims[1] - xstep)
		ax1.set_ylim(ylims[0]+ystep, ylims[1] - ystep)
	# If you clicked the second subplot
	if bb2.contains(fxy[0],fxy[1]):
		xlims = ax2.get_xlim()
		ylims = ax2.get_ylim()
		xstep = event.step*stepsz
		ystep = event.step*stepsz*np.float(nz)/nx
		ax2.set_xlim(xlims[0]+xstep, xlims[1] - xstep)
		ax2.set_ylim(ylims[0]+ystep, ylims[1] - ystep)

	# If you clicked the third subplot
	if bb3.contains(fxy[0],fxy[1]):
		xlims = ax3.get_xlim()
		ylims = ax3.get_ylim()
		xstep = event.step*stepsz*np.float(nx)/ny
		ystep = event.step*stepsz
		ax3.set_xlim(xlims[0]+xstep, xlims[1] - xstep)
		ax3.set_ylim(ylims[0]+ystep, ylims[1] - ystep)

	# If you clicked the fourth subplot
	if bb4.contains(fxy[0],fxy[1]):
		xlims = ax4.get_xlim()
		ylims = ax4.get_ylim()
		xstep = event.step*stepsz*np.float(nz)/ny
		ystep = event.step*stepsz
		ax4.set_xlim(xlims[0]+xstep, xlims[1] - xstep)
		ax4.set_ylim(ylims[0]+ystep, ylims[1] - ystep)

	plt.gcf().canvas.draw()

def on_click(event):
	#print('You scrolled %d steps at x: %d, y: %d', event.step, event.x, event.y)
	# Get the bounding box for each of the subplots
	bb1=ax1.get_position()
	bb2=ax2.get_position()
	bb3=ax3.get_position()
	bb4=ax4.get_position()

	print event.xdata, event.ydata
	# Transform coordinates to figure coordinates
	fxy = fig.transFigure.inverted().transform((event.x, event.y))
	
	x = np.int(np.round(event.xdata))
	y = np.int(np.round(event.ydata))
	# If you clicked the first subplot
	if bb1.contains(fxy[0],fxy[1]):
		current_slice[1] = event.xdata
		current_slice[2] = event.ydata
		im[1].set_data(img_data[:,x,:].T)
		im[2].set_data(img_data[:,:,y].T)
		ct_im[1].set_data(ct_data[:,x,:].T)
		ct_im[2].set_data(ct_data[:,:,y].T)
		cursor[0][0].set_xdata([event.xdata, event.xdata])
		cursor2[0][0].set_ydata([event.ydata, event.ydata])
		cursor2[1][0].set_ydata([event.ydata, event.ydata])
		cursor2[2][0].set_ydata([event.xdata, event.xdata])
		cursor[3][0].set_xdata([event.xdata, event.xdata])
		cursor2[3][0].set_ydata([event.ydata, event.ydata])
		
	# If you clicked the second subplot
	elif bb2.contains(fxy[0],fxy[1]):
		current_slice[0] = event.xdata
		current_slice[2] = event.ydata

	# If you clicked the third subplot
	elif bb3.contains(fxy[0],fxy[1]):
		current_slice[0] = event.xdata
		current_slice[1] = event.ydata

	# If you clicked the third subplot
	elif bb4.contains(fxy[0],fxy[1]):
		current_slice[1] = event.xdata
		current_slice[2] = event.ydata
	
	update_figure_data(im, ct_im, cursor, cursor2, current_slice)

	print("Current slice: %3.2f %3.2f %3.2f"%(current_slice[0], current_slice[1], current_slice[2]))
	plt.gcf().canvas.draw()

def update_figure_data(im, ct_im, cursor, cursor2, current_slice):
	im[0].set_data(img_data[current_slice[0],:,:].T)
	im[1].set_data(img_data[:,current_slice[1],:].T)
	im[2].set_data(img_data[:,:,current_slice[2]].T)

	ct_im[0].set_data(ct_data[current_slice[0],:,:].T)
	ct_im[1].set_data(ct_data[:,current_slice[1],:].T)
	ct_im[2].set_data(ct_data[:,:,current_slice[2]].T)

	cursor[0][0].set_xdata([current_slice[1], current_slice[1]]) 
	cursor2[0][0].set_ydata([current_slice[2], current_slice[2]])
	cursor[1][0].set_xdata([current_slice[0], current_slice[0]])
	cursor2[1][0].set_ydata([current_slice[2], current_slice[2]])
	cursor[2][0].set_xdata([current_slice[0], current_slice[0]])
	cursor2[2][0].set_ydata([current_slice[1], current_slice[1]])
	cursor[3][0].set_xdata([current_slice[1], current_slice[1]]) 
	cursor2[3][0].set_ydata([current_slice[2], current_slice[2]])

cid2 = fig.canvas.mpl_connect('scroll_event',on_scroll)
cid3 = fig.canvas.mpl_connect('button_press_event',on_click)
cid = fig.canvas.mpl_connect('key_press_event', on_key)

plt.show()
fig.canvas.draw()
#fig.canvas.setFocus()
