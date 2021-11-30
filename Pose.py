import cv2
import mediapipe as mp

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

webcam = cv2.VideoCapture(0)

INIT_CNT_DIFF = 30
MOVE_CONST = 0.0000015
LIFT_CONST = 0.8
LOWER_CONST = 0.05

cnt = 0
cnt_init = 0
# 움직임 측정을 위한 pose_landmarks index (코, 양어깨, 양팔꿈치, 양손목, 양골반, 양무릎, 양발목)
body_index = [0, 11, 12, 13, 14, 15, 16, 23, 24, 25, 26, 27, 28]
isFirst = False
isInit = False
prev_3_landmarks = [[], [], []]
height = 0
leg_length = 0
lift_flag = False
walk_cnt = 0

def printText(text, line=1):
  cv2.putText(image, text, (20, line * 50), cv2.FONT_HERSHEY_PLAIN, 2, (0, 0, 255), 2)

# 전신(body_index)이 온전히 보이는지 check
def isVisible(landmarks):
  for index in body_index:
    if landmarks[index].visibility < 0.5:
      return False
  return True

def dist(landmarks, a=23, b=27):
  return (landmarks[b].y - landmarks[a].y) * 10000

def isMove(landmarks, height):
  for prev in prev_3_landmarks:
    for index in body_index:
      if (abs(landmarks[index].x - prev[index].x) > height * MOVE_CONST or abs(landmarks[index].y - prev[index].y) > height * MOVE_CONST):
        return True
  return False

def isLift(landmarks):
  return True if dist(landmarks) / leg_length < LIFT_CONST else False

def isLower(landmarks):
  return True if abs(dist(landmarks) - leg_length) / leg_length < LOWER_CONST else False

while webcam.isOpened():
  cnt += 1
  success, image = webcam.read()
  if not success:
    print('error')
    continue

  # 해당 frame (capture)의 pose estimation
  image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
  image.flags.writeable = False
  results = pose.process(image)
  image.flags.writeable = True
  image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

  # TODO: 확인용. 완성 시 제거
  mp_drawing.draw_landmarks(
      image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS
  )

  try:
    # 모든 landmarks가 visible
    landmarks = results.pose_landmarks.landmark
    if isVisible(landmarks):
      visible = True
    # 하나 이상 invisible
    else:
      visible = False
  # 모든 landmarks가 invisible
  except:
    visible = False

  if visible:
    if not isFirst:
      isFirst = True
      prev_3_landmarks = [landmarks, landmarks, landmarks]
      cnt_init = cnt
      continue
    if not isInit:
      printText('Stand at attention.')
      if isMove(landmarks, dist(landmarks, 0, 27)):
        printText('Do not move', 2)
        cnt_init = cnt
      else:
        if cnt - cnt_init >= INIT_CNT_DIFF:
          height = dist(landmarks, 0, 27)
          leg_length = dist(landmarks)
          isInit = True
    else:
      if lift_flag:
        if isLower(landmarks):
          walk_cnt += 1
          lift_flag = False
      else:
        if isLift(landmarks):
          lift_flag = True
      printText('Test...')
      printText('move', 2) if isMove(landmarks, height) else printText('not move', 2)
      printText('lift', 3) if isLift(landmarks) else printText('not lift', 3)
      printText('lower', 4) if isLower(landmarks) else printText('not lower', 4)
      printText(f'walk cnt: {walk_cnt}', 5)

    prev_3_landmarks = prev_3_landmarks[1:] + [landmarks]

  else:
      printText('Show me your whole body.')

  cv2.imshow('Squid Game', image)
  if cv2.waitKey(5) & 0xFF == 27:
    break

webcam.release()