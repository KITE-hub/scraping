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
from time import sleep
from functools import cmp_to_key
import time
import random

# プロキシ情報を設定
proxy_address = "123.45.67.89:8080"  # 使用するプロキシのIPとポート
# ヘッドレスモードを有効化し、Chromeドライバーのパスを指定
chrome_options = Options()
chrome_options.add_argument("--headless")  # ヘッドレスモード
chrome_options.add_argument("--disable-gpu")
# chrome_options.add_argument('--proxy-server=http://{}'.format(proxy_address))
service = Service('D:/devdownload/chrome-win64/chromedriver-win64/chromedriver.exe')
driver = webdriver.Chrome(service=service, options=chrome_options)
# 指定した条件で単一の要素を取得し、待機を適用(タイムアウトは3秒ぐらいが限界)
def find_element_with_wait(driver, by, value, timeout=3):
  try:
    wait = WebDriverWait(driver, timeout)
    return wait.until(EC.presence_of_element_located((by, value)))
  except TimeoutException:
    # print(f"Timeout: Unable to locate element {value}")
    return None
# 指定した条件で複数要素を取得し、待機を適用(タイムアウトは3秒ぐらいが限界)
def find_elements_with_wait(driver, by, value, timeout=3):
  try:
    wait = WebDriverWait(driver, timeout)
    return wait.until(EC.presence_of_all_elements_located((by, value)))
  except TimeoutException:
    # print(f"Timeout: Unable to locate elements {value}")
    return []

# クラス定義
class faceClass:
  def __init__(face, sleepType, energy, ID, pokemonName, rarity, np, expCandy, researchExp, dreamShard):
    face.sleepType = sleepType
    face.energy = energy
    face.ID = ID
    face.pokemonName = pokemonName
    face.rarity = rarity
    face.np = np
    face.expCandy = expCandy
    face.researchExp = researchExp
    face.dreamShard = dreamShard
  def to_dict(face):
    return {
      "sleepType": face.sleepType,
      "energy": face.energy,
      "ID": face.ID,
      "pokemonName": face.pokemonName,
      "rarity": face.rarity,
      "np": face.np,
      "expCandy": face.expCandy,
      "researchExp": face.researchExp,
      "dreamShard": face.dreamShard,
    }
  @staticmethod 
  def compare(a, b):
    # 優先度: np>エナジー>寝顔ID>(ポケモン名>レア度>)
    if a.np != b.np:
      return a.np - b.np
    if a.energy != b.energy:
      return a.energy - b.energy
    if a.ID != b.ID:
      return a.ID - b.ID
    return 0  # 全てが同一の場合
class notDecidedListClass:
  def __init__(list, fieldName, pokemonName, rarity, np):
    list.fieldName = fieldName
    list.pokemonName = pokemonName
    list.rarity = rarity
    list.np = np
  def to_dict(list):
    return {
      "fieldName": list.fieldName,
      "pokemonName": list.pokemonName,
      "rarity": list.rarity,
      "np": list.np,
    }
class errorListClass:
  def __init__(list, fieldName, pokemonName, rarity):
    list.fieldName = fieldName
    list.pokemonName = pokemonName
    list.rarity = rarity
  def to_dict(list):
    return {
      "fieldName": list.fieldName,
      "pokemonName": list.pokemonName,
      "rarity": list.rarity,
    }

fieldConvert = {"ワカクサ本島": 0, "シアンの砂浜": 1, "トープ洞窟": 2, "ウノハナ雪原": 3, "ラピスラズリ湖畔": 4, "ゴールド旧発電所": 5}
faceData = [[] for _ in range(6)]
notDecidedList = []
errorList = []

