from playsound import playsound
import datetime
import pyautogui

def play_start_sound():
    try:
        playsound("efan.wav")  # 🎵 시작 알림 사운드
    except Exception as e:
        print(f"알림음 재생 실패: {e}")


def sound():
    try:
        playsound("beep-03.wav")
    except Exception as audio_err:
        print(f"소리 재생 실패: {audio_err}")
        
def capture_screen_to_file():
    try:
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        screenshot_path =f"./gradio_live_capture_{timestamp}.png"

        screenshot = pyautogui.screenshot()
        screenshot.save(screenshot_path)

        print(f"화면 캡처 완료: {screenshot_path}")
        return f"화면 캡처 완료! 저장 위치: {screenshot_path}"
    except Exception as e:
        print(f"[캡처 실패] {e}")
        return f"캡처 실패: {e}"