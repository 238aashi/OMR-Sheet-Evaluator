import cv2
import numpy as np
import omrUtlis
from imutils import contours
import csv
import os

 #Defining answers
A=[0]*75
B=[1]*75
C=[2]*75
D=[3]*75
Answer_key=[A,B,C,D]

Set=0
schoolCode=""
regNo="UP2"

responseImg=cv2.imread("res_sheet (1).jpg")
scale_percent = 30  # percent of original size

# Calculate the new dimensions
width = int(responseImg.shape[1] * scale_percent / 100)
height = int(responseImg.shape[0] * scale_percent / 100)
# Resize the Image
responseImg=cv2.resize(responseImg,(width,height),interpolation = cv2.INTER_AREA)

#Get perspective
responseROI=omrUtlis.getPerspective(responseImg,400,500)

# Pre-processing
response_sheet_gray = cv2.cvtColor(responseROI, cv2.COLOR_BGR2GRAY)
response_sheet_blur=cv2.GaussianBlur(response_sheet_gray, (5, 5), 0)
_, response_sheet_thresh = cv2.threshold(response_sheet_gray, 200, 255, 
cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)

cv2.imshow("im",response_sheet_thresh)
cv2.waitKey(0)

#Get contours
contours, hierarchy = cv2.findContours(response_sheet_thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

#Extract Rectangles
idx=0
minX=100
minY=100
rects=[]
for cnt in contours:
    area = cv2.contourArea(cnt)
    x, y, w, h = cv2.boundingRect(cnt)
    roi=response_sheet_thresh[y:y+h,x:x+w]
    aspectRatio=max(h,w)/min(h,w)
    if area>120 and area<250 and aspectRatio > 1.2:

        mask=np.zeros(response_sheet_thresh.shape,dtype="uint8")
        cv2.drawContours(mask,[cnt],-1,255,-1)
        mask=cv2.bitwise_and(response_sheet_thresh,response_sheet_thresh,mask=mask)
        total=cv2.countNonZero(mask)
        limit=0.8*total # checking if max area is covered 
        if total-area>23.5:
            rects.append((x,y,w,h))
            minX=min(minX,x)
            minY=min(minY,y)
            idx+=1

# More filtering to get only the desired shape
col=[]
row=[]
for rect in rects:
    if rect[0]>=minX-2 and rect[0]<=minX+2:
        col.append(rect)
        cv2.circle(responseROI,(rect[0],rect[1]),3,(0,0,255),cv2.FILLED)
    elif rect[1]>=minY-2 and rect[1]<=minY+2:
        row.append((rect[0],rect[1]))
        cv2.circle(responseROI,(rect[0],rect[1]),3,(0,0,255),cv2.FILLED)

# Sorting row and col matrix
row.sort(key = lambda x: x[0])
col.sort(key = lambda x: x[1])

midRow=[]
for rect in rects:
    start=col[9][1]
    end=col[10][1]
    if rect[1]>start+2 and rect[1]<end-2:
        midRow.append((rect[0],rect[1]))
        cv2.circle(responseROI,(rect[0],rect[1]),3,(0,0,255),cv2.FILLED)   
midRow.sort(key = lambda x: x[0])
cv2.imshow("oi",responseROI)
cv2.waitKey(0)
#Determining the set 
x=row[13][0]
Gtotal=0
color=(0,255,255)
for i in range(0,4):
    y=col[i][1]
    w=col[i][2]
    h=col[i][3]
    roi=response_sheet_thresh[y:y+h,x:x+w]
    total=cv2.countNonZero(roi)
    if total>Gtotal:
        Set=i
        ansx=x
        ansy=y
        answ=w
        ansh=h
        Gtotal=total
color=(0,255,255)
omrUtlis.markTheRegion(ansx,ansy,answ,ansh,responseROI,color)

# Determining School code
for i in range (14,17):
    Gtotal=0
    for j in range (0,10):
        x,y,w,h,roi,total=omrUtlis.coOrdinates(i,j,row,col,response_sheet_thresh)
        if total>Gtotal:
            Gtotal=total
            ansx=x
            ansy=y
            answ=w
            ansh=h
            ch=chr(j+48)
    color=(0,255,255)
    omrUtlis.markTheRegion(ansx,ansy,answ,ansh,responseROI,color)
    schoolCode+=ch

# Determining Registration Number
for i in range (0,13):
    Gtotal=0
    color=(0,255,255)
    if i>=0 and i<=2:
        x=row[i][0]
        y=col[0][1]
        w=col[0][2]
        h=col[0][3]
        omrUtlis.markTheRegion(x,y,w,h,responseROI,color)
        continue
    
    if i>=7:
        for j in range (0,10):
            x,y,w,h,roi,total=omrUtlis.coOrdinates(i,j,row,col,response_sheet_thresh)
            if total>Gtotal:
                ansx=x
                ansy=y
                answ=w
                ansh=h
                Gtotal=total
                ch=chr(j+48)
    elif i==3:
        for j in range (0,8):
            x,y,w,h,roi,total=omrUtlis.coOrdinates(i,j,row,col,response_sheet_thresh)
            if total>Gtotal:
                ansx=x
                ansy=y
                answ=w
                ansh=h
                Gtotal=total
                ch=chr(j+51)
    elif i==4:
        for j in range (0,2):
            x,y,w,h,roi,total=omrUtlis.coOrdinates(i,j,row,col,response_sheet_thresh)
            if total>Gtotal:
                ansx=x
                ansy=y
                answ=w
                ansh=h
                Gtotal=total
                if(j==0):
                    ch='S'
                else:
                    ch='J'
    elif i==5:
        for j in range (0,2):
            x,y,w,h,roi,total=omrUtlis.coOrdinates(i,j,row,col,response_sheet_thresh)
            if total>Gtotal:
                ansx=x
                ansy=y
                answ=w
                ansh=h
                Gtotal=total
                if(j==0):
                    ch='D'
                else:
                    ch='W'
    else:
        for j in range (0,3):
            x,y,w,h,roi,total=omrUtlis.coOrdinates(i,j,row,col,response_sheet_thresh)
            if total>Gtotal:
                ansx=x
                ansy=y
                answ=w
                ansh=h
                Gtotal=total
                if(j==0):
                    ch='A'
                elif j==1:
                    ch='F'
                else:
                    ch='N'
    regNo+=ch
    omrUtlis.markTheRegion(ansx,ansy,answ,ansh,responseROI,color)

# mapping responses with the answer key

NoOfQues=75
pos1=0
pos2=0
correctAns=0
IncorrectAns=0
threshold=75
posScore=4
negScore=-1
unattemptScore=0
Left=0
ansx=0
ansy=0
answ=0
ansh=0
idx=0
response_key=[]

for idx2 in range(0,NoOfQues):
    count=0
    ans=-1
    flag=0

    if(idx2%19==0 and idx2!=0):  # calculating the correct index
        pos1+=4
        pos2+=1
        
    for idx1 in range (0,4):
        x=midRow[idx1+pos1][0]
        y=col[10+(idx2%19)][1]
        w=col[10+(idx2%19)][2]
        h=col[10+(idx2%19)][3]

        roi=response_sheet_thresh[y:y+h,x:x+w]
        total=cv2.countNonZero(roi)

        if total>threshold:
            if count==0:
                idx=idx2%19+pos2*19
                ans=idx1
                ansx=x
                ansy=y
                answ=w
                ansh=h
                count+=1
            else:
                flag=1
                color=(57,41,237)
                omrUtlis.markTheRegion(x,y,w,h,responseROI,color)

    if not(flag):
        if ans!=-1 and Answer_key[Set][idx]==ans:
            response_key.append(chr(ans+65))
            correctAns+=1
            color=(0,255,0)
            omrUtlis.markTheRegion(ansx,ansy,answ,ansh,responseROI,color)
        elif ans!=-1:
            response_key.append(chr(ans+65))
            IncorrectAns+=1
            color=(57,41,237)
            omrUtlis.markTheRegion(ansx,ansy,answ,ansh,responseROI,color)
        elif ans==-1:
            
            Left+=1
            x=midRow[pos1+Answer_key[Set][idx]][0]
            y=col[10+(idx2%19)][1]
            w=col[10+(idx2%19)][2]
            h=col[10+(idx2%19)][3]
            # print(x,y,w,h)
            response_key.append("-")
            color=(255,165,0)
            omrUtlis.markTheRegion(x,y,w,h,responseROI,color)
    else:
        response_key.append("M")
        IncorrectAns+=1
        color=(57,41,237)
        omrUtlis.markTheRegion(ansx,ansy,answ,ansh,responseROI,color)

score=correctAns*posScore+IncorrectAns*negScore+Left*unattemptScore

Set=chr(Set+65)
# def flatten_list(lst):
#     flattened = []

#     for item in lst:
#         if isinstance(item, list):
#             flattened.extend(item)
#         else:
#             flattened.append(item)
#     return flattened
# flattened_data = flatten_list([Sno,regNo,Set,response_key])
print(1,regNo,Set,schoolCode,correctAns,IncorrectAns,Left,score)
# return [Sno,regNo,Set,schoolCode,correctAns,IncorrectAns,Left,score],flattened_data, responseROI
