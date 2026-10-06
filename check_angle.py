import cv2

crop = cv2.imread('debug_crop.jpg')
gray = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
gray = cv2.bilateralFilter(gray, 11, 17, 17)
_, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
coords = cv2.findNonZero(thresh)
angle = cv2.minAreaRect(coords)[-1]
print('Raw angle:', angle)