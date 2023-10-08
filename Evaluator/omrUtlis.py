import cv2
import numpy as np
from imutils import contours

def getPerspective(response_sheet,min_area,max_area):
    response_sheet_gray = cv2.cvtColor(response_sheet, cv2.COLOR_BGR2GRAY)
    _, response_sheet_thresh = cv2.threshold(response_sheet_gray, 200, 255, cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
    contours, hierarchy = cv2.findContours(response_sheet_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    rects = []
    idx=0
    for cnt in contours:
        area = cv2.contourArea(cnt)
        x, y, w, h = cv2.boundingRect(cnt)
        if area > min_area and area < max_area and w>=28 and w<=32 and h>=16 and h<=20:

            if(idx%2!=0):
                rects.append((x, y, w, h))
            else:
                rects.append((x+w, y, w, h))
            idx+=1
    # print((rects))
    Width1=rects[0][0]-rects[1][0]
    Width2=rects[2][0]-rects[3][0]
    Height1=rects[0][1]-rects[2][1]
    Height2=rects[1][1]-rects[3][1]

    Width=max(Width1,Width2)
    Height=max(Height1,Height2)

    input_points=np.array([(rects[3][0],rects[3][1]),(rects[2][0],rects[2][1]),(rects[1][0],rects[1][1]),(rects[0][0],rects[0][1])], dtype=np.float32)
    converted_points=np.array([(0,0),(Width,0),(0,Height),(Width,Height)], dtype=np.float32)
    matrix=cv2.getPerspectiveTransform(input_points,converted_points)

    img_output=cv2.warpPerspective(response_sheet,matrix,(Width,Height))
    return img_output

def coOrdinates(i,j,row,col,response_sheet_thresh):
    x=row[i][0]
    y=col[j][1]
    w=col[j][2]
    h=col[j][3]
    roi=response_sheet_thresh[y:y+h,x:x+w]
    total=cv2.countNonZero(roi)

    return x,y,w,h,roi,total
def markTheRegion(ansx,ansy,answ,ansh,responseROI,color):
    center_x = ansx + (answ / 2)
    center_y = ansy + (ansh / 2)
    cv2.circle(responseROI, (int(center_x), int(center_y)), 6, (color), -1) # Draw the center point