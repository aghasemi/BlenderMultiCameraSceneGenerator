
#filename='/home/ghasemi/blenderscript.py'
#exec(compile(open(filename).read(), filename, 'exec'))
#Run this from your terminal
# blender -b template.blend -P lin_array.py

import bpy
import os
import time
from bpy import data as D
from bpy import context as C
from random import gauss
from mathutils import *
from math import *
from subprocess import call

#Paints given image on the given object(plane)
def loadImage(imgName,ob):
	img = bpy.data.images.new(name='textureImage',width=1000,height=1000)
	img.source='FILE';
	img.filepath=imgName
	#img = img.recast_type()
	tex = bpy.data.textures.new('TextureName',type='IMAGE')
	print("Recast", tex, tex.type)
	print("Done", tex, tex.type)
	tex.image = img
	mat = bpy.data.materials.new('MatName')
	matto=mat.texture_slots.add()
	matto.texture=tex;
	matto.texture_coords = 'ORCO'
	matto.mapping = 'CUBE'
	bpy.ops.object.material_slot_remove()
	me = ob.data
	me.materials.append(mat)
	#Amount of repetition
	tex.repeat_x=1
	tex.repeat_y=2
	return

#Builds a noisy trajectory in 1D and necessarily positive (for use in X trajectory)
def build_traj_pos(m,nv):
	#Location deviations
	location_noise_variance=nv; #One hundredth of the baseline
	Tx=[]; #Camera trajectory
	##Forming the noise trajectory
	for i in range(0,m+1):
		tn=gauss(0,location_noise_variance)#+b*i/m ??
		Tx.append(tn);
	for i in range(1,m+1):
		Tx[i]=Tx[i]+Tx[i-1]; #Speed
	min_Tx=min(Tx);
	for i in range(0,m+1):
		Tx[i]=Tx[i]-min_Tx; #Force speed to be positive (with min of exactly 0)
	for i in range(1,m+1):
		Tx[i]=Tx[i]+Tx[i-1]; #Position
	return Tx

#Builds a noisy trajectory in 1D "NOT" necessarily positive (for use in Z)
def build_traj(m,nv):
	#Location deviations
	location_noise_variance=nv; #One hundredth of the baseline
	Tx=[]; #Camera trajectory
	##Forming the noise trajectory
	for i in range(0,m+1):
		tn=gauss(0,location_noise_variance)#+b*i/m ??
		Tx.append(tn);
	for i in range(1,m+1):
		Tx[i]=Tx[i]+Tx[i-1]; #Speed

	return Tx




#Main part


scene = bpy.data.scenes["Scene"];

#Prapring for image capture
scene.animation_data_clear();
bpy.context.active_object.animation_data_clear()
for a in bpy.data.actions: a.user_clear()  
scene.render.image_settings.file_format='PNG'


#Setting the 6DOF location of the object under consideration
bpy.data.objects['Plane'].select=1;
bpy.data.objects['Plane'].location=(0,20,0)
bpy.data.objects["Plane"].rotation_euler=Euler((pi/2, 0.0, 0.0), 'XYZ')
loadImage('repet.jpg',bpy.data.objects["Plane"])

m=300;
n1=1280;
n2=720;
b=1;
name='imprecise'+str(time.time())+'';

#X axis trajectory
Tx=build_traj_pos(m,b/10); #b/10 is noise variance
max_Tx=max(Tx)+0.0;
for i in range(0,m+1):
	Tx[i]=b*Tx[i]/max_Tx; #Force baseline to be 0

#Z axis trajectory
Tz=build_traj(m,b/100); #Second argument is noise variance
mean_Tz=sum(Tz)/(m+1.0); 
for i in range(0,m+1):
	Tz[i]=Tz[i]-mean_Tz; #So that the average of noise in Z axis is 0


for i in range(0,m+1):
	
	#Select the camera	
	bpy.data.objects['Camera'].select=1;


	#Specify the camera orientation
	noise_variance=0.0*pi/180;  #No orientaion noise for now!!!
	rX=gauss(0,noise_variance); #This one is around X axis (jittering up and down)
	rZ=gauss(0,noise_variance); #This one is around Z axis (image plane rotates, I think)
	rY=gauss(0,noise_variance); #This one is around Y axis (jittering left and right)
	camera_orientation=(pi/2+rX, 0.0+rZ, 0.0+rY);
	bpy.data.objects['Camera'].rotation_euler=Euler(camera_orientation, 'XYZ')

	
	

	
	
	#Specify camera location
	#!! It is (X,Z,Y) actually
	#camera_location=(b*i/m,0,0);
	camera_location=(Tx[i],Tz[i],0);
	bpy.data.objects['Camera'].location=camera_location;



	#Intrinsic parameters for iPhone 5
	bpy.data.objects['Camera'].data.sensor_width=2.27; # length in millimeters
	bpy.data.objects['Camera'].data.sensor_height=1.7;
	bpy.data.objects["Camera"].data.lens=2.52; #This is focal length

	#Finally render the frame
	scene.render.filepath = name+str(i);
	scene.render.resolution_x = n1 #perhaps set resolution in code
	scene.render.resolution_y = n2
	bpy.ops.render.render(write_still=True)
	
os.system('ffmpeg'+' -r 30 -f image2 -i '+name+'%d.png '+'./'+name+'.avi -crf 15')
#print('ffmpeg'+' -r 30 -f image2 -i '+name+'/'+name+'%d.png ../'+name+'.avi -crf 15');
os.system('rm -f '+name+'*.png ')
os.system('rm -rf '+name)
#exit(2)
