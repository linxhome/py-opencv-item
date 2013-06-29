#setencoding:utf-8
#find the edge of the data range through the color sample
import cv2.cv as cv
import cv2
from math import sin, cos, sqrt, pi
import sys
import os
import time
import string
import subprocess
import pyutil.util as util
import pyutil.errors as errors

tesseract_exe_name = 'OCR/tesseract' # Name of executable to be called at command line
scratch_image_name = "temp.bmp" # This file must be .bmp or other Tesseract-compatible format
scratch_text_name_root = "temp" # Leave out the .txt extension
cleanup_scratch_flag = True  # Temporary files cleaned up after OCR operation

#获得某目录下所有的图片，返回一个序列
def get_all_pic(imgdir):
    if os.path.isdir(imgdir):
        list = os.listdir(imgdir)
        imglist = []
        for file in list:
            path = imgdir+"/"+file
            if os.path.isdir(path):
               pass
            else:
                imglist.append(path)
        return imglist
    else:
        return [];

#获取样本的颜色空间
def getcolorrange(sample):
    samplesrc = cv.LoadImageM(sample)
    size = cv.GetSize(samplesrc)
    width = size[0]-1
    height = size[1]-1
    hist = {}
    #统计样本的颜色范围
    hsv = cv.CreateImage (cv.GetSize (samplesrc), 8, 3);
    cv.CvtColor(samplesrc, hsv, cv.CV_BGR2HSV);
    #不统计白色，v分量为0的直接略过
    for y in range(0,height):
        for x in range(0,width):
             h =  cv.Get2D(hsv,y,x)[0]/2;
             s =  cv.Get2D(hsv,y,x)[1]/255; 
             v =  cv.Get2D(hsv,y,x)[2]/255;
             if v > 0.92 or v < 0.04:
                continue
             index = str(h)+"_"+str(s)+"_"+str(v)
             if hist.has_key(index):
                hist[index] += 1
             else:
                hist[index] = 1 
    sum=0
    h_squa =s_squa=0
    for k,v in hist.items():
        keys = str(k).split("_")
        h = keys[0]
        s = keys[1]
        num = int(v)
        sum += num
        h_squa += num*float(h) 
        s_squa += num*float(s)
    h_aver = h_squa/sum
    s_aver = s_squa/sum
    h_min = h_max = h_aver 
    s_max = s_min = s_aver 
    for k,v in hist.items():
        keys = str(k).split("_");
        h = keys[0]
        h = float(h)
        s = keys[1]
        s = float(s)
        if abs(h-h_aver) < 5:
            if h>h_max:
                h_max = h
            elif h<h_min:
                h_min = h
        if abs(s-s_aver)<0.05:
            if s>s_max:
                s_max = s
            elif s<s_min:
                s_min = s
          
    print "h值的范围是(min,max)",h_min,h_max
    print "s值的范围是(min,max)",s_min,s_max
    return {'h_min':h_min,'h_max':h_max,'s_min':s_min,'s_max':s_max}

#根据样本的颜色空间，取原图中的在这些颜色空间附近的点生成一张新图，看看效果
def getdatepic(colorrange,srcfile,toprange=0,bottomrange=1):
    h_min = colorange.h_min
    h_max = colorange.h_max
    s_min = colorange.s_min
    s_max = colorange.s_max
          
    #根据取样的值来确定数据区所在的位置
    src = cv.LoadImageM(srcfile)
    size = cv.GetSize(src)
    width = size[0]-1
    height = size[1]-1
    hsv = cv.CreateImage (cv.GetSize (src), 8, 3);
    cv.CvtColor(src, hsv, cv.CV_BGR2HSV)
    y_range = {}
    x_range = {}
    #根据取样的颜色范围确定需要的数据区域
    top = height*toprange
    bottom = height*bottomrange
    for y in range(0,height):
        for x in range(0,width):
             h =  cv.Get2D(hsv,y,x)[0]/2;
             s =  cv.Get2D(hsv,y,x)[1]/255; 
             v =  cv.Get2D(hsv,y,x)[2]/255;
             if h>=h_min and h<=h_max and y>top and y < bottom   :
                 if y_range.has_key(y):
                    y_range[y] += 1;
                 else :
                    y_range[y] = 1 ;
                 if x_range.has_key(x):
                    x_range[x] += 1
                 else:
                    x_range[x] = 1
             else:
                 pix = [255,255,255]