url = f"https://pks.raenonx.cc/ja/pokedex/{i}"
driver.get(url) # ページを開く
# 必要な要素を取得
pokemonName = find_element_with_wait(driver, By.XPATH, "//div[@class='flex flex-col w-full gap-2 md:p-5 lg:p-8']//div[@class='truncate']")
if pokemonName:
  sleepType = find_element_with_wait(driver, By.XPATH, "//div[@class='flex flex-row items-center gap-1']")
  elements = find_elements_with_wait(driver, By.XPATH, "//div[@class='flex flex-col w-full md:w-fit']")
  if elements:
    for j, element in enumerate(elements):  # フィールドごと
      fieldName = element.find_element(By.XPATH, ".//div[@class='text-lg']").text
      element2 = element.find_elements(By.XPATH, ".//div[@class='flex flex-row place-content-center place-items-center items-center text-center gap-1.5 p-2.5']")
      for k, elem in enumerate(element2):  # レア度ごと
        rarityBase = elem.find_element(By.XPATH, ".//div[@class='flex flex-row items-center gap-0.5']")
        rarity = int(rarityBase.text.replace(",", ""))
        idBase = elem.find_element(By.XPATH, ".//small[@class='text-dimmed self-end']")
        id = int(idBase.text.replace("#", ""))  # 要確認
          
        energyBase = elem.find_element(By.XPATH, "(.//div[@class='flex flex-row place-content-center place-items-center items-center text-center gap-2']//div[@class='flex flex-row place-content-center place-items-center items-center text-center gap-1'])[1]")
        energyBase2 = energyBase.text.replace("\n", "")
        energy = energyConvert[fieldConvert[fieldName]][energyBase2]
        # npBaseの1つ目は、ランクとNPを指す、2つ目は寝顔マークとNPを指すが、未確定のときにdangerというクラスが追加される spanか？
        npBase = elem.find_element(By.XPATH, ".//div[@class='flex flex-row place-content-center place-items-center items-center text-center gap-2']//span")
        if(npBase.text=="検証中"):
          sleep(3)
          npBase = elem.find_element(By.XPATH, ".//div[@class='flex flex-row place-content-center place-items-center items-center text-center gap-2']//span")
          if(npBase.text=="検証中"): # ずっと検証中だったらエラーリストに入れる
            np = -1
            errorList.append(errorListClass(fieldName, pokemonName.text, rarity).to_dict())
          else: 
            np = int(npBase.text.replace(",", ""))
            notDecidedList.append(notDecidedListClass(fieldName, pokemonName.text, rarity, np).to_dict())
        else:
          np = int(npBase.text.replace(",", ""))
        researchExpBase = elem.find_element(By.XPATH, "(.//div[@class='flex flex-row place-content-center place-items-center items-center text-center w-full gap-1.5']//div[@class='flex flex-row place-content-center place-items-center items-center text-center w-full gap-0.5'])[1]")
        researchExp = int(researchExpBase.text.replace(",", ""))
        dreamShardBase = elem.find_element(By.XPATH, "(.//div[@class='flex flex-row place-content-center place-items-center items-center text-center w-full gap-1.5']//div[@class='flex flex-row place-content-center place-items-center items-center text-center w-full gap-0.5'])[2]")
        dreamShard = int(dreamShardBase.text.replace(",", ""))
        expCandyBase = elem.find_element(By.XPATH, "(.//div[@class='flex flex-row place-content-center place-items-center items-center text-center w-full gap-1.5']//div[@class='flex flex-row place-content-center place-items-center items-center text-center w-full gap-0.5'])[3]")
        expCandy = int(expCandyBase.text.replace(",", ""))
        faceData[fieldConvert[fieldName]].append(faceClass(sleepType.text, energy, id, pokemonName.text, rarity, np, expCandy, researchExp, dreamShard))
driver.quit()

for i in range(0,6):
  faceData[i] = sorted(faceData[i], key=cmp_to_key(faceClass.compare))
  faceData[i] = [face.to_dict() for face in faceData[i]]

with open('scraping/db/errorList.json', 'w', encoding='utf-8') as f:
  json.dump(errorList, f, indent=2, ensure_ascii=False)
with open('scraping/db/notDecidedList.json', 'w', encoding='utf-8') as f:
  json.dump(notDecidedList, f, indent=2, ensure_ascii=False)
with open('scraping/db/greengrass.json', 'w', encoding='utf-8') as f:
  json.dump(faceData[0], f, indent=2, ensure_ascii=False)
with open('scraping/db/cyan.json', 'w', encoding='utf-8') as f:
  json.dump(faceData[1], f, indent=2, ensure_ascii=False)
with open('scraping/db/taupe.json', 'w', encoding='utf-8') as f:
  json.dump(faceData[2], f, indent=2, ensure_ascii=False)
with open('scraping/db/snowdrop.json', 'w', encoding='utf-8') as f:
  json.dump(faceData[3], f, indent=2, ensure_ascii=False)
with open('scraping/db/lapis.json', 'w', encoding='utf-8') as f:
  json.dump(faceData[4], f, indent=2, ensure_ascii=False)
with open('scraping/db/gold.json', 'w', encoding='utf-8') as f:
  json.dump(faceData[5], f, indent=2, ensure_ascii=False)