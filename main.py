import cv2
import mediapipe as mp
import random
import time
import winsound

mp_drawing = mp.solutions.drawing_utils
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

webcam = cv2.VideoCapture(0)

img_webcam_required = cv2.imread('images/webcam_required.png')
img_start = cv2.imread('images/start.png')
img_countdown = cv2.imread('images/countdown.png')
img_timer = cv2.imread('images/timer.png')
img_set_difficulty = cv2.imread('images/set_difficulty.png')
img_easy = cv2.imread('images/easy.png')
img_normal = cv2.imread('images/normal.png')
img_hard = cv2.imread('images/hard.png')
img_info_empty = cv2.imread('images/info_empty.png')
img_info1 = cv2.imread('images/info1.png')
img_info2 = cv2.imread('images/info2.png')
img_info3 = cv2.imread('images/info3.png')
img_info4 = cv2.imread('images/info4.png')
img_info5 = cv2.imread('images/info5.png')
img_info6 = cv2.imread('images/info6.png')
img_canmove = cv2.imread('images/canmove.png')
img_cantmove = cv2.imread('images/cantmove.png')

game_window = img_start
info_window = img_info1
timer_window = img_set_difficulty

# 초기화 시 부동자세 시간
INIT_CNT_DIFF = 30
# 움직임 판정 coef (작을 수록 엄격)
MOVE_CONST = 0.000003
# 다리 lift 판정 coef
LIFT_CONST = 0.8
# 무궁화 음성 시간
CAN_MOVE_TIME = 30
# 얼음 시간 (난수)
CANT_MOVE_TIME_MIN = 25
CANT_MOVE_TIME_MAX = 50
# 난이도별 추가 시간
DIFFICULTY_TIME = 40

# 결승점까지 걸음 수
WIN_WALK_CNT = 55

# 난이도 (-1: not selected, 0: hard, 1: normal, 2: easy)
difficulty = -1
# 제한시간 (hard 기준. 실제 계산 시 time_limit + abs(difficulty) * DIFFICULTY_TIME)
time_limit = 80
# 시간 카운트 위한 prev time
prev_time = 0
# 시간 카운트
cnt = 0
# 카운트 계산용 변수
checkpoint = 0
# 움직임 측정을 위한 pose_landmarks index (코, 양어깨, 양팔꿈치, 양손목, 양골반, 양무릎, 양발목)
body_index = [0, 11, 12, 13, 14, 15, 16, 23, 24, 25, 26, 27, 28]
# 초기화
isFirst = False
isInit = False
isStart = False
# 움직이고 있지 않은지 측정을 위한 이전 3 프레임동안의 랜드마크
prev_3_landmarks = [[], [], []]
# 키
height = 0
# 다리 길이
leg_length = 0
# 다리 들었을 때의 flag
lift_flag = False
walk_cnt = 0
# 무궁화 음성 나오고 있을 때 true
canMove = True
# 상태 변경 flag
moveFlag = True
# 무궁화 상태 시작시간
state_cnt = 0
# 무궁화 음성 시간
canMoveTime = CAN_MOVE_TIME
# 못움직이는 시간
cantMoveTime = 0

win = False
isGameOver = False

def printTimer():
  time = (time_limit + abs(difficulty) * DIFFICULTY_TIME) - (cnt - checkpoint) // 10
  cv2.putText(timer_window, f'0{time // 60}:{0 if time % 60 < 10 else ""}{time % 60}', (50, 145), cv2.FONT_HERSHEY_PLAIN, 5, (0, 0, 255), 2)

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

