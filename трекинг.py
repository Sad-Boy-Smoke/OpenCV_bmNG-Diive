import cv2 as cv
import numpy as np
import vgamepad as vg

kernel =np.ones((5,5))
x_left = 500
y_left = 790
x_right = 500
y_right = 790

gamepad_value_left = 0
gamepad_value_right = 0

cout_for_moove = 0


kp = 1
ki = 0.15
kd = 0.3

prev_error_left = 0
integral_left = 0
prev_error_right = 0
integral_right = 0

def pid_control(error, prev_error, integral, kp, ki, kd):
    integral += error
    derivative = error - prev_error
    output = kp * error + ki * integral + kd * derivative
    return output, integral



# if cout_for_moove == 1:
#     keyDown('left') 
#     keyUp('left')
#     cout_for_moove = 0
# elif cout_for_moove == 2:
#     keyDown('right')
#     keyUp('right')
#     cout_for_moove = 0

def maskk(screen, vertex):
    mask = np.zeros_like(screen)
    cv.fillPoly(mask, vertex, 255)
    mask1 = cv.bitwise_and(screen, screen, mask=mask)
    return mask1

def dlines_left(screen_left, lines_left):
    global x_left, y_left
    try:
        for line_left in lines_left:
            cor_left = line_left[0]
            
            cv.line(screen_left, (cor_left[0],cor_left[1]), (cor_left[2], cor_left[3]), [255, 105, 0], 5)
            x_left = lines_left[0][0][0]
            y_left = lines_left[0][0][1]
    except:
        pass

def dlines_right(screen_right, lines_right):
    global x_right, y_right
    try:
        
        for line_right in lines_right:
            cor_right = line_right[0]
            cv.line(screen_right, (cor_right[0], cor_right[1]), (cor_right[2], cor_right[3]), [0, 105, 255], 5)
            x_right = lines_right[0][0][0]
            y_right = lines_right[0][0][1]

    except:
        print('2')

def nothing(x):
    pass

cv.namedWindow('Canny')
cv.namedWindow('Canny', cv.WINDOW_NORMAL)
cv.resizeWindow('Canny', 400, 300)
cv.createTrackbar("Canny_track_1", "Canny", 0,700, nothing)
cv.createTrackbar("Canny_track_2", "Canny", 0,700, nothing)

cap = cv.VideoCapture(0)
gamepad =  vg.VX360Gamepad()
while True:
    canny_threshe_1 = cv.getTrackbarPos("Canny_track_1", 'Canny')
    canny_threshe_2 = cv.getTrackbarPos("Canny_track_2", 'Canny')
    # gamepad_value_left = 0
    # gamepad_value_right = 0
    gamepad.reset() 
    d_left = 0
    d_right = 0

    #capture frame and first convert to hsv
    _, frame = cap.read()
    bil_fil = cv.bilateralFilter(frame, 13, 100, 100)
    # Convert BGR to HSV
    hsv_razmetka_white = cv.cvtColor(bil_fil, cv.COLOR_HSV2BGR)
    
    lower_white = np.array([0, 186, 219])
    upper_white = np.array([248, 245, 255])
    
    razmet_white = cv.inRange(frame, lower_white, upper_white)
    result_hsv = cv.bitwise_and(frame, frame, mask=razmet_white)
    
    # gray = cv.cvtColor(razmet_white, cv.COLOR_BGR2GRAY)    

    canny = cv.Canny(result_hsv,canny_threshe_1,canny_threshe_2, 5)
    left_vertex = np.array([[0, 327], [306, 204], [306, 490], [0, 469]])
    right_vertex = np.array([[640, 478], [642, 327], [306, 208], [310, 502]])
    # directly_vertex = np.array([[qqq, www], [eee, rrr], [ttt, yyy], [uuu, iii]])

    canny_left = maskk(canny, [left_vertex])
    canny_right = maskk(canny, [right_vertex])
    # canny_directly = maskk(canny,[directly_vertex] )

    all_mask = cv.add(canny_left,canny_right)
   
    lines_left = cv.HoughLinesP(canny_left, 1, np.pi/180, 13, 350, 13)
    lines_right = cv.HoughLinesP(canny_right, 1, np.pi/180, 13, 350, 13)
    
    dlines_left(frame, lines_left)
    dlines_right(frame, lines_right)

    cv.line(frame, (x_left, y_left), (327, 490), [255, 105, 0], 5)
    cv.line(frame, (x_right, y_right), (327, 490), [0, 105, 255], 5)

    d_left = 10000 / (np.sqrt(((x_left - 327) ** 2 + (y_left - 490) ** 2)) + 1)
    d_left = int(d_left)
    d_right = 10000 / (np.sqrt(((x_right - 327) ** 2 + (y_right - 490) ** 2)) + 1)
    d_right = int(d_right)

    if d_left >= 35:
        error_left = d_left - 30
        output_left, integral_left = pid_control(error_left, prev_error_left, integral_left, kp, ki, kd)
        prev_error_left = error_left
        gamepad_value_left = int(32767 // 17 * output_left)
        gamepad.left_joystick(x_value=gamepad_value_left, y_value=0)
        gamepad.update()

    elif d_right >= 35:
        error_right = d_right - 30
        output_right, integral_right = pid_control(error_right, prev_error_right, integral_right, kp, ki, kd)
        prev_error_right = error_right
        gamepad_value_right = int(32767 // 17 * output_right)
        gamepad.left_joystick(x_value=gamepad_value_right - 32767, y_value=0)
        gamepad.update()

    elif d_left > d_right and d_left > 35:
        error_left = d_left - 30
        output_left, integral_left = pid_control(error_left, prev_error_left, integral_left, kp, ki, kd)
        prev_error_left = error_left
        gamepad_value_left = int(32767 // 17 * output_left)
        gamepad.left_joystick(x_value=gamepad_value_left, y_value=0)
        gamepad.update()

    elif d_right > d_left and d_right > 35:
        error_right = d_right - 30
        output_right, integral_right = pid_control(error_right, prev_error_right, integral_right, kp, ki, kd)
        prev_error_right = error_right
        gamepad_value_right = int(32767 // 17 * output_right)
        gamepad.left_joystick(x_value = gamepad_value_right - 32767, y_value = 0)
        gamepad.update()
        
    cv.putText(frame, "" + str(d_left) + "", (10, 50), cv.FONT_HERSHEY_COMPLEX, 1, (255, 105, 0), 5)
    cv.putText(frame, "" + str(d_right) + "", (10, 100), cv.FONT_HERSHEY_COMPLEX, 1, (0, 105, 255), 5)

    cv.imshow('frame', frame)
    cv.imshow('canny left', canny_left)
    cv.imshow('canny right', canny_right)
    cv.imshow('rezalt', all_mask)
    cv.imshow('up_low_white', result_hsv)

    k = cv.waitKey(5) & 0xFF
    if k == 27:
        break
cv.destroyAllWindows()