from selenium import webdriver
from time import sleep
from bs4 import BeautifulSoup
from selenium.webdriver.common.action_chains import ActionChains
import math

# TODO > PAUSE_TIME 으로 지연시간을 발생시켜 놓았으나 로딩이 완료되기까지 기다리도록 로직을 구현하자. 인터넷 서칭 중에 보긴 봤..
#      > 실제로 내용 자체는 특정 element 를 찾는데 n 초내에 안 나오면 exception 발생 기능인데.. Sleep 보다 더 좋을듯 싶다.
PAUSE_TIME = 2.5
PAUSE_LONG_TIME = PAUSE_TIME * 2
# TODO > 현재는 웹브라우저를 오픈하여 동작하지만 차후에는 백그라운드에서 다 돌려야한다.
#  크롬의 headless 모드를 쓰래더라.
path = 'C:/chromedriver/chromedriver.exe'
driver = webdriver.Chrome(path)

# Soundcloud 로그인 페이지 접속
url = 'https://soundcloud.com/signin'
driver.get(url)

# Allow Cookie
allowCookie = driver.find_element_by_class_name('announcement__ack')
allowCookie.click()

# TODO > 생각해보면 나중에 로그인 부분에 정보를 입력 할 수 있게 해주면 범용성을 가지게 된다.
# Login 시작.
userId = ''
password = ''

# TODO > 일반 로그인을 시도할 경우 싸클측에서 봇으로 보는듯 하다. 해결법은 싸클 API 사용이긴 한데 현재 제공하지 않는다. 따라서 페북 로그인.
#      > 차후에 API 사용이 가능해지면 일반 로그인 기능으로 돌리는 걸 고려할만하다.
#      > google Login 도 고려사항.
# 페이스북 팝업 로그인 처리.
parentPage = driver.current_window_handle

logIn = driver.find_element_by_class_name('signinInitialStep_fbButton')
logIn.click()
sleep(PAUSE_TIME)
fbLogInPage = ''
for handle in driver.window_handles:
    if handle != parentPage:
        fbLogInPage = handle

sleep(PAUSE_TIME)
driver.switch_to.window(fbLogInPage)
driver.find_element_by_xpath('//*[@id ="email"]').send_keys(userId)
driver.find_element_by_xpath('//*[@id ="pass"]').send_keys(password)
driver.find_element_by_id('loginbutton').click()

sleep(PAUSE_TIME)

# 메인 페이지로 스위치.
driver.switch_to.window(parentPage)
# 라이큳리스트 페이지로.
driver.get('https://soundcloud.com/you/likes')


# 라이큳리스트 전체곡이 노출 되도록 끝까지 스크롤.
maxHeight = driver.execute_script("return document.body.scrollHeight")

while True:
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    sleep(PAUSE_LONG_TIME)
    currentHeight = driver.execute_script("return document.body.scrollHeight")
    if currentHeight == maxHeight:
        break
    maxHeight = currentHeight

# List 의 제일 윗행 Element TOP 값은 217
driver.execute_script("window.scrollTo(document.body.scrollHeight, 217);")
sleep(PAUSE_TIME)

soup = BeautifulSoup(driver.page_source, 'html.parser')

# 라이큳리스트에서 전체 타겟 ID 추출. (aria-owns)
likedList = soup.select('div.playableTile__actions > button.sc-button-more')
# 라이큳리스트 전체 곡 갯수
countOfList = len(likedList)
sleep(PAUSE_TIME)

n = 1
for likedSong in likedList:
    btn = driver.find_element_by_xpath('//div[@class="playableTile__actions"]/button[@aria-owns="' + likedSong.get('aria-owns') + '"]')
    sleep(PAUSE_TIME)
    # More 버튼 클릭. More 버튼이 Invisible Element 라 아래와 같은 처리가 필요.
    hover = ActionChains(driver).move_to_element(btn)
    hover.perform()
    btn.click()

    # Add To PlayList 버튼 클릭.
    sleep(PAUSE_TIME)
    addBtnId = likedSong.get('aria-owns')
    btn = driver.find_element_by_xpath('//*[@id="' + addBtnId + '"]/div/div/button[4]')
    btn.click()

    # playlist 선택.
    # TODO > 일단은 플레이리스트가 하나가 이미 있다는 걸 전제로 한다. 차후에 플레이리스트 자동생성 및 해당 플레이리스트에 추가하도록 기능을 개선해야함.
    sleep(PAUSE_TIME)
    btn = driver.find_element_by_class_name('addToPlaylistButton')
    btn.click()
    sleep(PAUSE_TIME)
    btn = driver.find_element_by_class_name('modal__closeButton')
    btn.click()
    sleep(PAUSE_TIME)
    if n % 6 == 0:
        addHeightAxis = math.trunc( n / 6 )
        driver.execute_script("window.scrollTo(" + str(217 + (addHeightAxis * 257)) + ", " + str(217 + (addHeightAxis * 257)) + ");")
    n = n + 1
    sleep(PAUSE_LONG_TIME)
# 깔끔하게 꺼준다.
driver.close()