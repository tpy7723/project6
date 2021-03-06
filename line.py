#-*- coding: utf-8 -*-
import cv2
import numpy as np

centerx = 320
temp = 320


                #100
def blue_img2(img, blue_threshold=150, green_threshold=150, red_threshold=150):
    threshold1 = (img[:,:,0] < blue_threshold) \
                | (img[:,:,1] < green_threshold) \
                | (img[:,:,2] < red_threshold)

    img[threshold1] = [0,0,0] # 검은색으로 바꾸기

		#100 
def blue_img(img, blue_threshold=1, green_threshold=20, red_threshold=20):
    threshold1 = (img[:,:,0] < blue_threshold) \
		| (img[:,:,1] < 0) \
                | (img[:,:,1] > green_threshold) \
		| (img[:,:,2] < 0) \
                | (img[:,:,2] > red_threshold)

    img[threshold1] = [0,0,0] # 검은색으로 바꾸기

def canny(img, low_threshold, high_threshold):
 	return cv2.Canny(img, low_threshold, high_threshold)

def region_of_interest(img, vertices, color=255):
    	mask = np.zeros_like(img) # 같은 사이즈의 빈 mask
    	cv2.fillPoly(mask, vertices, color) # vertice 만큼 검은색으로 채움
    	ROI_image = cv2.bitwise_and(img, mask) # img와mask 를 합침

	return ROI_image

def draw_fit_line(img, lines):
    	cv2.line(img, (lines[0], lines[1]), (lines[2], lines[3]), [0,0,255], 5)

def hough_lines(img, rho, theta, threshold, min_line_len, max_line_gap):
    	lines = cv2.HoughLinesP(img, rho, theta, threshold, np.array([]), minLineLength=min_line_len, maxLineGap=max_line_gap)

    	return lines

def get_fitline(img, f_lines):
    	lines = np.squeeze(f_lines)

    	if lines.ndim==1:
    		lines = lines.reshape(2,2)
    	else:
    		lines = lines.reshape(lines.shape[0]*2,2)

    	vx, vy, x, y = cv2.fitLine(lines,cv2.DIST_L2,0, 0.01, 0.01) #cv2.cv.CV_DIST_L2

   	x1, y1 = int(((img.shape[0]-1)-y)/vy*vx + x) , img.shape[0]-1
    	x2, y2 = int((430-y)/vy*vx + x) , 430
    	result = [x1,y1,x2,y2]

    	return result

def get_lane(img):
	global centerx,temp
	num = 0
	height, width = img.shape[:2]
	blue_img2(img)  # 파란색 검출
	canny_img = canny(img, 10, 30) #100 150
	#cv2.imshow("123",canny_img)
        vertices = np.array([[(0, height), (0, height*2/3+60), (width, height*2/3+60), (width, height)]], dtype=np.int32) # rectangular
	ROI_img = region_of_interest(canny_img, vertices)
	cv2.imshow("ROI", ROI_img)	# 40 50 27
	line_arr = hough_lines(ROI_img, 1, 1*np.pi/180,120,100,27) # threshold/minlength/distance
	line_arr = np.squeeze(line_arr)

	if line_arr.ndim == 2:
		slope_degree = (np.arctan2(line_arr[:,1] - line_arr[:,3], line_arr[:,0] - line_arr[:,2]) * 180) / np.pi
		L_lines, R_lines = line_arr[(slope_degree>0),:], line_arr[(slope_degree<0),:]

		L_lines = L_lines[L_lines[:,0] < 540]
		R_lines = R_lines[R_lines[:,0] > 100]
		if L_lines.shape[0]!=0:
			if R_lines.shape[0]!=0:
				L_lines = L_lines[L_lines[:,0]<320]
			print "L_lines" ,L_lines
			left_fit_line = get_fitline(img,L_lines)
			print "draw left line"
			lx1,ly1,lx2,ly2 = left_fit_line
			draw_fit_line(img, left_fit_line)

		if R_lines.shape[0]!=0:
                        if L_lines.shape[0]!=0:
                                R_lines = R_lines[R_lines[:,0]>320]
			print "R_lines", R_lines
			right_fit_line = get_fitline(img,R_lines)
			print "draw right line"
			rx1,ry1,rx2,ry2 = right_fit_line
			draw_fit_line(img, right_fit_line)

		if L_lines.shape[0]!=0 and R_lines.shape[0]==0:
			centerx= int((lx2+640)/2)
			num=1

                if L_lines.shape[0]==0 and R_lines.shape[0]!=0:
                        centerx= int((rx1+rx2)/4)
			num=1

		if L_lines.shape[0]!=0 and R_lines.shape[0]!=0:
			centerx= int((lx1+lx2+rx1+rx2)/4)
			num=2

	        if centerx>640 or centerx<0:
                	centerx = temp
	        else:
        	        temp = centerx

		cv2.circle(img,(centerx,240),3,(130,60,130),-1)  # centery = height/2 

	#print "centerx=", centerx
	centerx = str(centerx)
	num = str(num)

        if len(centerx) == 1:
        	centerx = "000"+centerx
        elif len(centerx) == 2:
        	centerx = "00"+centerx
        elif len(centerx) == 3:
        	centerx = "0"+centerx

	return img, centerx, num