#根据样本的颜色空间，取得源图中的数据区域，第一个参数是样本，第二个参数是原图
def getdataedge(colorange,srcfile,toprange=0,bottomrange=1):
    h_min = colorange.h_min
    h_max = colorange.h_max
    s_min = colorange.s_min
    s_max = colorange.s_max
          
    #根据取样的值来确定数据区所在的位置
    src = cv.LoadImageM(srcfile)
    size = cv.GetSize(src)
    width = size[0]-1
    height = size[1]-1
    hsv = cv.CreateImage (cv.GetSize (src), 8, 3);
    cv.CvtColor(src, hsv, cv.CV_BGR2HSV)
    y_range = {}
    x_range = {}
    #根据取样的颜色范围确定需要的数据区域
    top = height*toprange
    bottom = height*bottomrange
    for y in range(0,height):
        for x in range(0,width):
             h =  cv.Get2D(hsv,y,x)[0]/2;
             s =  cv.Get2D(hsv,y,x)[1]/255; 
             v =  cv.Get2D(hsv,y,x)[2]/255;
             if h>=h_min and h<=h_max and y>top and y < bottom   :
                 if y_range.has_key(y):
                    y_range[y] += 1;
                 else :
                    y_range[y] = 1 ;
                 if x_range.has_key(x):
                    x_range[x] += 1
                 else:
                    x_range[x] = 1
             else:
                 pix = [255,255,255]

    y_min = height
    y_max =0
    for y,num in y_range.items():
        if num<20:
            del y_range[y]
        else:
            if y>y_max:
                y_max = y
            if y<y_min:
                y_min = y
    #print "数据区域的范围是(y)",y_min,y_max
    x_min = width
    x_max =0
    for x,num in x_range.items():
        if num<20:
            del x_range[x]
        else:
            if x>x_max:
                x_max = x
            if x<x_min:
                x_min = x
    #print "数据区域的范围是(x)",x_min,x_max
   
    #print "将数据范围朝外放大10个像素"
    if x_min -10 > 0 :
        x_min -= 10
    else:
        x_min = 0
    if x_max + 10 < width:
        x_max += 10
    else:
        x_max = width
    if y_min - 10 > 0:
       y_min -= 10
    else:
       y_min = 0
    if y_max + 10 < height:
       y_max += 10
    else:
       y_max = height
    print x_min,x_max,y_min,y_max
    return {'x':x_min,'y':y_min,'width':x_max-x_min,'height':y_max-y_min}

#对选定的区域对图片进行二值化    
def blackwhite(srcfile,rect,two=120):
    #根据刚才计算出来的范围，裁剪图片
    x_min=rect['x']
    y_min=rect['y']
    x_max=rect['x'] + rect['width']
    y_max=rect['y'] + rect['height']
    #cv.CreateImage (cv.GetSize (src), 8, 3);
    src = cv.LoadImageM(srcfile)
    sep = cv.CreateImage(cv.GetSize(src),8,3)
    height = cv.GetSize(src)[1];
    width = cv.GetSize(src)[0];
    for y in range(0,height):
        for x in range(0,width):
             g =  cv.Get2D(src,y,x)[0];
             b =  cv.Get2D(src,y,x)[1]; 
             r =  cv.Get2D(src,y,x)[2];
             if x>x_max or x<x_min or y>y_max or y<y_min :
                 pix = [0,0,0] 
             else:
                 pix = [g,b,r]
             cv.Set2D(sep,y,x,pix)

    grey_img =  cv.CreateImage(cv.GetSize(sep),cv. IPL_DEPTH_8U, 1);  
    cv.CvtColor(sep, grey_img,cv.CV_BGR2GRAY);  
    #灰度化
    #src = cv.LoadImage(pic, 0)
    bw = cv.CreateImage(cv.GetSize(src), cv.IPL_DEPTH_8U, 1)
    #二值化
    cv.Threshold(grey_img,bw, two, 255, 0);
    #反色
    cv.Not(bw,bw)
    basename = os.path.basename(srcfile)
    basename = string.replace(basename,".jpg","")
    blackwhite=basename+"_black.jpg"
    cv.SaveImage(blackwhite,bw)
    return blackwhite

