import cv2
import numpy as np
from math import *
from datetime import datetime
now = datetime.now() 
current_time = now.strftime("%H:%M:%S")


cap = cv2.VideoCapture("Video 1.mp4")
ret, frame1 = cap.read()
ret, frame2 = cap.read()
#h, w, _ = frame1.shape #размер видео

#определение пользователем точек интереса
cv2.imshow("image", cv2.resize(frame1, (960, 540)))
print('Для добавления точки интереса кликните в нужном месте на изображении с камеры')
track_points = [] #точки для отслеживания места нахождения сотрудника [x, y, радиус, название, находиться ли сотрудник у станка]
def onMouse(event, x, y, flags, param):
   global posList
   if event == cv2.EVENT_LBUTTONDOWN:
        r, name = input('Введите данные о точке интереса в формате *радиус(в пикселях), название*: ').split(", ")
        track_points.append([x*2, y*2, int(r), name, False])
        print('Точка интереса добавлена, для начала отслеживания нажмите ESC')
        cv2.circle(frame1, (x*2, y*2), int(r)*2, (255, 0, 0), -1)
        cv2.putText(frame1, f'{name}, x={x}, y={y}, r={r}', (x*2, y*2), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 2)
        cv2.imshow("image", cv2.resize(frame1, (960, 540)))
cv2.setMouseCallback("image", onMouse)
cv2.waitKey(0)
cv2.destroyAllWindows()
print('Отслеживание запущено')
    
oldContours = []
while cap.isOpened(): # метод isOpened() выводит статус видеопотока
    alldiff = cv2.absdiff(frame1, frame2) # нахождение разницы двух кадров, которая проявляется лишь при изменении одного из них, т.е. с этого момента наша программа реагирует на любое движение.
    diff = alldiff#[200: 576, 300: 928] #область для отслеживания  
    area1 = frame1#[200: 576, 300: 928]

    gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY) # перевод кадров в черно-белую градацию
    
    blur = cv2.GaussianBlur(gray, (61, 61), 0) # фильтрация лишних контуров

    _, thresh = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY) # метод для выделения кромки объекта белым цветом
    kernel = np.ones((20, 20), 'uint8')
    dilated = cv2.dilate(thresh, kernel, iterations = 3) # данный метод противоположен методу erosion(), т.е. эрозии объекта, и расширяет выделенную на предыдущем этапе область
 
    contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE) # нахождение массива контурных точек
    
    detections = []
    if len(contours)>0: #проверка найдены ли контуры
        oldContours=contours
    else:
        contours = oldContours
    for contour in contours:
        (x, y, w, h) = cv2.boundingRect(contour) # преобразование массива из предыдущего этапа в кортеж из четырех координат
        if cv2.contourArea(contour)<9000: # условие по площади объекта
            continue
        detections.append([x, y, w, h])

    if(len(detections)>0): #проверка на не нулевой массив найденых контуров на данном кадре
        for x, y, w, h in detections:
            cv2.rectangle(area1, (x, y), (x + w, y + h), (0, 255, 0), 3) #отрисовка прямоугольника x y w h 
            #нахождение центра прямоугольника
            centrex = (x +x + w) // 2
            centrey = (y +y + h) // 2
            for point in track_points: #проверка вхождения контура в точки интереса
                point_x = point[0]
                point_y = point[1]
                point_r = point[2]
                if sqrt((centrex-point_x)**2 + (centrey-point_y)**2) <= point_r and point[4]==False:
                    for point_a in track_points:
                        point_a[4] = False
                    point[4] = True;
                    now = datetime.now() 
                    current_time = now.strftime("%H:%M:%S")
                    print(f'Сотрудник подошёл к точке {point[3]} в {current_time}')
                    break

    cv2.imshow("thresh", cv2.resize(dilated, (960, 540)))
    cv2.imshow("frame2", frame1)

    frame1 = frame2  
    ret, frame2 = cap.read() 

    if cv2.waitKey(40) == 27:
        break
    
cap.release()
cv2.destroyAllWindows()




