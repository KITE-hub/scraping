from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.proxy import Proxy, ProxyType
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import json
from energyConvert import energyConvert
from faceClasses import FaceClass, FaceClassNotDecided, FaceClassError
from time import sleep
from functools import cmp_to_key
from datetime import datetime, timezone, timedelta
import csv

def find_element_with_wait(driver, by, value, timeout):
  try:
    wait = WebDriverWait(driver, timeout)
    return wait.until(EC.presence_of_element_located((by, value)))
  except TimeoutException:
    return None

urlList = []
pokemonList = []

class List:
  def __init__(self, id, pokemonName, sleepType):
    self.id = id
    self.pokemonName = pokemonName
    self.sleepType = sleepType
  def to_dict(self):
    return {
      "id": self.id,
      "pokemonName": self.pokemonName,
      "sleepType": self.sleepType
    }

fieldConvert = {"ワカクサ本島": 0, "シアンの砂浜": 1, "トープ洞窟": 2, "ウノハナ雪原": 3, "ラピスラズリ湖畔": 4, "ゴールド旧発電所": 5}
sleepTypeConvert = {"うとうと": 0, "すやすや": 1, "ぐっすり": 2}
faceData = [[[] for _ in range(3)] for _ in range(6)]
faceDataNotDecided = []
faceDataError = []
legend = []
lastOmit = []

lotteryConfig = {
  "updateDate": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
  "legend": legend
}

chrome_options = Options()
# chrome_options.add_argument("--headless")  # ヘッドレスモード
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.85 Safari/537.36")
# proxy_address = "123.45.67.89:8080"  # 使用するプロキシのIP:ポート
# chrome_options.add_argument('--proxy-server=http://{}'.format(proxy_address))
service = Service('D:/Downloads/chromedriver-win64/chromedriver-win64/chromedriver.exe')
driver = webdriver.Chrome(service=service, options=chrome_options)