while webcam.isOpened():
  success, cam = webcam.read()
  if not success:
    print('error')
    continue

  # 해당 frame (capture)의 pose estimation
  cam = cv2.cvtColor(cam, cv2.COLOR_BGR2RGB)
  cam.flags.writeable = False
  results = pose.process(cam)
  cam.flags.writeable = True
  cam = cv2.cvtColor(cam, cv2.COLOR_RGB2BGR)

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
    # 초기화
    timer_window = cv2.imread('images/timer.png')
    if time.time() - prev_time >= 0.1:
      cnt += 1
      prev_time = time.time()
    prev_3_landmarks = prev_3_landmarks[1:] + [landmarks]
    if not isFirst:
      isFirst = True
      prev_3_landmarks = [landmarks] * 3
      game_window = img_countdown

    if not isInit:
      info_window = img_info2
      if isMove(landmarks, dist(landmarks, 0, 27)):
        info_window = img_info3
        checkpoint = cnt
      else:
        if cnt - checkpoint >= INIT_CNT_DIFF:
          height = dist(landmarks, 0, 27)
          leg_length = dist(landmarks)
          isInit = True
          checkpoint = cnt
    # 카운트다운
    if isInit and not isStart and not isGameOver:
      info_window = img_info4
      cv2.putText(timer_window, f'{(29 - (cnt - checkpoint)) // 10 + 1}', (135, 145),
                  cv2.FONT_HERSHEY_PLAIN, 5, (0, 0, 255), 2)

      if (29 - (cnt - checkpoint)) == 0:
        checkpoint = cnt
        isStart = True

    # 게임종료
    if isGameOver:
      if win:
        info_window = img_info6
      else:
        info_window = img_info5

    # 게임시작
    if isStart:
      printTimer()
      info_window = img_info_empty

      # timeout
      if (time_limit + abs(difficulty) * DIFFICULTY_TIME) - (cnt - checkpoint) // 10 == 0:
        isGameOver = True
        isStart = False
        winsound.PlaySound('sounds\\gun.wav', winsound.SND_ASYNC)

      if canMove:
        # 무궁화 시작
        if moveFlag:
          state_cnt = cnt
          winsound.PlaySound('sounds\\voice.wav', winsound.SND_ASYNC)
          moveFlag = False
          game_window = img_canmove
        else:
          # 무궁화 끝
          if cnt - state_cnt == canMoveTime:
            canMove = False
            moveFlag = True
          # 무궁화 중
          else:
            if lift_flag:
              if not isLift(landmarks):
                walk_cnt += 1
                img_canmove = img_canmove[6:-6, 8:-8].copy()
                img_cantmove = img_cantmove[6:-6, 8:-8].copy()
                game_window = img_canmove
                lift_flag = False
            else:
              if isLift(landmarks):
                lift_flag = True
            if walk_cnt >= WIN_WALK_CNT:
              win = True
              isGameOver = True
              isStart = False

      else:
        # 얼음 시작
        if moveFlag:
          state_cnt = cnt
          cantMoveTime = random.randrange(CANT_MOVE_TIME_MIN, CANT_MOVE_TIME_MAX)
          moveFlag = False
          game_window = img_cantmove
        else:
          # 얼음 끝
          if cnt - state_cnt == cantMoveTime:
            canMove = True
            moveFlag = True
          # 얼음 중
          else:
            if isMove(landmarks, dist(landmarks, 0, 27)):
              isGameOver = True
              isStart = False
              winsound.PlaySound('sounds\\gun.wav', winsound.SND_ASYNC)

  elif not isGameOver:
    info_window = img_info1

  # 렌더링
  info = cv2.vconcat([info_window, timer_window, cv2.resize(cam, (320, 240))])
  window = cv2.hconcat([cv2.resize(game_window, (960, 720)), info])

  cv2.namedWindow('Squid Game', cv2.WINDOW_KEEPRATIO)
  cv2.imshow('Squid Game', window)

  # keyboard event
  key = cv2.waitKey(33) & 0xFF
  # 재시작
  if key == 32:
    img_canmove = cv2.imread('images/canmove.png')
    img_cantmove = cv2.imread('images/cantmove.png')
    game_window = img_start
    info_window = img_info1
    timer_window = img_set_difficulty
    difficulty = -1
    prev_time = 0
    cnt = 0
    checkpoint = 0
    isFirst = False
    isInit = False
    isStart = False
    prev_3_landmarks = [[], [], []]
    height = 0
    leg_length = 0
    lift_flag = False
    walk_cnt = 0
    canMove = True
    moveFlag = True
    state_cnt = 0
    # 못움직이는 시간
    cantMoveTime = 0
    win = False
    isGameOver = False
  # 종료
  elif key == 27:
    break
  #난이도 선택
  elif difficulty == -1 and not isFirst:
    if key == 49:
      difficulty = 2
      timer_window = img_easy
    elif key == 50:
      difficulty = 1
      timer_window = img_normal
    elif key == 51:
      difficulty = 0
      timer_window = img_hard

if not webcam.isOpened():
  while not webcam.isOpened():
    cv2.imshow('Squid Game', img_webcam_required)
    if cv2.waitKey(5) & 0xFF == 27:
      break

cv2.destroyAllWindows()
webcam.release()
