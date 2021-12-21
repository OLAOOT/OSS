# 무궁화 꽃이 피었습니다 

## Introduction
Seoultech CS - OSS 과목의 term project로 개발했습니다.

넷플릭스 오리지널 드라마 '오징어 게임'에 등장하는 '무궁화 꽃이 피었습니다'를
[google mediapipe](https://google.github.io/mediapipe/) 의 Pose를 통한 동작 감지 기능을 구현해 만들었습니다.

## Cautions

- 구동에 웹캠이 반드시 필요합니다.
- 1인용 게임으로, 캠에 다른 인물이 비치지 않아야 합니다.
- 똑바로 선 상태에서, 캠에 머리부터 양팔, 양다리 등 전신을 찍을 수 있는 충분한 공간에서 구동해야 합니다.
- 신체 일부가 보이지 않으면 Pose가 동작하지 못하므로, 가급적 배경과 같은 색의 옷을 입거나, 측면으로 서서 신체 부위를 가리는 등의 행위를 하지 않아야 합니다.
- 게임 도중에는 반드시 제자리에서 걷거나 뛰어야 합니다. 캠에서 신체 일부가 벗어나 버리거나, 몸이 커지거나 작아져버려 수치 계산에 장애가 생길 수 있습니다.

## Description
- ESC 키로 종료, space bar로 재시작할 수 있습니다.
- 시작하면 난이도를 선택할 수 있습니다. 어려울 수록 제한 시간이 줄어들며, 키보드 숫자 키를 이용합니다.
- 캠에 전신이 보이도록 하고, 잠시 부동 자세로 대기하면 카운트다운 후 게임이 시작됩니다.
- 로봇이 '무궁화 꽃이 피었습니다' 구호를 외치고 있을 때는, 자유롭게 움직일 수 있습니다. 제자리 걸음을 하게되면 앞으로 나아갈 수 있습니다.
- 구호를 외치고 있지 않을 때는 움직일 수 없습니다. 이 시간은 특정 범위 내에서 무작위로 주어지며, 움직임이 감지되면 총성과 함께 게임이 끝납니다.
- 제한 시간 안에 결승선을 통과하면 승리, 움직일 수 없을 때 움직이거나 제한 시간이 다 되면 패배입니다.
- 얼굴이 노출되는 프로그램 특성 상 screenshot은 따로 추가하지 않았습니다.

## How it Works

![mediapipe](images/pose.png)
mediapipe Pose는 사진이나 영상의 사람을 감지하여, 각 부위를 landmark로 나타냅니다.

이를 이용해 움직일 수 있을 때, landmark 23과 27의 거리 (y좌표)가 줄어들면, 즉 왼쪽 다리를 들어 올리면 '걷는다'고 판단해 앞으로 나아갑니다.

또 움직일 수 없을 때 (로봇이 쳐다보고 있을 때), 전신의 landmark (얼굴 등은 미세한 파트는 계산하지 않고, 주요 관절만 판단)를 감지해,
이전 3개의 프레임 동안의 landmark의 위치를 저장해 두었다가 그로부터의 변동 거리를 계산합니다. 어느 landmark가 일정 거리 이상 이동했다면 움직인 것으로 판정합니다.

따라서 현재 카메라와의 거리에 따라 해당하는 계산 값의 결과가 바뀔 수 있기 때문에, 처음 전신이 캠에 보였을 때 부동자세로 키와 다리의 길이를 측정하게 됩니다.

각종 파라미터 값들은 코드에서 constant 값들을 조정해 수정할 수 있습니다.

## References

- [opencv](https://opencv.org/)
- [google mediapipe: Pose](https://google.github.io/mediapipe/solutions/pose.html)
- [codingforentrepreneurs: mediapipe Pose-Estimation tutorial](https://www.codingforentrepreneurs.com/comments/18692)
- Netflix Original 'Squid Game'

## License

- MIT