urlNumber = 243
url = f"https://pks.raenonx.cc/ja/pokedex/{urlNumber}"
driver.get(url) # ページを開く
# 必要な要素を取得
isGood = find_element_with_wait(driver, By.XPATH, "//*[contains(text(), 'ポケモンボックス')]", 6)
sleep(0.5)
if isGood is not None:
  isEvent = find_element_with_wait(driver, By.XPATH, "//div[@class='text-event-pokemon rounded-lg p-1 shadow-border shadow-fuchsia-700 dark:shadow-fuchsia-500']", 0)
  # print(f"pokemonName text: {pokemonName.text}")
  if isEvent is None:
    pokemonName = find_element_with_wait(driver, By.XPATH, "//div[@class='flex flex-col w-full gap-2 md:p-5 lg:p-8']//span[contains(@class, 'truncate')]", 0)
    isLegend = find_element_with_wait(driver, By.XPATH, "//div[@class='text-legendary-pokemon rounded-lg p-1 shadow-border shadow-indigo-600 dark:shadow-indigo-300']", 0)
    if isLegend is not None:
      legend.append(pokemonName.text)
    sleepTypeBefore = driver.find_element(By.XPATH, "//div[@class='flex flex-col w-full gap-y-3 md:p-5 lg:p-8']//div[@class='flex flex-col place-content-center place-items-center text-center w-full text-dimmed whitespace-nowrap p-1 text-sm md:w-32' and text()='睡眠タイプ']")
    sleepType = sleepTypeBefore.find_element(By.XPATH, "following-sibling::div[1]").text
    pokemonList.append(List(urlNumber, pokemonName.text, sleepType).to_dict())
    releaseDateBefore = driver.find_element(By.XPATH, "//div[@class='flex flex-col w-full gap-y-3 md:p-5 lg:p-8']//div[@class='flex flex-col place-content-center place-items-center text-center w-full text-dimmed whitespace-nowrap p-1 text-sm md:w-32' and text()='リリース日']")
    releaseDateBase = releaseDateBefore.find_element(By.XPATH, "following-sibling::div[1]").text
    # print(f"releaseDate: {releaseDate.text}")
    if releaseDateBase!="-":
      jst = datetime.strptime(releaseDateBase, "%Y-%m-%d %H:%M").replace(tzinfo=timezone(timedelta(hours=9)))
      utc = jst.astimezone(timezone.utc)
      releaseDate = utc.strftime("%Y-%m-%dT%H:%M:%SZ")
      elements = driver.find_elements(By.XPATH, "//div[@class='flex flex-col w-full md:w-fit']")
      for j, element in enumerate(elements):  # フィールドごと
        fieldName = element.find_element(By.XPATH, ".//div[@class='text-lg']").text
        element2 = element.find_elements(By.XPATH, ".//div[@class='flex flex-row place-content-center place-items-center text-center gap-1.5 p-2.5']")
        for k, elem in enumerate(element2):  # レア度ごと
          rarityBase = elem.find_element(By.XPATH, ".//div[@class='flex flex-row items-center gap-0.5']")
          rarity = int(rarityBase.text.replace(",", ""))
          sleepFaceName = elem.find_element(By.XPATH, ".//span[@class='truncate']").text
          # print(f"sleepFaceName: {sleepFaceName.text}")
          energyBase = elem.find_element(By.XPATH, "(.//div[@class='flex flex-row place-content-center place-items-center text-center gap-2']//div[@class='flex flex-row place-content-center place-items-center text-center gap-1'])[1]")
          energyBase2 = energyBase.text.replace("\n", "")
          energy = energyConvert[fieldConvert[fieldName]][energyBase2]
          idBase = elem.find_element(By.XPATH, ".//small[@class='text-dimmed self-end']")
          id = int(idBase.text.replace("#" , ""))
          researchExpBase = elem.find_element(By.XPATH, "(.//div[@class='flex flex-row place-content-center place-items-center text-center w-full gap-1.5']//div[@class='flex flex-row place-content-center place-items-center text-center w-full gap-0.5'])[1]")
          researchExp = int(researchExpBase.text.replace(",", ""))
          dreamShardBase = elem.find_element(By.XPATH, "(.//div[@class='flex flex-row place-content-center place-items-center text-center w-full gap-1.5']//div[@class='flex flex-row place-content-center place-items-center text-center w-full gap-0.5'])[2]")
          dreamShard = int(dreamShardBase.text.replace(",", ""))
          expCandyBase = elem.find_element(By.XPATH, "(.//div[@class='flex flex-row place-content-center place-items-center text-center w-full gap-1.5']//div[@class='flex flex-row place-content-center place-items-center text-center w-full gap-0.5'])[3]")
          expCandy = int(expCandyBase.text.replace(",", ""))
          npBase = energyBase.find_element(By.XPATH, "following-sibling::div[1]")
          npText = npBase.text
          if "text-danger" in npBase.get_attribute("class"):
            if npText == "検証中":
              sleep(3)
              npText = npBase.text
              if npText == "検証中" or npText == "-":
                np = -1
              else:
                np = int(npText.replace(",", ""))
            elif npText == "-":
              np = -1
            else:
              np = int(npText.replace(",", ""))
            if np != -1:
              newNotDecided = FaceClassNotDecided(pokemonName.text, rarity, sleepFaceName, np).to_dict()
              if newNotDecided not in faceDataNotDecided:
                faceDataNotDecided.append(newNotDecided)
            else:
              newError = FaceClassError(pokemonName.text, rarity, sleepFaceName).to_dict()
              if newError not in faceDataError:
                faceDataError.append(newError)
          else:
            np = int(npText.replace(",", ""))
          if np != -1:
            faceData[fieldConvert[fieldName]][sleepTypeConvert[sleepType]].append(FaceClass(pokemonName.text, releaseDate, rarity, sleepFaceName, energy, id, np, expCandy, researchExp, dreamShard))
  print(f"urlNumber: {urlNumber}") # 確認
driver.quit()

for i in range(0,6):
  for j in range(0,3):
    faceData[i][j] = sorted(faceData[i][j], key=cmp_to_key(FaceClass.compare))
    faceData[i][j] = [face.to_dict() for face in faceData[i][j]]

with open("pokemonList.csv", "w", newline="", encoding="utf-8") as f:
  writer = csv.DictWriter(f, fieldnames=["id", "pokemonName", "sleepType"])
  writer.writeheader()
  writer.writerows(pokemonList)

with open('./db/other/error.json', 'w', encoding='utf-8') as f:
  json.dump(faceDataError, f, indent=2, ensure_ascii=False)
with open('./db/other/notDecided.json', 'w', encoding='utf-8') as f:
  json.dump(faceDataNotDecided, f, indent=2, ensure_ascii=False)
with open('./db/other/lotteryConfig.json', 'w', encoding='utf-8') as f:
  json.dump(lotteryConfig, f, indent=2, ensure_ascii=False)

with open('./db/greengrass.json', 'w', encoding='utf-8') as f:
  json.dump(faceData[0], f, indent=2, ensure_ascii=False)
with open('./db/cyan.json', 'w', encoding='utf-8') as f:
  json.dump(faceData[1], f, indent=2, ensure_ascii=False)
with open('./db/taupe.json', 'w', encoding='utf-8') as f:
  json.dump(faceData[2], f, indent=2, ensure_ascii=False)
with open('./db/snowdrop.json', 'w', encoding='utf-8') as f:
  json.dump(faceData[3], f, indent=2, ensure_ascii=False)
with open('./db/lapis.json', 'w', encoding='utf-8') as f:
  json.dump(faceData[4], f, indent=2, ensure_ascii=False)
with open('./db/gold.json', 'w', encoding='utf-8') as f:
  json.dump(faceData[5], f, indent=2, ensure_ascii=False)