#根据得到的数据范围将图片切割成一小块一小块的，返回的是小图片所存的文件夹
def splitimage(srcfile,rect,two=120):
    if os.path.isdir('outputdir'):
        pass
    else:
        os.mkdir('outputdir')
    directory = string.replace(str(srcfile),".jpg","")+"_tmp";
    if os.path.isdir(directory):
        pass
    else:
        os.mkdir(directory)
    
    img = cv2.imread(srcfile)
    os.chdir('outputdir');
    os.chdir(directory)
    data_width = int(0.1896*rect['width'])
    data_height = int(0.25*rect['height'])
    
    for a in range(0,4):
        y_start=rect['y']+a*data_height
        for b in range(1,5):
            x_start=rect['x']+rect['width']-(5-b)*data_width
            #已经起始坐标是x_start,y_start,长宽data_width,data_height，切割出数据区域
            #分割出的图片分别为a1_1
            filename=str(a)+"_"+str(b)
            newimg = img[y_start+5:y_start+data_height-5,x_start+40:x_start+data_width]
            #cv2.imshow("newimg",newimg)
            cv2.imwrite(filename+".tif",newimg);            
            #得到一指数据区域的图片，单个进行terract 处理
    os.chdir("../../")
    return directory
    
    
#调用tesscat对图片进行数字的识别
def outputnum(orcdir,outputdir):
    if not os.path.isdir(orcdir):
        return false
    filelist = os.listdir(orcdir)
    #把文件分为四组
    train_second = []
    train_third= []
    train_fouth = []
    train_fifth = []
    for ocrfile in filelist:
        text = ""
        prefix = string.split(ocrfile,"_")
        img = orcdir+"/"+ocrfile
        text = image_file_to_string(img)
        text = text.strip();
        text = text.strip("\n");
        if text == "":
            text = "0"
        if '0' == prefix[0] :
            train_second.append(text)
        elif '1' == prefix[0]:
            train_third.append(text)
        elif '2' == prefix[0]:
            train_fouth.append(text)
        elif '3' == prefix[0]:
            train_fifth.append(text)
    writefile(train_second,"second",outputdir)
    writefile(train_third,"third",outputdir)
    writefile(train_fouth,"fouth",outputdir)
    writefile(train_fifth,"fifth",outputdir)

def writefile(dataline,filename,outputdir):
    if os.path.isdir(outputdir):
        pass
    else:
        os.mkdir(outputdir)
    os.chdir(outputdir)
    file = open(filename,'a')
    str = "";
    for one in dataline:
        str += one+"\t";
    str += "\n";
    file.write(str);
    file.close()
    os.chdir("../")

    
#调用tesseract
def call_tesseract(input_filename, output_filename):
	"""Calls external tesseract.exe on input file (restrictions on types),
	outputting output_filename+'txt'"""
	args = [tesseract_exe_name, input_filename, output_filename]
	proc = subprocess.Popen(args)
	retcode = proc.wait()
	if retcode!=0:
		errors.check_for_errors()



#写文件，再读ocr后的内容出来
def image_file_to_string(filename, cleanup = cleanup_scratch_flag, graceful_errors=True):
    call_tesseract(filename, scratch_text_name_root)
    text = util.retrieve_text(scratch_text_name_root)
    if cleanup:
        util.perform_cleanup(scratch_image_name, scratch_text_name_root)
    return text

if __name__=="__main__":
    sample  = 'yellow.jpg'

    #选择目录，遍历图片文件
    img_tmp_dir = './source'
    imglist = get_all_pic(img_tmp_dir)

    #生成临时目录，保存切割生成的图片
    for imagefile in imglist:
        colorrect = getcolorrange(sample) #取样本的颜色空间
        rect =  getdataedge(colorrect,imagefile) #根据样本获得数据所在的有效区域
        
        blackwhitepic = blackwhite(imagefile,rect,120)  #对数据区域生成二值化图片
        #blackwhitepic = "original_meitu_1_black.jpg"
        #rect = {'y': 154, 'x': 98, 'height': 137, 'width': 506}
        print blackwhitepic,rect
        exit
        #tmp_directory = splitimage(blackwhitepic,rect)  #根据数据区域对二值化后的图进行切割
        #tmp_directory = "original_meitu_1_black_tmp";
        #outputnum(tmp_directory,"outputdir")  #根据生成的小图片tesscart，以追加的形式写

   
    
   
